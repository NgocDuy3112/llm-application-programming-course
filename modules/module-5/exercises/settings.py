from pydantic_settings import BaseSettings, SettingsConfigDict



class Settings(BaseSettings):
    # TODO 1.1: Khai báo API Key cho Groq (đọc từ biến môi trường GROQ_API_KEY)
    GROQ_API_KEY: str
    
    # TODO 1.2: Cấu hình Pydantic để đọc từ file .env và bỏ qua các biến thừa
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")



settings = Settings()
