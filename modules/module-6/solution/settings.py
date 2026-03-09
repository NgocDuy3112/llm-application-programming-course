from pathlib import Path
import os
from typing import Any

from pydantic_settings import BaseSettings, SettingsConfigDict
import yaml


ROOT_DIR = Path(__file__).resolve().parent.parent
MODELS_YAML_PATH = ROOT_DIR / "models.yaml"
ENV_FILE_PATH = ROOT_DIR / ".env"


def _file_mtime_ns(path: Path) -> int | None:
    """Return file mtime in ns, or None when file is unavailable."""
    try:
        return path.stat().st_mtime_ns
    except OSError:
        return None


def _read_models_config(path: Path) -> list[dict[str, Any]]:
    """Read models.yaml using the current schema: top-level provider list."""
    try:
        with open(path, "r", encoding="utf-8") as file:
            data = yaml.safe_load(file)
    except Exception as exc:
        raise ValueError(f"Failed to read models config: {path}") from exc

    if data is None:
        return []

    if isinstance(data, list):
        return [item for item in data if isinstance(item, dict)]

    raise ValueError(
        "models.yaml must be a top-level list of providers"
    )


def _extract_provider_map(providers: list[dict[str, Any]]) -> dict[str, dict[str, Any]]:
    """Convert provider list into a {name: provider_config} map."""
    provider_map: dict[str, dict[str, Any]] = {}
    for provider in providers:
        name = provider.get("name")
        if isinstance(name, str) and name:
            provider_map[name] = provider
    return provider_map


def load_models_config() -> list[dict[str, Any]]:
    """Return full models configuration from models.yaml."""
    return LLMProvider.models_config()


def _load_env_file_values(env_path: Path) -> dict[str, str]:
    """Parse .env file into a key/value map for dynamic API key lookups."""
    if not env_path.exists():
        return {}

    values: dict[str, str] = {}
    for raw_line in env_path.read_text(encoding="utf-8").splitlines():
        line = raw_line.strip()
        if not line or line.startswith("#"):
            continue
        if line.startswith("export "):
            line = line[len("export "):].strip()
        if "=" not in line:
            continue

        key, value = line.split("=", 1)
        key = key.strip()
        value = value.strip().strip('"').strip("'")
        if key:
            values[key] = value

    return values


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=str(ENV_FILE_PATH), strict=False)
    GROQ_API_KEY: str | None = None
    TAVILY_API_KEY: str | None = None
    OLLAMA_API_KEY: str | None = None

    def get_api_key(self, env_var_name: str | None) -> str | None:
        """Resolve API key value from env/.env by env var name."""
        if not env_var_name:
            return None

        candidates = [
            os.getenv(env_var_name),
            getattr(self, env_var_name, None),
            (self.model_extra or {}).get(env_var_name),
            _load_env_file_values(ENV_FILE_PATH).get(env_var_name),
        ]
        for value in candidates:
            if isinstance(value, str) and value.strip():
                return value.strip()
        return None


class LLMProvider:
    """Dynamic LLM provider loaded from models.yaml.

    Each provider has:
        - name: Provider display name
        - api_key: Optional env variable name for API key
        - default_models: List of available models
        - base_url: Optional base URL for API calls
    """

    _YAML_PATH = MODELS_YAML_PATH
    _raw_config: list[dict[str, Any]] = []
    _provider_map: dict[str, dict[str, Any]] = {}
    _cache_mtime_ns: int | None = None
    _cache_ready: bool = False
    _instances: dict[str, "LLMProvider"] = {}

    @classmethod
    def _refresh_cache_if_needed(cls) -> None:
        """Reload models config only when models.yaml changes."""
        mtime_ns = _file_mtime_ns(cls._YAML_PATH)
        if cls._cache_ready and cls._cache_mtime_ns == mtime_ns:
            return

        raw_config = _read_models_config(cls._YAML_PATH)
        provider_map = _extract_provider_map(raw_config)

        cls._raw_config = raw_config
        cls._provider_map = provider_map
        cls._cache_mtime_ns = mtime_ns
        cls._cache_ready = True
        cls._instances = {}

    @classmethod
    def _load_configs(cls) -> dict[str, dict[str, Any]]:
        """Return provider map loaded from models.yaml."""
        cls._refresh_cache_if_needed()
        return cls._provider_map

    @classmethod
    def models_config(cls) -> list[dict[str, Any]]:
        """Return the full raw config loaded from models.yaml."""
        cls._refresh_cache_if_needed()
        return cls._raw_config

    def __new__(cls, name: str = None):
        """Get or create provider instance by name."""
        configs = cls._load_configs()
        
        # Return first provider as default if no name provided
        if name is None:
            name = next(iter(configs.keys()), None)
            if name is None:
                raise ValueError("No providers available in models.yaml")
        
        if name in cls._instances:
            return cls._instances[name]

        if name not in configs:
            raise ValueError(f"Unknown provider: {name}. Available: {list(configs.keys())}")

        instance = super().__new__(cls)
        instance._name = name
        instance._api_key = configs[name].get("api_key")
        instance._default_models = configs[name].get("default_models", [])
        instance._base_url = configs[name].get("base_url")
        cls._instances[name] = instance
        return instance

    @property
    def value(self) -> str:
        """Return the provider display name."""
        return self._name

    @property
    def api_key(self) -> str | None:
        """Return the env variable name used for API key."""
        return self._api_key

    @property
    def default_models(self) -> list[str]:
        """Return the list of default models for this provider."""
        return self._default_models

    @property
    def base_url(self) -> str | None:
        """Optional base URL to use for API calls to this provider."""
        return self._base_url

    def __str__(self) -> str:
        return self._name

    def __repr__(self) -> str:
        return f"LLMProvider({self._name!r})"

    def __eq__(self, other) -> bool:
        if isinstance(other, LLMProvider):
            return self._name == other._name
        if isinstance(other, str):
            return self._name == other
        return False

    def __hash__(self) -> int:
        return hash(self._name)

    @classmethod
    def all(cls) -> list["LLMProvider"]:
        """Return all available providers."""
        return [cls(name) for name in cls._load_configs().keys()]

    @classmethod
    def values(cls) -> list[str]:
        """Return all provider names."""
        return list(cls._load_configs().keys())