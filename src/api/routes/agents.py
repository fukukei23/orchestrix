"""
エージェント関連のAPIルート
"""

from fastapi import APIRouter, HTTPException, status
from typing import List
import logging
import yaml
import os


router = APIRouter()
logger = logging.getLogger(__name__)

_CONFIG_PATH = os.path.join(
    os.path.dirname(os.path.dirname(os.path.dirname(__file__))),
    '..', 'config', 'agents.yaml'
)


def _load_agents_config():
    try:
        with open(_CONFIG_PATH, 'r', encoding='utf-8') as f:
            return yaml.safe_load(f)
    except FileNotFoundError:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Agent configuration file not found"
        )


def _format_agent(agent_id: str, config: dict) -> dict:
    return {
        "id": agent_id,
        "name": config.get('name', ''),
        "cli_command": config.get('cli_command', ''),
        "default_model": config.get('default_model', ''),
        "supports_features": config.get('supports_features', []),
        "cost_per_1k_input": config.get('cost_per_1k_input', 0),
        "cost_per_1k_output": config.get('cost_per_1k_output', 0),
        "enabled": config.get('enabled', True)
    }


@router.get("/", response_model=List[dict])
async def list_agents():
    config = _load_agents_config()
    return [_format_agent(aid, acfg) for aid, acfg in config.get('agents', {}).items()]


@router.get("/{agent_id}", response_model=dict)
async def get_agent(agent_id: str):
    config = _load_agents_config()
    agents = config.get('agents', {})

    if agent_id not in agents:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Agent {agent_id} not found"
        )

    return _format_agent(agent_id, agents[agent_id])


@router.post("/{agent_id}/toggle", response_model=dict)
async def toggle_agent(agent_id: str, enabled: bool = True):
    config = _load_agents_config()
    agents = config.get('agents', {})

    if agent_id not in agents:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Agent {agent_id} not found"
        )

    agents[agent_id]['enabled'] = enabled

    with open(_CONFIG_PATH, 'w', encoding='utf-8') as f:
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
    config = _load_agents_config()
    agents = config.get('agents', {})

    if agent_id not in agents:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Agent {agent_id} not found"
        )

    agent_config = agents[agent_id]
    cost_input = agent_config.get('cost_per_1k_input', 0)
    cost_output = agent_config.get('cost_per_1k_output', 0)

    input_cost = (input_tokens / 1000) * cost_input
    output_cost = (output_tokens / 1000) * cost_output

    return {
        "agent_id": agent_id,
        "model": model,
        "input_tokens": input_tokens,
        "output_tokens": output_tokens,
        "estimated_cost_usd": round(input_cost + output_cost, 4),
        "breakdown": {
            "input_cost": round(input_cost, 4),
            "output_cost": round(output_cost, 4)
        }
    }
