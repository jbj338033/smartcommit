import openai
from typing import Optional

class OpenAIService:
    def __init__(self, api_key: str):
        self.api_key = api_key
        openai.api_key = api_key

    def generate_commit_message(self, file_content: str, language: str = 'ko') -> Optional[str]:
        try:
            response = openai.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[
                    {
                        "role": "system",
                        "content": (
                            f"Generate a concise git commit message in {language} "
                            "that follows conventional commits format. "
                            "Focus on what changes were made and why."
                        )
                    },
                    {"role": "user", "content": file_content}
                ],
                max_tokens=100
            )
            return response.choices[0].message.content.strip()
        except Exception:
            return None