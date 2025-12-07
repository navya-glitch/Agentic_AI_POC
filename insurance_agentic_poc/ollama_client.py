# ollama_client.py
import requests

OLLAMA_URL = "http://localhost:11434/api/chat"
DEFAULT_MODEL = "gemma3:1b"  # or any other model you have


def chat_ollama(system_prompt: str, user_prompt: str, model: str = DEFAULT_MODEL) -> str:
    """
    Simple helper to call Ollama /api/chat with a system + user prompt.
    Returns assistant content as string.
    """
    payload = {
        "model": model,
        "stream": False,
        "messages": [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt},
        ],
    }

    resp = requests.post(OLLAMA_URL, json=payload, timeout=120)
    resp.raise_for_status()
    data = resp.json()
    return data["message"]["content"]
