import os
from dotenv import load_dotenv

load_dotenv()


def get_env(key: str, default: str = None, required: bool = False) -> str:
    value = os.getenv(key, default)
    if required and not value:
        raise EnvironmentError(f"Environment variable {key} is required")
    return value

class Settings:
    APP_NAME: str = get_env("APP_NAME", "SoundBot API")
    VERSION: str = get_env("APP_VERSION", "1.0.0")
    SPOTIFY_CLIENT_ID: str = get_env("SPOTIFY_CLIENT_ID", required=True)
    SPOTIFY_CLIENT_SECRET: str = get_env("SPOTIFY_CLIENT_SECRET", required=True)
    SPOTIFY_REDIRECT_URI: str = get_env("SPOTIFY_REDIRECT_URI", "http://localhost:8000/auth/spotify/callback")
    GROQ_API_KEY: str = get_env("GROQ_API_KEY", required=True)
    MEM_LIMIT: int = int(get_env("SOUNDBOT_MEM_LIMIT", "30"))
    CORS_ORIGINS: str = get_env("CORS_ALLOWED_ORIGINS", "*")
    REDIS_URL: str = get_env("REDIS_URL", "redis://localhost:6379")


settings = Settings()