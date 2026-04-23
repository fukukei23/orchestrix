"""データベース初期化スクリプト"""
import os
import sys
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base

from src.database.models import Base
from dotenv import load_dotenv

load_dotenv()


def get_db_engine():
    """データベースエンジンを取得する"""
    from src.database.connection import get_db_engine
    return get_db_engine()


def init_database():
    """データベースの全テーブルを作成する"""
    print("Creating all database tables...")

    try:
        engine = get_db_engine()

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
