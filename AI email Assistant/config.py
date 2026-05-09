import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

EMAIL = os.getenv("EMAIL", "")
APP_PASSWORD = os.getenv("APP_PASSWORD", "")
OLLAMA_URL = os.getenv("OLLAMA_URL", "http://localhost:11434/api/generate")
OLLAMA_MODEL = os.getenv("OLLAMA_MODEL", "tinyllama")

if not EMAIL or not APP_PASSWORD:
    raise ValueError("❌ Missing EMAIL or APP_PASSWORD in .env file. Please set credentials.")
