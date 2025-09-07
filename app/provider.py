import os
import httpx
from typing import Dict

class Provider:
    """Abstraction over different LLM providers.
    Defaults to a safe 'echo' fallback if nothing configured.
    Supports Ollama if OLLAMA_BASE_URL is set.
    TODO: add OpenAI/Anthropic clients as needed.
    """
    def __init__(self) -> None:
        self.ollama_url = os.getenv("OLLAMA_BASE_URL")
        self.ollama_model = os.getenv("OLLAMA_MODEL", "llama3.1")
        self.mode = "echo"
        if self.ollama_url:
            self.mode = "ollama"
        # Example: if os.getenv("OPENAI_API_KEY"): self.mode = "openai"

    async def generate(self, prompt: str, meta: Dict) -> str:
        if self.mode == "ollama":
            async with httpx.AsyncClient(timeout=60) as client:
                resp = await client.post(f"{self.ollama_url}/api/generate", json={
                    "model": self.ollama_model,
                    "prompt": prompt,
                    "stream": False
                })
                resp.raise_for_status()
                data = resp.json()
                return data.get("response","")
        elif self.mode == "openai":
            # TODO: implement OpenAI call if desired
            return f"[openai-not-configured] {prompt}"
        else:
            # safe echo fallback for demo
            return f"[echo] {prompt}"
