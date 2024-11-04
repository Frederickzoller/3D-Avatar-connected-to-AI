import requests
from django.conf import settings
import json

class LLMService:
    def __init__(self):
        self.api_url = f"https://api-inference.huggingface.co/models/{settings.LLM_MODEL}"
        self.headers = {"Authorization": f"Bearer {settings.HF_API_TOKEN}"}

    async def get_response(self, message: str, conversation_context: list = None) -> str:
        try:
            # Format conversation history
            formatted_messages = ""
            if conversation_context:
                for msg in conversation_context:
                    role = "User: " if msg["role"] == "user" else "Assistant: "
                    formatted_messages += f"{role}{msg['content']}\n"
            
            # Add current message
            formatted_messages += f"User: {message}\nAssistant: "

            # Prepare payload
            payload = {
                "inputs": formatted_messages,
                "parameters": {
                    "max_length": 150,
                    "temperature": 0.7,
                    "return_full_text": False
                }
            }

            # Make API request
            response = requests.post(self.api_url, headers=self.headers, json=payload)
            response.raise_for_status()  # Raise exception for bad status codes
            
            # Parse response
            result = response.json()
            if isinstance(result, list) and len(result) > 0:
                return result[0].get('generated_text', 'I apologize, but I could not generate a response.')
            return 'I apologize, but I could not generate a response.'

        except Exception as e:
            print(f"Error in LLM service: {str(e)}")
            return "I apologize, but I'm having trouble processing your request right now."