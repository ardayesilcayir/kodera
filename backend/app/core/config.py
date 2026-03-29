from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    SUPABASE_URL: str = ""
    SUPABASE_KEY: str = ""
    HF_TOKEN: str = ""

    class Config:
        env_file = ".env"
        extra = "ignore"

settings = Settings()
