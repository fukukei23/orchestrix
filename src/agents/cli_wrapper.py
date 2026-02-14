"""
汎用CLI Wrapperモジュール
様々なAIエージェントCLIを統一的に扱うためのラッパー
"""

import subprocess
import yaml
from typing import Dict, List, Optional, Any
from pathlib import Path
import os


class CLIWrapper:
    def __init__(self, config_path: str = None):
        if config_path is None:
            config_path = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), 'config', 'agents.yaml')
        self.config_path = config_path
        self.agents_config = self._load_config()

    def _load_config(self) -> Dict:
        try:
            with open(self.config_path, 'r', encoding='utf-8') as f:
                return yaml.safe_load(f)
        except FileNotFoundError:
            return {'agents': {
                'claude_code': {'name': 'Claude Code', 'cli_command': 'claude', 'default_model': 'claude-sonnet-4-5-20250929', 'supports_features': ['code', 'file_edit', 'bash'], 'cost_per_1k_input': 3.0, 'cost_per_1k_output': 15.0, 'enabled': True}
            }}

    def get_available_agents(self) -> List[str]:
        return [agent_id for agent_id, config in self.agents_config['agents'].items() if config.get('enabled', True)]

    def get_agent_config(self, agent_id: str) -> Optional[Dict]:
        return self.agents_config['agents'].get(agent_id)
