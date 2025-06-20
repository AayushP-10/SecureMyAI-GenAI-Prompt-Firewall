import requests
from app.config import get_groq_api_key

def call_groq(prompt: str) -> str:
    api_key = get_groq_api_key()
    if not api_key:
        return "[Groq API key not set]"
    url = "https://api.groq.com/openai/v1/chat/completions"
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }
    data = {
        "model": "compound-beta",
        "messages": [
            {"role": "user", "content": prompt}
        ],
        "max_tokens": 512,
        "temperature": 0.7
    }
    try:
        resp = requests.post(url, headers=headers, json=data, timeout=15)
        resp.raise_for_status()
        result = resp.json()
        return result["choices"][0]["message"]["content"]
    except Exception as e:
        return f"[Groq API error] {e}" 