import requests
from app.config import get_gemini_api_key

def call_gemini(prompt: str) -> str:
    api_key = get_gemini_api_key()
    if not api_key:
        return "[Gemini API key not set]"
    url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent?key={api_key}"
    headers = {"Content-Type": "application/json"}
    data = {
        "contents": [
            {"parts": [{"text": prompt}]}
        ]
    }
    try:
        resp = requests.post(url, headers=headers, json=data, timeout=15)
        resp.raise_for_status()
        result = resp.json()
        return result["candidates"][0]["content"]["parts"][0]["text"]
    except Exception as e:
        return f"[Gemini API error] {e}" 