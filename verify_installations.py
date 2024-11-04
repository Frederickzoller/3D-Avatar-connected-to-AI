# Create this file in your project root
import torch
import transformers
from transformers import AutoModelForCausalLM, AutoTokenizer

def verify_installations():
    print(f"PyTorch version: {torch.__version__}")
    print(f"Transformers version: {transformers.__version__}")
    
    # Test model loading
    try:
        tokenizer = AutoTokenizer.from_pretrained("Qwen/Qwen2.5-72B-Instruct", trust_remote_code=True)
        print("✓ Tokenizer loaded successfully")
    except Exception as e:
        print(f"× Error loading tokenizer: {str(e)}")

if __name__ == "__main__":
    verify_installations() 