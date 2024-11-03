from transformers import AutoModelForCausalLM, AutoTokenizer
from django.conf import settings
import torch

class LLMService:
    def __init__(self):
        self.tokenizer = AutoTokenizer.from_pretrained(settings.LLM_MODEL, trust_remote_code=True)
        self.model = AutoModelForCausalLM.from_pretrained(
            settings.LLM_MODEL,
            device_map="auto",
            trust_remote_code=True
        ).eval()
        
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
            
            # Generate response
            response = self.model.chat(
                self.tokenizer,
                formatted_messages,
                history=[],
                temperature=0.7,
                max_length=150
            )
            
            return response
            
        except Exception as e:
            print(f"Error in LLM service: {str(e)}")
            return "I apologize, but I'm having trouble processing your request right now."