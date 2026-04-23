"""Claude API client"""
import os
import anthropic
from typing import Dict, Any
from dotenv import load_dotenv

load_dotenv()

class ClaudeClient:
    """Claude API クライアント"""

    def __init__(self):
        self.api_key = os.getenv('ANTHROPIC_API_KEY', '')
        if not self.api_key:
            raise ValueError("ANTHROPIC_API_KEY environment variable is not set")

        self.client = anthropic.Anthropic(api_key=self.api_key)

    def invoke(self, prompt: str, model: str = "claude-sonnet-4-5-20250929") -> Dict[str, Any]:
        """
        Claude APIを呼び出す

        Args:
            prompt: プロンプト
            model: モデル名（デフォルト: claude-sonnet-4-5-20250929）

        Returns:
            レスポンス辞書
        """
        try:
            message = self.client.messages.create(
                model=model,
                max_tokens=4096,
                messages=[
                    {
                        "role": "user",
                        "content": prompt
                    }
                ]
            )

            return {
                "success": True,
                "content": message.content[0].text,
                "model": model,
                "input_tokens": message.usage.input_tokens,
                "output_tokens": message.usage.output_tokens,
                "total_tokens": message.usage.total_tokens
            }

        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }

    def count_tokens(self, text: str, model: str = "claude-sonnet-4-5-20250929") -> int:
        """
        テキスト数をカウントする

        Args:
            text: テキスト
            model: モデル名

        Returns:
            トークン数
        """
        try:
            response = self.client.messages.create(
                model=model,
                max_tokens=4096,
                messages=[
                    {
                        "role": "user",
                        "content": text
                    }
                ]
            )

            return response.usage.input_tokens

        except Exception as e:
            print(f"Error counting tokens: {e}")
            return 0
