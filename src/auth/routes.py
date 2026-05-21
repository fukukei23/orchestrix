"""認証APIルート"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from pydantic import BaseModel, EmailStr
from typing import Optional

from ..api.dependencies import get_db
from ..database.models import User
from .jwt_handler import verify_password, get_password_hash, create_access_token
from .dependencies import get_current_user


router = APIRouter()


class LoginRequest(BaseModel):
    """ログインリクエストモデル"""
    username: str
    password: str


class LoginResponse(BaseModel):
    """ログインレスポンスモデル"""
    access_token: str
    token_type: str = "bearer"
    user_id: str
    username: str


class UserCreate(BaseModel):
    """ユーザー作成リクエストモデル"""
    username: str
    password: str
    email: str


@router.post("/login", response_model=LoginResponse, status_code=status.HTTP_200_OK)
async def login(
    credentials: LoginRequest,
    db: Session = Depends(get_db)
):
    """
    ユーザーログイン

    Args:
        credentials: ユーザー名とパスワード
        db: データベースセッション

    Returns:
        アクセストークンを含むレスポンス
    """
    user = db.query(User).filter(User.username == credentials.username).first()

    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password"
        )

    if not verify_password(credentials.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password"
        )

    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="User account is inactive"
        )

    access_token = create_access_token(data={"sub": str(user.id)})

    return LoginResponse(
        access_token=access_token,
        user_id=str(user.id),
        username=user.username
    )


@router.post("/register", response_model=dict, status_code=status.HTTP_201_CREATED)
async def register(
    user_data: UserCreate,
    db: Session = Depends(get_db)
):
    """
    新規ユーザーを登録する

    Args:
        user_data: ユーザー情報
        db: データベースセッション

    Returns:
        作成結果
    """
    # ユーザー名が既に存在するか確認
    existing_user = db.query(User).filter(User.username == user_data.username).first()
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Username already registered"
        )

    # 新規ユーザー作成
    new_user = User(
        username=user_data.username,
        email=user_data.email,
        hashed_password=get_password_hash(user_data.password),
        is_active=True
    )

    db.add(new_user)
    db.commit()
    db.refresh(new_user)

    return {
        "id": new_user.id,
        "username": new_user.username,
        "email": new_user.email,
        "message": "User created successfully"
    }


@router.get("/me", status_code=status.HTTP_200_OK)
async def get_current_user_info(current_user: User = Depends(get_current_user)):
    """
    現在のユーザー情報を取得する

    Args:
        current_user: 現在のユーザー（認証済み）

    Returns:
        ユーザー情報
    """
    return {
        "id": current_user.id,
        "username": current_user.username,
        "email": current_user.email,
        "is_active": current_user.is_active,
        "created_at": current_user.created_at.isoformat() if current_user.created_at else None
    }


@router.post("/logout", status_code=status.HTTP_200_OK)
async def logout():
    """
    ログアウト（クライアント側でトークンを削除）

    Returns:
        ログアウト結果
    """
    # 実装: クライアント側でトークンを削除する必要がある
    return {
        "message": "Logout successful. Please remove token from client"
    }
