"""
FastAPI依存関係モジュール
"""
from typing import Generator
from sqlalchemy.orm import Session
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials


security = HTTPBearer()


def get_db() -> Generator[Session, None, None]:
    """
    データベースセッションを取得

    Yields:
        Database session
    """
    from ..database.connection import SessionLocal
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security)):
    """
    認証ユーザーを取得

    Args:
        credentials: HTTP認証情報

    Returns:
        ユーザー情報（簡易実装）
    """
    # TODO: JWT検証を実装
    return {"user_id": "demo_user", "authenticated": True}
