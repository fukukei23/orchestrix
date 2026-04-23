"""JWT認証ハンドラー"""
import os
from datetime import datetime, timedelta
from typing import Dict, Any, Optional
import jwt
from passlib.context import CryptContext
from dotenv import load_dotenv

load_dotenv()

SECRET_KEY = os.getenv('SECRET_KEY', 'your-secret-key-change-this-in-production')
ALGORITHM = os.getenv('ALGORITHM', 'HS256')
ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv('ACCESS_TOKEN_EXPIRE_MINUTES', '30'))

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """
    パスワードを検証する

    Args:
        plain_password: プレインテキストのパスワード
        hashed_password: ハッシュされたパスワード

    Returns:
        検証結果
    """
    return pwd_context.verify(plain_password, hashed_password)


def get_password_hash(password: str) -> str:
    """
    パスワードをハッシュ化する

    Args:
        password: プレインテキストのパスワード

    Returns:
        ハッシュされたパスワード
    """
    return pwd_context.hash(password)


def create_access_token(data: Dict[str, Any]) -> str:
    """
    アクセストークンを作成する

    Args:
        data: トークンに含めるデータ（通常: user_id, username）

    Returns:
        JWTトークン
    """
    to_encode = data.copy()

    # 有効期限を追加
    expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})

    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)

    return encoded_jwt


def decode_access_token(token: str) -> Dict[str, Any]:
    """
    アクセストークンをデコードする

    Args:
        token: JWTトークン

    Returns:
        デコードされたデータ

    Raises:
        jwt.ExpiredSignatureError: トークンの有効期限切れ
        jwt.InvalidTokenError: 無効なトークン
    """
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        return payload
    except jwt.ExpiredSignatureError:
        raise jwt.ExpiredSignatureError("Token has expired")
    except jwt.InvalidTokenError:
        raise jwt.InvalidTokenError("Invalid token")
