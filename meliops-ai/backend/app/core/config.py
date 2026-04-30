from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    DATABASE_URL: str
    MELI_CLIENT_ID: str
    MELI_CLIENT_SECRET: str
    MELI_REDIRECT_URI: str
    JWT_SECRET_KEY: str
    ENCRYPTION_KEY: str

    class Config:
        env_file = ".env"

settings = Settings()
