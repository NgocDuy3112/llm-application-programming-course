from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file="./secrets/.env", strict=False)
    API_KEY: str


settings = Settings()


MODELS_LIST = {
    # TODO #2: Add more providers by uncommenting the line below and define your models
    # Solution: "OpenAI": ["gpt-4o", "gpt-3.5-turbo"],
    # "OpenAI": ["gpt-4o", "gpt-3.5-turbo"],
    # "Groq": ["openai/gpt-oss-20b", "openai/gpt-oss-safeguard-20b", "openai/gpt-oss-120b"],
    # "Gemini": ["gemini-3-pro", "gemini-3-flash", "gemini-2.5-pro", "gemini-2.5-flash"],
    # "Ollama": ["qwen3:4b", "qwen3:1.7b", "gemma3:1b"],
}


NEED_API_KEY_PROVIDERS = ["OpenAI", "Groq", "Gemini"]