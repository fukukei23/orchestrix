"""LLM Clients と API Dependencies のテスト"""
import pytest
from unittest.mock import patch, MagicMock


class TestClaudeClient:

    @patch.dict("os.environ", {"ANTHROPIC_API_KEY": "test-key"})
    def test_init_sets_api_key(self):
        from src.llm.claude_client import ClaudeClient
        client = ClaudeClient()
        assert client.api_key == "test-key"

    @patch.dict("os.environ", {"ANTHROPIC_API_KEY": "test-key"})
    @patch("src.llm.claude_client.anthropic.Anthropic")
    def test_invoke_success(self, mock_anthropic_cls):
        from src.llm.claude_client import ClaudeClient
        mock_response = MagicMock()
        mock_response.content = [MagicMock(text="Hello")]
        mock_response.usage.input_tokens = 10
        mock_response.usage.output_tokens = 20
        mock_response.usage.total_tokens = 30
        mock_anthropic_cls.return_value.messages.create.return_value = mock_response

        client = ClaudeClient()
        result = client.invoke("test prompt")
        assert result["success"] is True
        assert result["content"] == "Hello"

    @patch.dict("os.environ", {"ANTHROPIC_API_KEY": "test-key"})
    @patch("src.llm.claude_client.anthropic.Anthropic")
    def test_invoke_error_returns_failure(self, mock_anthropic_cls):
        from src.llm.claude_client import ClaudeClient
        mock_anthropic_cls.return_value.messages.create.side_effect = Exception("API error")

        client = ClaudeClient()
        result = client.invoke("test")
        assert result["success"] is False
        assert "API error" in result["error"]


class TestOpenAIClient:

    @patch.dict("os.environ", {"OPENAI_API_KEY": "test-key"})
    def test_init_default_base_url(self):
        from src.llm.openai_client import OpenAIClient
        client = OpenAIClient()
        assert client.base_url is None

    @patch.dict("os.environ", {"OPENAI_API_KEY": "test-key"})
    def test_init_custom_base_url(self):
        from src.llm.openai_client import OpenAIClient
        client = OpenAIClient(base_url="https://custom.api/v1")
        assert client.base_url == "https://custom.api/v1"

    @patch.dict("os.environ", {"OPENAI_API_KEY": "test-key"})
    @patch("src.llm.openai_client.openai.OpenAI")
    def test_invoke_success(self, mock_openai_cls):
        from src.llm.openai_client import OpenAIClient
        mock_response = MagicMock()
        mock_response.choices = [MagicMock()]
        mock_response.choices[0].message.content = "Result"
        mock_response.usage.prompt_tokens = 50
        mock_response.usage.completion_tokens = 25
        mock_response.usage.total_tokens = 75
        mock_openai_cls.return_value.chat.completions.create.return_value = mock_response

        client = OpenAIClient()
        result = client.invoke("test prompt")
        assert result["success"] is True
        assert result["content"] == "Result"

    @patch.dict("os.environ", {"OPENAI_API_KEY": "test-key"})
    @patch("src.llm.openai_client.openai.OpenAI")
    def test_invoke_error_returns_failure(self, mock_openai_cls):
        from src.llm.openai_client import OpenAIClient
        mock_openai_cls.return_value.chat.completions.create.side_effect = Exception("Timeout")

        client = OpenAIClient()
        result = client.invoke("test")
        assert result["success"] is False

    def test_missing_api_key_raises(self):
        from src.llm.openai_client import OpenAIClient
        with patch.dict("os.environ", {}, clear=True):
            with pytest.raises(ValueError, match="OPENAI_API_KEY"):
                OpenAIClient()
