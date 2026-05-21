"""
エージェント関連のAPIルート
"""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List, Dict
import logging
import yaml
import os


router = APIRouter()
logger = logging.getLogger(__name__)


@router.get("/", response_model=List[dict])
async def list_agents():
    """
    利用可能なエージェントを一覧

    Returns:
        エージェントのリスト
    """
    # エージェント設定ファイルを読み込み
    config_path = os.path.join(
        os.path.dirname(os.path.dirname(os.path.dirname(__file__))),
        '..',
        'config',
        'agents.yaml'
    )

    try:
        with open(config_path, 'r', encoding='utf-8') as f:
            config = yaml.safe_load(f)
    except FileNotFoundError:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Agent configuration file not found"
        )

    agents = []
    for agent_id, agent_config in config.get('agents', {}).items():
        agents.append({
            "id": agent_id,
            "name": agent_config.get('name', ''),
            "cli_command": agent_config.get('cli_command', ''),
            "default_model": agent_config.get('default_model', ''),
            "supports_features": agent_config.get('supports_features', []),
            "cost_per_1k_input": agent_config.get('cost_per_1k_input', 0),
            "cost_per_1k_output": agent_config.get('cost_per_1k_output', 0),
            "enabled": agent_config.get('enabled', True)
        })

    return agents


@router.get("/{agent_id}", response_model=dict)
async def get_agent(agent_id: str):
    """
    エージェント詳細を取得

    Args:
        agent_id: エージェントID

    Returns:
        エージェント詳細
    """
    config_path = os.path.join(
        os.path.dirname(os.path.dirname(os.path.dirname(__file__))),
        '..',
        'config',
        'agents.yaml'
    )

    try:
        with open(config_path, 'r', encoding='utf-8') as f:
            config = yaml.safe_load(f)
    except FileNotFoundError:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Agent configuration file not found"
        )

    agents = config.get('agents', {})

    if agent_id not in agents:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Agent {agent_id} not found"
        )

    agent_config = agents[agent_id]

    return {
        "id": agent_id,
        "name": agent_config.get('name', ''),
        "cli_command": agent_config.get('cli_command', ''),
        "default_model": agent_config.get('default_model', ''),
        "supports_features": agent_config.get('supports_features', []),
        "cost_per_1k_input": agent_config.get('cost_per_1k_input', 0),
        "cost_per_1k_output": agent_config.get('cost_per_1k_output', 0),
        "enabled": agent_config.get('enabled', True)
    }


@router.post("/{agent_id}/toggle", response_model=dict)
async def toggle_agent(agent_id: str, enabled: bool = True):
    """
    エージェントを有効/無効化

    Args:
        agent_id: エージェントID
        enabled: 有効化するかどうか

    Returns:
        結果
    """
    config_path = os.path.join(
        os.path.dirname(os.path.dirname(os.path.dirname(__file__))),
        '..',
        'config',
        'agents.yaml'
    )

    try:
        with open(config_path, 'r', encoding='utf-8') as f:
            config = yaml.safe_load(f)
    except FileNotFoundError:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Agent configuration file not found"
        )

    agents = config.get('agents', {})

    if agent_id not in agents:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Agent {agent_id} not found"
        )

    agents[agent_id]['enabled'] = enabled

    # 設定を保存
    with open(config_path, 'w', encoding='utf-8') as f:
        yaml.dump(config, f)

    logger.info(f"Toggled agent {agent_id}: {'enabled' if enabled else 'disabled'}")

    return {
        "agent_id": agent_id,
        "enabled": enabled,
        "message": f"Agent {agent_id} {'enabled' if enabled else 'disabled'} successfully"
    }


@router.post("/estimate-cost", response_model=dict)
async def estimate_cost(
    agent_id: str,
    model: str,
    input_tokens: int,
    output_tokens: int
):
    """
    コストを見積もる

    Args:
        agent_id: エージェントID
        model: モデル名
        input_tokens: 入力トークン数
        output_tokens: 出力トークン数

    Returns:
        見積もりコスト
    """
    config_path = os.path.join(
        os.path.dirname(os.path.dirname(os.path.dirname(__file__))),
        '..',
        'config',
        'agents.yaml'
    )

    try:
        with open(config_path, 'r', encoding='utf-8') as f:
            config = yaml.safe_load(f)
    except FileNotFoundError:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Agent configuration file not found"
        )

    agents = config.get('agents', {})

    if agent_id not in agents:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Agent {agent_id} not found"
        )

    agent_config = agents[agent_id]
    cost_per_1k_input = agent_config.get('cost_per_1k_input', 0)
    cost_per_1k_output = agent_config.get('cost_per_1k_output', 0)

    total_cost = ((input_tokens / 1000) * cost_per_1k_input +
                 (output_tokens / 1000) * cost_per_1k_output)

    return {
        "agent_id": agent_id,
        "model": model,
        "input_tokens": input_tokens,
        "output_tokens": output_tokens,
        "estimated_cost_usd": round(total_cost, 4),
        "breakdown": {
            "input_cost": round((input_tokens / 1000) * cost_per_1k_input, 4),
            "output_cost": round((output_tokens / 1000) * cost_per_1k_output, 4)
        }
    }
