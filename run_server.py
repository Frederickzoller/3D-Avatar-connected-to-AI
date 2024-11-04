from waitress import serve
from citizens_llm_chat.wsgi import application
import os

port = int(os.environ.get("PORT", 8000))
serve(application, host="0.0.0.0", port=port) 