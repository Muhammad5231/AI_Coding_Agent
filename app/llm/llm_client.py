"""
Local LLM Client.
Handles communication with local LLM instances (Ollama native or OpenAI-compatible local APIs).
Includes streaming support using pure standard HTTP library (requests).
"""

import json
import logging
import requests
from typing import Generator, Dict, Any, Tuple

logger = logging.getLogger("LLMClient")


class LLMClient:
    """Client for generating text and streaming responses from local LLM backends."""

    def __init__(self, config: Dict[str, Any]) -> None:
        self.api_type = config.get("api_type", "ollama").lower()
        self.api_url = config.get("api_url", "http://localhost:11434").rstrip("/")
        self.model_name = config.get("model_name", "llama3:8b")
        self.temperature = float(config.get("temperature", 0.2))
        self.max_tokens = int(config.get("max_tokens", 4096))
        self.timeout = int(config.get("timeout", 120))

    def test_connection(self) -> Tuple[bool, str]:
        """Test whether the endpoint and model are accessible."""
        try:
            if self.api_type == "ollama":
                url = f"{self.api_url}/api/tags"
                res = requests.get(url, timeout=5)
                if res.status_code == 200:
                    models = [m.get("name") for m in res.json().get("models", [])]
                    return True, f"Connected to Ollama! Available models: {', '.join(models) if models else 'None'}"
                return False, f"Ollama returned HTTP status {res.status_code}"
            else:
                # OpenAI Compatible
                url = f"{self.api_url}/v1/models"
                res = requests.get(url, timeout=5)
                if res.status_code == 200:
                    return True, "Successfully connected to OpenAI-compatible API endpoint!"
                return False, f"API returned HTTP status {res.status_code}"
        except Exception as e:
            logger.error(f"Connection test failed: {e}")
            return False, f"Connection failed: {str(e)}"

    def stream_generation(self, prompt: str, system_prompt: str = "") -> Generator[str, None, None]:
        """Stream chunks of text from the target LLM API."""
        if self.api_type == "ollama":
            yield from self._stream_ollama(prompt, system_prompt)
        else:
            yield from self._stream_openai(prompt, system_prompt)

    def _stream_ollama(self, prompt: str, system_prompt: str) -> Generator[str, None, None]:
        """Internal generator for Ollama `/api/generate` streaming endpoint."""
        url = f"{self.api_url}/api/generate"
        payload = {
            "model": self.model_name,
            "prompt": prompt,
            "system": system_prompt,
            "stream": True,
            "options": {
                "temperature": self.temperature,
                "num_predict": self.max_tokens
            }
        }
        
        try:
            response = requests.post(url, json=payload, stream=True, timeout=self.timeout)
            response.raise_for_status()

            for line in response.iter_lines():
                if line:
                    chunk = json.loads(line.decode("utf-8"))
                    text = chunk.get("response", "")
                    if text:
                        yield text
                    if chunk.get("done", False):
                        break
        except requests.exceptions.RequestException as e:
            logger.error(f"Ollama Streaming request error: {e}")
            yield f"\n[LLM Error: Request failed - {str(e)}]"

    def _stream_openai(self, prompt: str, system_prompt: str) -> Generator[str, None, None]:
        """Internal generator for OpenAI-compatible / Groq Cloud streaming endpoint."""
        url = f"{self.api_url}/v1/chat/completions"
        messages = []
        if system_prompt:
            messages.append({"role": "system", "content": system_prompt})
        messages.append({"role": "user", "content": prompt})

        payload = {
            "model": self.model_name,
            "messages": messages,
            "temperature": self.temperature,
            "max_tokens": self.max_tokens,
            "stream": True
        }

        # Headers for Cloud API Authentication
        headers = {"Content-Type": "application/json"}
        api_key = self.config.get("api_key", "").strip()
        if api_key:
            headers["Authorization"] = f"Bearer {api_key}"

        try:
            response = requests.post(url, json=payload, headers=headers, stream=True, timeout=self.timeout)
            response.raise_for_status()

            for line in response.iter_lines():
                if line:
                    line_str = line.decode("utf-8").strip()
                    if line_str.startswith("data: "):
                        data_content = line_str[6:]
                        if data_content == "[DONE]":
                            break
                        try:
                            data_json = json.loads(data_content)
                            delta = data_json["choices"][0]["delta"]
                            if "content" in delta:
                                yield delta["content"]
                        except json.JSONDecodeError:
                            continue
        except requests.exceptions.RequestException as e:
            logger.error(f"Cloud Streaming request error: {e}")
            yield f"\n[LLM Error: Request failed - {str(e)}]"

        try:
            response = requests.post(url, json=payload, stream=True, timeout=self.timeout)
            response.raise_for_status()

            for line in response.iter_lines():
                if line:
                    line_str = line.decode("utf-8").strip()
                    if line_str.startswith("data: "):
                        data_content = line_str[6:]
                        if data_content == "[DONE]":
                            break
                        try:
                            data_json = json.loads(data_content)
                            delta = data_json["choices"][0]["delta"]
                            if "content" in delta:
                                yield delta["content"]
                        except json.JSONDecodeError:
                            continue
        except requests.exceptions.RequestException as e:
            logger.error(f"OpenAI Streaming request error: {e}")
            yield f"\n[LLM Error: Request failed - {str(e)}]"