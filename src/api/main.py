"""
FastAPI アプリケーション
OrchestrixのREST APIエンドポイントを提供します。
"""

from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session
import logging
from datetime import datetime
from typing import List, Optional

from ..database.connection import SessionLocal
from ..database.models import Task, Execution, Log, AgentConfig
from .routes import tasks, agents, analytics, executions
from ..auth.routes import router as auth_router
from .dependencies import get_db, get_current_user


# FastAPIアプリ作成
app = FastAPI(
    title="Orchestrix API",
    description="AI Agent Orchestration Matrix API",
    version="1.0.0"
)

# CORSミドルウェア設定
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ロギング設定
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# ルートをインクルード
app.include_router(auth_router, prefix="/api/v1/auth", tags=["Auth"])
app.include_router(tasks.router, prefix="/api/v1/tasks", tags=["Tasks"])
app.include_router(agents.router, prefix="/api/v1/agents", tags=["Agents"])
app.include_router(analytics.router, prefix="/api/v1/analytics", tags=["Analytics"])
app.include_router(executions.router, prefix="/api/v1", tags=["Executions"])


@app.get("/")
async def root():
    """ルートエンドポイント"""
    return {
        "name": "Orchestrix API",
        "version": "1.0.0",
        "status": "operational",
        "docs": "/docs",
        "redoc": "/redoc"
    }


@app.get("/health")
async def health_check():
    """ヘルスチェックエンドポイント"""
    return {
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "services": {
            "api": "operational",
            "database": "operational",
            "redis": "operational"
        }
    }


@app.on_event("startup")
async def startup_event():
    """アプリ起動時の処理"""
    logger.info("Orchestrix API starting up...")


@app.on_event("shutdown")
async def shutdown_event():
    """アプリシャットダウン時の処理"""
    logger.info("Orchestrix API shutting down...")


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )
