import openai

class OpenAIService:
   def __init__(self, api_key: str):
       self.api_key = api_key
       openai.api_key = api_key

   def generate_commit_message(self, file_content: str, language: str = 'ko') -> str:
       commit_types = {
           'feat': '새로운 기능 추가',
           'fix': '버그 수정',
           'docs': '문서 수정', 
           'style': '코드 포맷팅, 세미콜론 누락, 코드 변경이 없는 경우',
           'refactor': '코드 리팩토링',
           'test': '테스트 코드, 리팩토링 테스트 코드 추가',
           'chore': '빌드 업무 수정, 패키지 매니저 수정',
           'comment': '주석 추가 및 변경',
           'remove': '파일, 폴더 삭제',
           'rename': '파일, 폴더명 수정'
       }

       try:
           response = openai.chat.completions.create(
               model="gpt-3.5-turbo",
               messages=[
                   {
                       "role": "system",
                       "content": (
                           f"다음 커밋 타입 중에서 하나를 선택하여 '{language}'로 커밋 메시지를 작성하세요:\n" +
                           "\n".join([f"- {k}: {v}" for k, v in commit_types.items()]) +
                           "\n\n형식: [타입]: [설명]"
                       )
                   },
                   {"role": "user", "content": file_content}
               ],
               max_tokens=100
           )
           return response.choices[0].message.content.strip()
       except Exception as e:
           print(f"Error generating commit message: {str(e)}")
           return None