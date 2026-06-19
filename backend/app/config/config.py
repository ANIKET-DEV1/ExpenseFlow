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



@lru_cache
def get_config():
    return AppConfig()


@lru_cache
def mail_config():
    return Notification_config()