from pydantic_settings import BaseSettings, SettingsConfigDict
from typing import Optional

class Settings(BaseSettings):
    PROJECT_NAME: str = "PaperAmbulance"
    API_V1_STR: str = "/api/v1"
    
    SECRET_KEY: str = "local_secret_key"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24 * 8  # 8 days
    
    DATABASE_URL: str
    GOOGLE_API_KEY: str
    
    # Neon Auth / Clerk
    CLERK_FRONTEND_API: str
    NEON_AUTH_JWKS_URL: str

    model_config = SettingsConfigDict(
        env_file=".env",
        case_sensitive=True,
    )

settings = Settings()
