"""OpenAI API client (OpenAI 互換 API もサポート)"""
import os
import openai
from typing import Dict, Any, Optional
from dotenv import load_dotenv

load_dotenv()

class OpenAIClient:
    """OpenAI API クライアント (OpenAI 互換 API もサポート)"""

    def __init__(self, base_url: Optional[str] = None):
        self.base_url = base_url
        self.api_key = os.getenv('OPENAI_API_KEY', '')
        if not self.api_key:
            raise ValueError("OPENAI_API_KEY environment variable is not set")

        # base_url が指定されている場合は OpenAI 互換 API を使用
        if base_url:
            self.client = openai.OpenAI(api_key=self.api_key, base_url=base_url)
        else:
            self.client = openai.OpenAI(api_key=self.api_key)

    def invoke(self, prompt: str, model: str = "gpt-4o") -> Dict[str, Any]:
        """
        OpenAI APIを呼び出す

        Args:
            prompt: プロンプト
            model: モデル名（デフォルト: gpt-4o）

        Returns:
            レスポンス辞書
        """
        try:
            response = self.client.chat.completions.create(
                model=model,
                messages=[
                    {
                        "role": "user",
                        "content": prompt
                    }
                ],
                max_tokens=4096
            )

            return {
                "success": True,
                "content": response.choices[0].message.content,
                "model": model,
                "input_tokens": response.usage.prompt_tokens,
                "output_tokens": response.usage.completion_tokens,
                "total_tokens": response.usage.total_tokens
            }

        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }

    def count_tokens(self, text: str, model: str = "gpt-4o") -> int:
        """
        テキスト数をカウントする

        Args:
            text: テキスト
            model: モデル名

        Returns:
            トークン数
        """
        try:
            import tiktoken
            encoding = tiktoken.encoding_for_model(model)
            return len(encoding.encode(text))

        except Exception as e:
            print(f"Error counting tokens: {e}")
            return 0
