import requests

OLLAMA_URL = "http://localhost:11434/api/generate"
MODEL = "llama3"

def generate_llm(prompt: str, timeout=180):
    payload = {
        "model": MODEL,
        "prompt": prompt,
        "stream": False
    }

    response = requests.post(OLLAMA_URL, json=payload, timeout=timeout)
    response.raise_for_status()

    return response.json()["response"]
