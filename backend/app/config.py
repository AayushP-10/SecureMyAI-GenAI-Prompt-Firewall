# Placeholder for configuration and environment variables 

import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

def get_groq_api_key():
    return os.getenv("GROQ_API_KEY")

def get_gemini_api_key():
    return os.getenv("GEMINI_API_KEY") 