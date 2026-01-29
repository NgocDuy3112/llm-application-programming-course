from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file="./secrets/.env", strict=False)
    API_KEY: str


settings = Settings()


MODELS_LIST = {
    # "OpenAI": ["SeaLLMs/SeaLLMs-v3-1.5B"],
    "Groq": ["openai/gpt-oss-20b", "openai/gpt-oss-safeguard-20b", "openai/gpt-oss-120b"],
    "Gemini": ["gemini-3-pro", "gemini-3-flash", "gemini-2.5-pro", "gemini-2.5-flash"],
    "Ollama": ["qwen3:4b", "gemma3:1b"],
    # "Huggingface": ["meta-llama/Llama-2-7b-chat-hf", "meta-llama/Llama-2-13b-chat-hf"]
}


NEED_API_KEY_PROVIDERS = ["OpenAI", "Groq", "Gemini"]