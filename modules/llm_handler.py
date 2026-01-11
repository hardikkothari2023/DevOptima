"""
Handles all interactions with the Groq Large Language Model (LLM) API.
"""

import os
import time
from groq import Groq, APIError
import streamlit as st
from dotenv import load_dotenv
from utils.logger import setup_logger

# Initialize logger for this module
logger = setup_logger("llm_handler")

# Load environment variables from .env file for local development
load_dotenv()

# --- CONFIGURATION ---
MAX_RETRIES = 3
RETRY_DELAY_SECONDS = 2
GROQ_MODEL = "llama-3.3-70b-versatile"
SUPPORTED_MODELS = {"llama-3.3-70b-versatile", "llama-3.1-8b-instant"}

if GROQ_MODEL not in SUPPORTED_MODELS:
    raise RuntimeError(f"Unsupported Groq model: {GROQ_MODEL}. Please check llm_handler.py")

# --- API CLIENT INITIALIZATION ---
def _get_api_key() -> str | None:
    try:
        if hasattr(st, "secrets") and "GROQ_API_KEY" in st.secrets:
            return st.secrets["GROQ_API_KEY"]
    except Exception:
        pass
    return os.getenv("GROQ_API_KEY")

def get_groq_client() -> Groq | None:
    api_key = _get_api_key()
    return Groq(api_key=api_key) if api_key else None

# --- CORE LLM INTERACTION ---
def call_groq_api(system_prompt: str, user_code: str, model_name: str = GROQ_MODEL) -> str:
    """
    Sends a request to the Groq API with retry logic.
    """
    client = get_groq_client()
    if not client:
        logger.error("GROQ_API_KEY not found in secrets or environment.")
        return "ERROR: GROQ_API_KEY not found."

    user_prompt = f"USER_CODE:\n```python\n{user_code}\n```"
    logger.info(f"Calling Groq API with model: {model_name}")
    
    for attempt in range(MAX_RETRIES):
        try:
            chat_completion = client.chat.completions.create(
                model=model_name,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt},
                ],
                temperature=0.1,
                max_tokens=4096,
            )
            response_content = chat_completion.choices[0].message.content
            logger.info(f"Successfully received response from Groq on attempt {attempt + 1}")
            return response_content
            
        except APIError as e:
            error_message = f"Groq API Error on attempt {attempt + 1}: {e}"
            logger.error(error_message)
            if attempt < MAX_RETRIES - 1:
                time.sleep(RETRY_DELAY_SECONDS * (attempt + 1))
            else:
                return f"ERROR: Failed to communicate with Groq API after {MAX_RETRIES} attempts. Last error: {e}"
        except Exception as e:
            logger.error(f"Unexpected error in call_groq_api: {e}")
            return f"An unexpected error occurred: {e}"
            
    return "ERROR: An unknown error occurred after all retries."
