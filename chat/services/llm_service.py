import os
from transformers import AutoTokenizer, pipeline
from django.conf import settings
import logging
import torch

logger = logging.getLogger(__name__)

class LLMService:
    def __init__(self):
        try:
            self.model_name = settings.LLM_MODEL
            self.hf_token = settings.HF_API_TOKEN
            
            logger.info(f"Initializing LLM service with model: {self.model_name}")
            
            # Check CUDA availability but default to CPU
            device = "cpu"
            logger.info(f"Using device: {device}")
            
            # Initialize tokenizer first
            try:
                self.tokenizer = AutoTokenizer.from_pretrained(
                    self.model_name,
                    token=self.hf_token,
                    use_fast=False  # Use slower but more compatible tokenizer
                )
            except Exception as e:
                logger.error(f"Error initializing tokenizer: {str(e)}")
                raise
            
            # Initialize pipeline with explicit model kwargs
            self.pipe = pipeline(
                "text-generation",
                model=self.model_name,
                tokenizer=self.tokenizer,
                token=self.hf_token,
                device=device,
                model_kwargs={
                    "low_cpu_mem_usage": True,
                    "torch_dtype": torch.float32
                }
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
            
            # Generate response with error handling
            try:
                response = self.pipe(
                    prompt,
                    max_new_tokens=512,
                    num_return_sequences=1,
                    temperature=0.7,
                    do_sample=True,
                    pad_token_id=self.tokenizer.eos_token_id
                )[0]['generated_text']
            except Exception as e:
                logger.error(f"Error during text generation: {str(e)}")
                return "I apologize, but I'm having trouble processing your request. Please try again."
            
            # Extract only the assistant's response
            response_parts = response.split("Assistant:")
            if len(response_parts) > 1:
                response = response_parts[-1].strip()
            
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