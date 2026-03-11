from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    mongodb_uri: str
    db_name: str
    groq_api_key: str

    class Config:
        env_file = ".env"

settings = Settings()