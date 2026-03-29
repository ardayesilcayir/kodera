from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    SUPABASE_URL: str = ""
    SUPABASE_KEY: str = ""
    HF_TOKEN: str = ""
    # true/1 → NLPService LLM çıkarımı yapmaz (sadece metin placeholder döner)
    DISABLE_LLM: bool = False

    class Config:
        env_file = ".env"
        extra = "ignore"

settings = Settings()
