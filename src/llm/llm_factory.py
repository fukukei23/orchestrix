"""LLM client factory"""
from typing import Dict, Any
from .claude_client import ClaudeClient
from .openai_client import OpenAIClient


class LLMFactory:
    """LLM クライアントファクトリー"""

    _clients: Dict[str, Any] = {}

    @classmethod
    def get_client(cls, agent_type: str) -> Any:
        """
        エージェントタイプからLLMクライアントを取得する

        Args:
            agent_type: エージェントタイプ（claude_code, openclaw, glm_llm, minimax_llm, kimi_llm, codex_cli, gemini_cli）

        Returns:
            LLMクライアントインスタンス
        """
        if agent_type not in cls._clients:
            if agent_type == 'claude_code':
                cls._clients[agent_type] = ClaudeClient()
            elif agent_type == 'glm_llm':
                # GLM (智谱AI) - OpenAI 互換 API
                cls._clients[agent_type] = OpenAIClient(base_url="https://open.bigmodel.cn/api/paas/v4")
            elif agent_type == 'minimax_llm':
                # MiniMax - OpenAI 互換 API
                cls._clients[agent_type] = OpenAIClient(base_url="https://api.minimax.chat/v1")
            elif agent_type == 'kimi_llm':
                # Kimi (Moonshot AI) - OpenAI 互換 API
                cls._clients[agent_type] = OpenAIClient(base_url="https://api.moonshot.cn/v1")
            elif agent_type == 'openai':
                cls._clients[agent_type] = OpenAIClient()
            elif agent_type == 'codex_cli':
                # OpenAI Codex (古い API、非推奨)
                cls._clients[agent_type] = OpenAIClient()
            elif agent_type == 'gemini_cli':
                # Google Gemini API（将来実装）
                raise ValueError(f"Agent type {agent_type} not yet implemented")

        return cls._clients[agent_type]

    @classmethod
    def reset_clients(cls):
        """全てのクライアントをリセットする"""
        cls._clients.clear()
