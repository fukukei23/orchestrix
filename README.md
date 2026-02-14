# Orchestrix - AI Agent Orchestration Matrix

## 概要
Orchestrixは、複数のAIエージェントを統括し、24時間自動実行可能なオーケストレーションシステムです。

## セットアップ

### 1. Python環境のセットアップ
```bash
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

### 2. Dockerコンテナの起動
```bash
docker-compose up -d
```

### 3. データベースの初期化
```bash
# Alembicの初期化（まだの場合）
alembic init alembic

# マイグレーションの作成と適用
alembic revision --autogenerate -m "Initial migration"
alembic upgrade head
```

### 4. 環境変数の設定
`.env`ファイルにAPIキーを設定してください。

## テストの実行
```bash
pytest tests/unit/
```

## 次のステップ
Phase 1のコアモジュールを実装します。
