from pydantic_settings import BaseSettings, SettingsConfigDict
from enum import Enum


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file="../.env", strict=False)
    GROQ_API_KEY: str


class LLMProvider(str, Enum):
    """Enum of supported LLM providers with per-member metadata.

    Each member's .value is the provider name (string). Metadata attached to each
    member includes:
        - needs_api_key: bool
        - default_models: list[str]
        - base_url: Optional[str]  # base URL to use when constructing clients
    """
    GROQ = (
        "Groq",
        True,
        [
            "openai/gpt-oss-20b", 
            "openai/gpt-oss-safeguard-20b", 
            "openai/gpt-oss-120b",
            "moonshotai/kimi-k2-instruct-0905",
            "meta-llama/llama-4-scout-17b-16e-instruct",
        ],
        "https://api.groq.com/openai/v1",
    )
    OPENAI = (
        "OpenAI",
        True,
        ["gpt-4o", "gpt-3.5-turbo"],
        None,
    )
    OLLAMA = (
        "Ollama",
        False,
        ["qwen3:4b", "qwen3:1.7b", "gemma3:1b"],
        "http://localhost:11434/v1",
    )

    def __new__(cls, value: str, needs_api_key: bool, default_models: list[str], base_url: str | None = None):
        obj = str.__new__(cls, value)
        obj._value_ = value
        obj._needs_api_key = needs_api_key
        obj._default_models = default_models
        obj._base_url = base_url
        return obj

    @property
    def needs_api_key(self) -> bool:
        """Whether this provider requires an API key."""
        return self._needs_api_key

    @property
    def default_models(self) -> list[str]:
        """Return the list of default models for this provider."""
        return self._default_models

    @property
    def base_url(self) -> str | None:
        """Optional base URL to use for API calls to this provider."""
        return self._base_url