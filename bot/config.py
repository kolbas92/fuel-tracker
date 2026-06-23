# bot/config.py
from pydantic_settings import BaseSettings

class BotSettings(BaseSettings):
    bot_token: str
    api_url: str = "http://localhost:8000"
    api_key: str = "changeme"
    frontend_url: str = "http://localhost:5173"

    model_config = {"env_file": ".env"}

settings = BotSettings()
