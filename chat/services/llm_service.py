import openai
from django.conf import settings

class LLMService:
    def __init__(self):
        openai.api_key = settings.OPENAI_API_KEY
        
    async def get_response(self, message: str, conversation_context: list = None) -> str:
        try:
            messages = []
            if conversation_context:
                messages.extend(conversation_context)
            
            messages.append({"role": "user", "content": message})
            
            response = await openai.ChatCompletion.acreate(
                model="gpt-4",
                messages=messages,
                temperature=0.7,
                max_tokens=150
            )
            
            return response.choices[0].message.content
            
        except Exception as e:
            print(f"Error in LLM service: {str(e)}")
            return "I apologize, but I'm having trouble processing your request right now." 