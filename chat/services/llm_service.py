import os
from transformers import AutoTokenizer, AutoModelForCausalLM
import torch
from django.conf import settings
import logging
import traceback

logger = logging.getLogger(__name__)

class LLMService:
    def __init__(self):
        try:
            self.model_name = settings.LLM_MODEL
            self.hf_token = settings.HF_API_TOKEN
            
            logger.info(f"Initializing LLM service with model: {self.model_name}")
            logger.info(f"HF Token available: {bool(self.hf_token)}")
            
            # Initialize tokenizer with better error handling
            try:
                self.tokenizer = AutoTokenizer.from_pretrained(
                    self.model_name, 
                    trust_remote_code=True,
                    token=self.hf_token
                )
                logger.info("Tokenizer initialized successfully")
            except Exception as e:
                logger.error(f"Failed to initialize tokenizer: {str(e)}")
                logger.error(traceback.format_exc())
                raise
            
            # Initialize model with better error handling
            try:
                device = torch.device('cpu')
                logger.info(f"Using device: {device}")
                
                self.model = AutoModelForCausalLM.from_pretrained(
                    self.model_name,
                    trust_remote_code=True,
                    token=self.hf_token,
                    device_map='cpu',
                    torch_dtype=torch.float32,
                    low_cpu_mem_usage=True
                )
                self.model.to(device)
                logger.info("Model initialized successfully")
            except Exception as e:
                logger.error(f"Failed to initialize model: {str(e)}")
                logger.error(traceback.format_exc())
                raise
            
        except Exception as e:
            logger.error(f"Error in LLM service initialization: {str(e)}")
            logger.error(traceback.format_exc())
            raise

    async def get_response(self, message, conversation_history):
        try:
            logger.info(f"Generating response for message: {message[:50]}...")
            logger.info(f"Conversation history length: {len(conversation_history)}")
            
            formatted_history = self._format_conversation_history(conversation_history)
            prompt = self._prepare_prompt(formatted_history, message)
            
            logger.info(f"Prepared prompt length: {len(prompt)}")
            
            response = self._generate_response(prompt)
            
            logger.info(f"Generated response length: {len(response)}")
            return response
            
        except Exception as e:
            logger.error(f"Error generating response: {str(e)}")
            logger.error(traceback.format_exc())
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

    def _generate_response(self, prompt):
        try:
            # Tokenize the prompt
            inputs = self.tokenizer(prompt, return_tensors="pt")
            
            # Generate response
            with torch.no_grad():
                outputs = self.model.generate(
                    **inputs,
                    max_new_tokens=512,
                    num_return_sequences=1,
                    temperature=0.7,
                    do_sample=True,
                    pad_token_id=self.tokenizer.eos_token_id
                )
            
            # Decode and clean response
            response = self.tokenizer.decode(outputs[0], skip_special_tokens=True)
            
            # Extract only the assistant's response
            response_parts = response.split("Assistant:")
            if len(response_parts) > 1:
                return response_parts[-1].strip()
            return response.strip()
            
        except Exception as e:
            logger.error(f"Error in response generation: {str(e)}")
            raise