"""
LLM Client - Unified interface for calling LLMs from multiple backends.

Supports OpenAI, Anthropic, and HuggingFace backends with automatic
configuration from environment variables or config files.
"""

import os
import json
import re
from typing import Optional, Dict, Any
from pathlib import Path


class LLMClient:
    """
    Unified client for calling LLMs from multiple backends.

    Usage:
        client = LLMClient(agent_name="FinanceAgent")
        response = client.call(prompt="Analyze AAPL's P/E ratio trend", max_tokens=1000)
    """

    def __init__(self, agent_name: str = "Agent", backend: Optional[str] = None):
        self.agent_name = agent_name
        self.backend = backend or os.environ.get("LLM_BACKEND", "openai")
        self._load_config()

        if self.backend == "anthropic":
            self._init_anthropic()
        elif self.backend == "openai":
            self._init_openai()
        elif self.backend == "huggingface":
            self._init_huggingface()

    def _load_config(self):
        self.anthropic_key = os.environ.get("ANTHROPIC_API_KEY")
        self.openai_key = os.environ.get("OPENAI_API_KEY")
        self.hf_key = os.environ.get("HF_API_KEY") or os.environ.get("HUGGINGFACE_API_KEY")
        self.hf_model = os.environ.get("HF_MODEL", "moonshotai/Kimi-K2.5")
        self.hf_endpoint = os.environ.get("HF_ENDPOINT")
        self.anthropic_model = os.environ.get("ANTHROPIC_MODEL", "claude-sonnet-4-20250514")
        self.openai_model = os.environ.get("OPENAI_MODEL", "gpt-4o")
        self.openai_base_url = os.environ.get("OPENAI_BASE_URL")
        timeout_env = os.environ.get("LLM_TIMEOUT")
        self.timeout = int(timeout_env) if timeout_env else 180

        config_file = Path.home() / ".businessclaw" / "llm_config.json"
        if config_file.exists():
            try:
                with open(config_file) as f:
                    config = json.load(f)
                    self.backend = config.get("backend", self.backend)
                    self.anthropic_key = config.get("anthropic_api_key", self.anthropic_key)
                    self.openai_key = config.get("openai_api_key", self.openai_key)
                    self.hf_key = config.get("hf_api_key", self.hf_key)
                    self.anthropic_model = config.get("anthropic_model", self.anthropic_model)
                    self.openai_model = config.get("openai_model", self.openai_model)
                    self.openai_base_url = config.get("openai_base_url", self.openai_base_url)
                    if "timeout" in config:
                        self.timeout = int(config["timeout"])
            except Exception:
                pass

    def _init_anthropic(self):
        try:
            import anthropic
            if not self.anthropic_key:
                raise ValueError("ANTHROPIC_API_KEY not set")
            self.anthropic_client = anthropic.Anthropic(api_key=self.anthropic_key)
        except ImportError:
            raise ImportError("anthropic package not installed. Run: pip install anthropic")

    def _init_openai(self):
        try:
            import openai
            if not self.openai_key:
                raise ValueError("OPENAI_API_KEY not set")
            kwargs = {"api_key": self.openai_key}
            if self.openai_base_url:
                kwargs["base_url"] = self.openai_base_url
            self.openai_client = openai.OpenAI(**kwargs)
        except ImportError:
            raise ImportError("openai package not installed. Run: pip install openai")

    def _init_huggingface(self):
        try:
            from huggingface_hub import InferenceClient
            hf_timeout = self.timeout
            if self.hf_endpoint:
                self.hf_client = InferenceClient(base_url=self.hf_endpoint, timeout=hf_timeout)
            else:
                if not self.hf_key:
                    print("Warning: HF_API_KEY not set. Using public Inference API (rate limited).")
                self.hf_client = InferenceClient(
                    model=self.hf_model, token=self.hf_key, timeout=hf_timeout
                )
        except ImportError:
            raise ImportError("huggingface_hub not installed. Run: pip install huggingface_hub")

    def call(
        self,
        prompt: str,
        max_tokens: int = 1000,
        temperature: float = 1.0,
        timeout: Optional[int] = None,
        session_id: Optional[str] = None,
    ) -> str:
        if self.backend == "anthropic":
            return self._call_anthropic(prompt, max_tokens, temperature)
        elif self.backend == "openai":
            return self._call_openai(prompt, max_tokens, temperature)
        elif self.backend == "huggingface":
            return self._call_huggingface(prompt, max_tokens, temperature)
        else:
            raise ValueError(f"Unknown backend: {self.backend}")

    def _call_anthropic(self, prompt: str, max_tokens: int, temperature: float) -> str:
        try:
            message = self.anthropic_client.messages.create(
                model=self.anthropic_model,
                max_tokens=max_tokens,
                temperature=temperature,
                messages=[{"role": "user", "content": prompt}],
            )
            return message.content[0].text
        except Exception as e:
            print(f"Anthropic API error: {e}")
            return ""

    def _call_openai(self, prompt: str, max_tokens: int, temperature: float) -> str:
        def _wants_max_completion_tokens(model: str) -> bool:
            m = (model or "").strip().lower()
            if m.startswith("gpt-5"):
                return True
            if re.match(r"^o\d", m):
                return True
            return False

        def _extract_text(resp) -> str:
            try:
                return resp.choices[0].message.content or ""
            except Exception:
                return ""

        base_kwargs = {
            "model": self.openai_model,
            "temperature": temperature,
            "messages": [{"role": "user", "content": prompt}],
        }

        try:
            kwargs = dict(base_kwargs)
            if _wants_max_completion_tokens(self.openai_model):
                kwargs["max_completion_tokens"] = int(max_tokens)
            else:
                kwargs["max_tokens"] = int(max_tokens)
            response = self.openai_client.chat.completions.create(**kwargs)
            return _extract_text(response)
        except Exception as e:
            msg = str(e)
            try:
                if "max_tokens" in msg and "max_completion_tokens" in msg:
                    kwargs = dict(base_kwargs)
                    kwargs["max_completion_tokens"] = int(max_tokens)
                    response = self.openai_client.chat.completions.create(**kwargs)
                    return _extract_text(response)
            except Exception:
                pass
            print(f"OpenAI API error: {e}")
            return ""

    def _call_huggingface(self, prompt: str, max_tokens: int, temperature: float) -> str:
        try:
            try:
                response = self.hf_client.text_generation(
                    prompt, max_new_tokens=max_tokens, temperature=temperature, return_full_text=False
                )
                return str(response) if response else ""
            except ValueError as ve:
                if "not supported for task" not in str(ve):
                    raise

            try:
                response = self.hf_client.chat_completion(
                    messages=[{"role": "user", "content": prompt}],
                    max_tokens=max_tokens,
                    temperature=temperature,
                )
                if hasattr(response, "choices") and len(response.choices) > 0:
                    return response.choices[0].message.content or ""
                elif isinstance(response, dict) and "choices" in response:
                    return response["choices"][0]["message"]["content"]
                return str(response) if response else ""
            except Exception:
                raise
        except Exception as e:
            print(f"Hugging Face API error: {e}")
            return ""


_client: Optional[LLMClient] = None


def get_llm_client(agent_name: str = "Agent", backend: Optional[str] = None) -> LLMClient:
    global _client
    if _client is None or _client.agent_name != agent_name or (backend and _client.backend != backend):
        _client = LLMClient(agent_name=agent_name, backend=backend)
    return _client
