"""認証用依存関係"""
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session
from typing import Annotated

from .jwt_handler import decode_access_token
from ..api.dependencies import get_db
from ..database.models import User
import jwt


# Bearerトークンの設定
oauth2_scheme = HTTPBearer()


async def get_current_user(
    token: Annotated[str, Depends(oauth2_scheme)],
    db: Session = Depends(get_db)
):
    """
    現在のユーザーを取得する

    Args:
        token: JWTトークン
        db: データベースセッション

    Returns:
        Userオブジェクト

    Raises:
        HTTPException: 認証エラー
    """
    credentials_exception = HTTPException(
        status_code=status.HTTP_403_FORBIDDEN,
        detail="Could not validate credentials"
    )

    try:
        payload = decode_access_token(token)
        user_id = payload.get("sub")

        if user_id is None:
            raise credentials_exception

        user = db.query(User).filter(User.id == user_id).first()

        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found"
            )

        return user

    except jwt.ExpiredSignatureError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token has expired"
        )
    except jwt.InvalidTokenError:
        raise credentials_exception
