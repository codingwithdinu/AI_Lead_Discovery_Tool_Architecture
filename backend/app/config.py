from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    app_name: str = "AI Lead Discovery & Intelligence API"
    environment: str = "development"
    database_url: str = "sqlite+aiosqlite:///./app.db"
    cors_origins: str = "http://localhost:3000"
    jwt_secret: str = "change-me-in-production"
    jwt_algorithm: str = "HS256"
    access_token_minutes: int = 60
    settings_config = SettingsConfigDict(env_file=".env", extra="ignore")

settings = Settings()
