# bot/config.py
from pydantic_settings import BaseSettings

class BotSettings(BaseSettings):
    bot_token: str
    api_url: str = "http://localhost:8000"
    api_key: str = "changeme"
    frontend_url: str = "http://localhost:5173"
    bot_username: str = "zapravka_gde_bot"
    channel_url: str = ""  # e.g. https://t.me/your_channel; empty hides the button

    model_config = {"env_file": ".env", "extra": "ignore"}

settings = BotSettings()
