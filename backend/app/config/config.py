from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import DirectoryPath, Field, SecretStr
from functools import lru_cache
from pathlib import Path

class AppConfig(BaseSettings):
    app_name: str
    base_url:str
    database_url: SecretStr
    secret_key: SecretStr
    algorithms: str
    ACCESS_TOKEN_EXPIRE_MINUTE: int
    redis_url:str
    redis_port:int
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

APP_DIR=Path(__file__).resolve().parent.parent


class Notification_config(BaseSettings):
    MAIL_USERNAME: str
    MAIL_PASSWORD: str
    MAIL_FROM: str
    MAIL_FROM_NAME: str
    MAIL_SERVER: str
    MAIL_PORT: int
    MAIL_STARTTLS: bool = True
    MAIL_SSL_TLS: bool = False
    USE_CREDENTIALS: bool = True
    VALIDATE_CERTS: bool = True
    TEMPLATE_FOLDER:DirectoryPath=APP_DIR/"templates/emails"
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

class Ai_config(BaseSettings):
    GEMINI_API_KEY:SecretStr
    SYSTEM_INTRUCTION:str= """You are the assistant inside an Expense Tracker application.
Your ONLY job is to help users with:
- Adding, viewing, or updating their expenses and debts/settlements
- Summarizing or explaining their spending data
- Answering questions about how to use this app's features
- General practical advice specifically about budgeting, expense tracking, or debt management

You must NOT answer questions unrelated to these topics: general knowledge, current events, coding help, other apps, or anything outside personal finance and this application's features.
If the user asks something outside this scope, politely decline and redirect them. For example: I'm here to help with your expenses and budgeting, I can't help with that, but feel free to ask me about your spending!
"""
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")


@lru_cache
def get_config():
    return AppConfig()


@lru_cache
def mail_config():
    return Notification_config()

@lru_cache 
def ai_config():
    return Ai_config()
