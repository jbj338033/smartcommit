import openai
from typing import Optional, Dict, List
import re
from datetime import datetime

class OpenAIService:
    def __init__(self, api_key: str):
        if not isinstance(api_key, str) or not api_key.strip():
            raise ValueError("API key must be a non-empty string")
            
        self.api_key = api_key
        openai.api_key = api_key
        
        self.commit_types = {
            'en': {
                'feat': 'Add new feature',
                'fix': 'Fix a bug',
                'docs': 'Update documentation',
                'style': 'Code formatting',
                'refactor': 'Code refactoring',
                'test': 'Add or update tests',
                'chore': 'Update build tasks',
                'perf': 'Performance improvements',
                'ci': 'CI/CD changes',
                'security': 'Security fixes',
                'deps': 'Dependencies updates',
                'breaking': 'Breaking changes',
                'revert': 'Revert changes'
            },
            'ko': {
                'feat': '새로운 기능 추가',
                'fix': '버그 수정',
                'docs': '문서 수정',
                'style': '코드 포맷팅',
                'refactor': '코드 리팩토링',
                'test': '테스트 코드 추가',
                'chore': '빌드 업무 수정',
                'perf': '성능 개선',
                'ci': 'CI/CD 변경',
                'security': '보안 수정',
                'deps': '종속성 업데이트',
                'breaking': '주요 변경사항',
                'revert': '변경사항 되돌리기'
            }
        }

    def _analyze_code(self, content: str) -> List[str]:
        patterns = {
            'test': r'test|spec|assert|describe|it\s*\(',
            'security': r'security|auth|crypto|password|token',
            'perf': r'performance|optimize|cache|speed',
            'deps': r'dependency|package\.json|requirements\.txt'
        }
        
        return [key for key, pattern in patterns.items() 
                if re.search(pattern, content, re.I)]

    def generate_commit_message(self, file_content: str, language: str = 'en') -> Optional[str]:
        if not isinstance(file_content, str) or not file_content.strip():
            raise ValueError("File content must be a non-empty string")
        
        if language not in self.commit_types:
            raise ValueError(f"Unsupported language: {language}")

        indicators = self._analyze_code(file_content)
        
        prompt = f"""As a senior developer, generate a precise git commit message.

Rules:
<type>: <description>
Language: {language}
Max length: 50 chars
Use imperative mood
No punctuation at end

Types:
{"\n".join([f"{k}: {v}" for k, v in self.commit_types[language].items()])}

Analysis: {", ".join(indicators) if indicators else "none"}
"""

        try:
            response = openai.chat.completions.create(
                model="gpt-4-turbo-preview",
                messages=[
                    {"role": "system", "content": prompt},
                    {"role": "user", "content": file_content}
                ],
                max_tokens=60,
                temperature=0.4,
                presence_penalty=0.2,
                frequency_penalty=0.3,
                top_p=0.95,
                stop=["\n", "。", ".", "!"]
            )
            
            if not response.choices:
                return None
                
            message = response.choices[0].message.content.strip()
            message = re.sub(r'[.!？。]+$', '', message).lower()
            
            return message if re.match(r'^[a-z]+(\([^)]+\))?!?: .+$', message) else None
            
        except Exception as e:
            print(f"Error generating commit message: {str(e)}")
            return None