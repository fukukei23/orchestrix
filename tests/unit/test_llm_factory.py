"""LLM Factory テスト"""
import pytest
from unittest.mock import patch, MagicMock

from src.llm.llm_factory import LLMFactory
from src.llm.claude_client import ClaudeClient
from src.llm.openai_client import OpenAIClient


@pytest.fixture(autouse=True)
def reset_factory():
    LLMFactory.reset_clients()
    yield
    LLMFactory.reset_clients()


class TestGetClient:

    @patch.dict("os.environ", {"ANTHROPIC_API_KEY": "test-key"})
    def test_claude_code_returns_claude_client(self):
        client = LLMFactory.get_client("claude_code")
        assert isinstance(client, ClaudeClient)

    @patch.dict("os.environ", {"OPENAI_API_KEY": "test-key"})
    def test_openai_returns_openai_client(self):
        client = LLMFactory.get_client("openai")
        assert isinstance(client, OpenAIClient)

    @patch.dict("os.environ", {"OPENAI_API_KEY": "test-key"})
    def test_glm_llm_returns_openai_compatible(self):
        client = LLMFactory.get_client("glm_llm")
        assert isinstance(client, OpenAIClient)
        assert "bigmodel.cn" in client.base_url

    @patch.dict("os.environ", {"OPENAI_API_KEY": "test-key"})
    def test_minimax_llm_returns_openai_compatible(self):
        client = LLMFactory.get_client("minimax_llm")
        assert isinstance(client, OpenAIClient)
        assert "minimax" in client.base_url

    @patch.dict("os.environ", {"OPENAI_API_KEY": "test-key"})
    def test_kimi_llm_returns_openai_compatible(self):
        client = LLMFactory.get_client("kimi_llm")
        assert isinstance(client, OpenAIClient)
        assert "moonshot" in client.base_url

    def test_gemini_cli_raises_not_implemented(self):
        with pytest.raises(ValueError, match="not yet implemented"):
            LLMFactory.get_client("gemini_cli")

    def test_unknown_type_raises_keyerror(self):
        with pytest.raises(KeyError):
            LLMFactory.get_client("unknown_type")


class TestClientCaching:

    @patch.dict("os.environ", {"ANTHROPIC_API_KEY": "test-key"})
    def test_same_type_returns_cached_instance(self):
        c1 = LLMFactory.get_client("claude_code")
        c2 = LLMFactory.get_client("claude_code")
        assert c1 is c2


class TestResetClients:

    @patch.dict("os.environ", {"ANTHROPIC_API_KEY": "test-key"})
    def test_reset_clears_cache(self):
        LLMFactory.get_client("claude_code")
        LLMFactory.reset_clients()
        assert len(LLMFactory._clients) == 0
