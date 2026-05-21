"""
タスクスケジューラーモジュール
Celery Beatを使って定期実行を管理します。
"""

from typing import Dict, List, Optional
from datetime import datetime, timedelta
from celery import Celery
from celery.schedules import crontab
import logging
import croniter


class TaskScheduler:
    """タスクスケジューラー"""

    def __init__(self,
                 celery_app: Celery,
                 broker_url: str,
                 result_backend: str = None):
        """
        初期化

        Args:
            celery_app: Celeryアプリインスタンス
            broker_url: RedisブローカーURL
            result_backend: 結果保存場所（オプション）
        """
        self.app = celery_app
        self.app.conf.broker_url = broker_url
        self.app.conf.result_backend = result_backend or broker_url
        self.app.conf.task_serializer = 'json'
        self.app.conf.result_serializer = 'json'
        self.app.conf.accept_content = ['json']
        self.app.conf.result_expires = 3600  # 1時間
        self.app.conf.timezone = 'Asia/Tokyo'

        self.logger = logging.getLogger(__name__)

    def schedule_task(self,
                    task_name: str,
                    cron_expression: str,
                    task_id: str,
                    task_args: Dict = None,
                    enabled: bool = True) -> bool:
        """
        タスクをスケジュール

        Args:
            task_name: タスク名（登録されたCeleryタスク）
            cron_expression: cron式（例: "0 9 * * *"）
            task_id: 一意のタスクID
            task_args: タスク引数
            enabled: 有効/無効

        Returns:
            成功したかどうか
        """
        if task_args is None:
            task_args = {}

        try:
            # cron式をパース
            cron = self._parse_cron_expression(cron_expression)

            if enabled:
                # Celeryのschedule登録
                self.app.conf.beat_schedule = {
                    f'schedule-{task_id}': {
                        'task': task_name,
                        'schedule': cron,
                        'args': [task_args],
                        'options': {
                            'expires': 3600
                        }
                    }
                }
                self.logger.info(
                    f"Scheduled task '{task_name}' (ID: {task_id}) "
                    f"with cron: {cron_expression}"
                )
            else:
                # スケジュールから削除
                if f'schedule-{task_id}' in self.app.conf.beat_schedule:
                    del self.app.conf.beat_schedule[f'schedule-{task_id}']
                self.logger.info(f"Unscheduled task {task_id}")

            return True

        except Exception as e:
            self.logger.error(f"Failed to schedule task: {e}")
            return False

    def _parse_cron_expression(self, cron_expr: str) -> crontab:
        """
        cron式をパース

        Args:
            cron_expr: cron式（例: "0 9 * * *"）

        Returns:
            Celeryのcrontabオブジェクト
        """
        parts = cron_expr.split()
        if len(parts) != 5:
            raise ValueError(f"Invalid cron expression: {cron_expr}")

        minute, hour, day_of_month, month_of_year, day_of_week = parts

        return crontab(
            minute=minute,
            hour=hour,
            day_of_month=day_of_month,
            month_of_year=month_of_year,
            day_of_week=day_of_week
        )

    def schedule_natural_language(self,
                             description: str,
                             task_name: str,
                             task_id: str,
                             task_args: Dict = None) -> Dict:
        """
        自然言語からスケジュールを解析して設定

        Args:
            description: 自然言語の説明（例: "毎日朝9時に実行"）
            task_name: タスク名
            task_id: タスクID
            task_args: タスク引数

        Returns:
            スケジュール設定結果
        """
        if task_args is None:
            task_args = {}

        # 自然言語をcron式に変換
        cron_expression = self._natural_to_cron(description)

        result = {
            'natural_language': description,
            'cron_expression': cron_expression,
            'parsed': False,
            'error': None
        }

        try:
            success = self.schedule_task(
                task_name=task_name,
                cron_expression=cron_expression,
                task_id=task_id,
                task_args=task_args
            )
            result['parsed'] = success
            result['scheduled_at'] = datetime.now().isoformat()
        except Exception as e:
            result['error'] = str(e)

        return result

    def _natural_to_cron(self, description: str) -> str:
        """
        自然言語をcron式に変換

        Args:
            description: 自然言語の説明

        Returns:
            cron式
        """
        desc_lower = description.lower()

        # 簡単なパターンマッチ
        patterns = {
            # 毎日
            r'毎日\s*(\d{1,2})時': lambda m: f"0 {m.group(1)} * * *",
            r'毎朝\s*(\d{1,2})時': lambda m: f"0 {m.group(1)} * * *",
            r'毎晩\s*(\d{1,2})時': lambda m: f"0 {m.group(1)} * * *",

            # 毎週
            r'毎週.*月曜.*(\d{1,2})時': lambda m: f"0 {m.group(1)} * * 1",
            r'毎週.*火曜.*(\d{1,2})時': lambda m: f"0 {m.group(1)} * * 2",
            r'毎週.*水曜.*(\d{1,2})時': lambda m: f"0 {m.group(1)} * * 3",
            r'毎週.*木曜.*(\d{1,2})時': lambda m: f"0 {m.group(1)} * * 4",
            r'毎週.*金曜.*(\d{1,2})時': lambda m: f"0 {m.group(1)} * * 5",

            # 毎時
            r'毎時': lambda m: "0 * * * *",

            # 毎月
            r'毎月\s*1日\s*(\d{1,2})時': lambda m: f"0 {m.group(1)} 1 * *",

            # 特定の間隔
            r'(\d+)\s*分毎': lambda m: f"*/{m.group(1)} * * * *",
            r'(\d+)\s*時間毎': lambda m: f"0 */{m.group(1)} * * *",
        }

        for pattern, converter in patterns.items():
            import re
            match = re.search(pattern, desc_lower)
            if match:
                return converter(match)

        # デフォルト：毎日9時
        self.logger.warning(
            f"Could not parse natural language: {description}, "
            "using default: daily at 9am"
        )
        return "0 9 * * *"

    def get_next_run_time(self, task_id: str) -> Optional[datetime]:
        """
        次回の実行時間を取得

        Args:
            task_id: タスクID

        Returns:
            次回の実行時間
        """
        schedule_key = f'schedule-{task_id}'
        if schedule_key not in self.app.conf.beat_schedule:
            self.logger.warning(f"Task {task_id} not found in schedule")
            return None

        schedule_info = self.app.conf.beat_schedule[schedule_key]
        cron_expr = schedule_info['schedule']

        # 次回の実行時間を計算
        now = datetime.now()
        try:
            # croniterを使って次回の実行時間を計算
            cron_str = self._croniter_to_cronstring(cron_expr)
            cron = croniter.croniter(cron_str, now)
            next_run = next(cron)
            return next_run
        except Exception as e:
            self.logger.error(f"Failed to calculate next run time: {e}")
            return None

    def _croniter_to_cronstring(self, crontab_obj) -> str:
        """Celeryのcrontabをcroniter用の文字列に変換"""
        # 簡易的な実装（詳細なマッピングが必要）
        parts = [
            crontab_obj._orig_minute if crontab_obj._orig_minute != '*' else '*',
            crontab_obj._orig_hour if crontab_obj._orig_hour != '*' else '*',
            crontab_obj._orig_day_of_month if crontab_obj._orig_day_of_month != '*' else '*',
            crontab_obj._orig_month_of_year if crontab_obj._orig_month_of_year != '*' else '*',
            crontab_obj._orig_day_of_week if crontab_obj._orig_day_of_week != '*' else '*'
        ]
        return ' '.join(parts)

    def list_scheduled_tasks(self) -> List[Dict]:
        """
        スケジュールされたタスクを一覧

        Returns:
            タスク情報のリスト
        """
        tasks = []

        for key, schedule_info in self.app.conf.beat_schedule.items():
            if key.startswith('schedule-'):
                task_id = key.replace('schedule-', '')
                cron_expr = schedule_info['schedule']
                next_run = self.get_next_run_time(task_id)

                tasks.append({
                    'task_id': task_id,
                    'task_name': schedule_info['task'],
                    'cron_expression': self._croniter_to_cronstring(cron_expr),
                    'next_run': next_run.isoformat() if next_run else None,
                    'enabled': True
                })

        return tasks

    def unschedule_task(self, task_id: str) -> bool:
        """
        タスクのスケジュールを解除

        Args:
            task_id: タスクID

        Returns:
            成功したかどうか
        """
        schedule_key = f'schedule-{task_id}'

        if schedule_key in self.app.conf.beat_schedule:
            del self.app.conf.beat_schedule[schedule_key]
            self.logger.info(f"Unscheduled task {task_id}")
            return True

        self.logger.warning(f"Task {task_id} not found in schedule")
        return False

    def validate_cron_expression(self, cron_expr: str) -> Dict:
        """
        cron式をバリデーション

        Args:
            cron_expr: cron式

        Returns:
            バリデーション結果
        """
        result = {
            'valid': False,
            'error': None,
            'next_runs': []
        }

        try:
            parts = cron_expr.split()
            if len(parts) != 5:
                result['error'] = f"Invalid format: expected 5 parts, got {len(parts)}"
                return result

            minute, hour, day, month, weekday = parts

            # 各パートのバリデーション
            if not self._validate_cron_part(minute, 0, 59):
                result['error'] = f"Invalid minute: {minute}"
                return result
            if not self._validate_cron_part(hour, 0, 23):
                result['error'] = f"Invalid hour: {hour}"
                return result
            if not self._validate_cron_part(day, 1, 31):
                result['error'] = f"Invalid day: {day}"
                return result
            if not self._validate_cron_part(month, 1, 12):
                result['error'] = f"Invalid month: {month}"
                return result
            if not self._validate_cron_part(weekday, 0, 6):
                result['error'] = f"Invalid weekday: {weekday}"
                return result

            result['valid'] = True

            # 次回の実行時間を計算（最大5回）
            cron = croniter.croniter(cron_expr, datetime.now())
            for _ in range(5):
                try:
                    next_run = next(cron)
                    result['next_runs'].append(next_run.isoformat())
                except StopIteration:
                    break

        except Exception as e:
            result['error'] = str(e)

        return result

    def _validate_cron_part(self, part: str, min_val: int, max_val: int) -> bool:
        """cronパートのバリデーション"""
        if part == '*':
            return True

        # カンマ区切りのリスト
        if ',' in part:
            values = part.split(',')
            for v in values:
                if '-' in v:
                    # レンジ（例: 1-5）
                    start, end = v.split('-')
                    if not (start.isdigit() and end.isdigit()):
                        return False
                    if not (min_val <= int(start) <= max_val and min_val <= int(end) <= max_val):
                        return False
                elif '/' in v:
                    # 間隔（例: */5）
                    base, interval = v.split('/')
                    if not base.isdigit() or not interval.isdigit():
                        return False
                elif not v.isdigit():
                    return False
            return True

        # シンプルな値
        if '-' in part:
            start, end = part.split('-')
            return (start.isdigit() and end.isdigit() and
                    min_val <= int(start) <= max_val and
                    min_val <= int(end) <= max_val)

        if '/' in part:
            base, interval = part.split('/')
            return (base in ['*'] and interval.isdigit() and
                    min_val <= int(interval) <= max_val)

        return part.isdigit() and min_val <= int(part) <= max_val
