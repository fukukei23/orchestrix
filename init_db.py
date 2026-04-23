"""データベース初期化スクリプト（Alembicを使用）"""
import os
import sys
from sqlalchemy import create_engine, text
from sqlalchemy.ext.declarative import declarative_base

# プロジェクトルートをPYTHONPATHに追加
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from dotenv import load_dotenv

from src.database.models import Base
from src.database.connection import get_engine

load_dotenv()


def init_database():
    """データベースの全テーブルを作成する"""
    print("Creating all database tables...")

    try:
        engine = get_engine()

        # 全テーブルを作成
        Base.metadata.create_all(bind=engine)

        print("✅ Database tables created successfully!")
        print("📊 Created tables:")
        print("  - tasks")
        print("  - task_dependencies")
        print("  - executions")
        print("  - logs")
        print("  - agent_configs")
        print("  - users")
        print()
        return {
            'success': True,
            'message': 'Database initialized successfully'
        }

    except Exception as e:
        print(f"❌ Database initialization failed: {e}")
        print()
        return {
            'success': False,
            'error': str(e)
        }


if __name__ == "__main__":
    init_database()
