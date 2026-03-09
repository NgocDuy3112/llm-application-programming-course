from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file="../.env", strict=False)
    GROQ_API_KEY: str

    def __post_init__(self):
        if not self.GROQ_API_KEY:
            raise ValueError("GROQ_API_KEY is required")


settings = Settings()