import os
from transformers import AutoTokenizer, pipeline
from django.conf import settings
import logging

logger = logging.getLogger(__name__)

class LLMService:
    def __init__(self):
        try:
            self.model_name = settings.LLM_MODEL
            self.hf_token = settings.HF_API_TOKEN
            
            logger.info(f"Initializing LLM service with model: {self.model_name}")
            
            # Initialize pipeline with CPU device
            self.pipe = pipeline(
                "text-generation",
                model=self.model_name,
                token=self.hf_token,
                device="cpu"  # Force CPU usage
            )
            
            logger.info("LLM service initialized successfully")
            
        except Exception as e:
            logger.error(f"Error initializing LLM service: {str(e)}")
            raise

    async def get_response(self, message, conversation_history):
        try:
            logger.info(f"Generating response for message: {message[:50]}...")
            
            # Format conversation history
            formatted_history = self._format_conversation_history(conversation_history)
            
            # Prepare the prompt
            prompt = self._prepare_prompt(formatted_history, message)
            
            # Generate response using pipeline
            response = self.pipe(
                prompt,
                max_new_tokens=512,
                num_return_sequences=1,
                temperature=0.7,
                do_sample=True
            )[0]['generated_text']
            
            # Extract only the assistant's response
            response_parts = response.split("Assistant:")
            if len(response_parts) > 1:
                response = response_parts[-1].strip()
            
            logger.info(f"Generated response: {response[:50]}...")
            return response
            
        except Exception as e:
            logger.error(f"Error generating response: {str(e)}")
            return "I apologize, but I'm having trouble generating a response right now. Please try again later."

    def _format_conversation_history(self, history):
        formatted = []
        for msg in history:
            role = "User" if msg['role'] == 'user' else "Assistant"
            formatted.append(f"{role}: {msg['content']}")
        return "\n".join(formatted)

    def _prepare_prompt(self, history, new_message):
        if history:
            return f"{history}\nUser: {new_message}\nAssistant:"
        return f"User: {new_message}\nAssistant:"