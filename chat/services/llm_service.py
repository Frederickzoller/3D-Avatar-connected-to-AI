import os
from transformers import AutoTokenizer, pipeline
from django.conf import settings
import logging
import torch
from concurrent.futures import ThreadPoolExecutor
import asyncio

logger = logging.getLogger(__name__)

class LLMService:
    _instance = None
    _executor = ThreadPoolExecutor(max_workers=2)

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(LLMService, cls).__new__(cls)
            cls._instance._initialized = False
        return cls._instance

    def __init__(self):
        if self._initialized:
            return
            
        try:
            self.model_name = settings.LLM_MODEL
            self.hf_token = settings.HF_API_TOKEN
            
            logger.info(f"Initializing LLM service with model: {self.model_name}")
            
            # Initialize tokenizer with simpler settings
            self.tokenizer = AutoTokenizer.from_pretrained(
                self.model_name,
                token=self.hf_token
            )
            
            # Initialize pipeline with basic settings
            self.pipe = pipeline(
                "text-generation",
                model=self.model_name,
                tokenizer=self.tokenizer,
                token=self.hf_token,
                device="cpu"
            )
            
            logger.info("LLM service initialized successfully")
            self._initialized = True
            
        except Exception as e:
            logger.error(f"Error initializing LLM service: {str(e)}")
            raise

    async def get_response(self, message, conversation_history):
        try:
            logger.info(f"Generating response for message: {message[:50]}...")
            
            # Format the prompt
            formatted_history = self._format_conversation_history(conversation_history)
            prompt = self._prepare_prompt(formatted_history, message)
            
            # Generate response synchronously (pipeline doesn't support async)
            outputs = self.pipe(
                prompt,
                max_new_tokens=128,
                num_return_sequences=1,
                temperature=0.7,
                do_sample=True,
                pad_token_id=self.tokenizer.eos_token_id
            )
            
            # Extract response
            response_text = outputs[0]['generated_text']
            response_parts = response_text.split("Assistant:")
            
            if len(response_parts) > 1:
                response = response_parts[-1].strip()
            else:
                response = response_text.strip()
            
            logger.info(f"Generated response: {response[:50]}...")
            return response
            
        except Exception as e:
            logger.error(f"Error in get_response: {str(e)}")
            return "I apologize, but I'm having trouble generating a response right now. Please try again later."

    def _format_conversation_history(self, history):
        try:
            formatted = []
            for msg in history:
                role = "User" if msg['role'] == 'user' else "Assistant"
                formatted.append(f"{role}: {msg['content']}")
            return "\n".join(formatted)
        except Exception as e:
            logger.error(f"Error formatting conversation history: {str(e)}")
            return ""

    def _prepare_prompt(self, history, new_message):
        try:
            if history:
                return f"{history}\nUser: {new_message}\nAssistant:"
            return f"User: {new_message}\nAssistant:"
        except Exception as e:
            logger.error(f"Error preparing prompt: {str(e)}")
            return f"User: {new_message}\nAssistant:"