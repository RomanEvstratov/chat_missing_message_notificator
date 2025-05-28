import logging
from pathlib import Path

from pydantic import SecretStr
from pydantic_settings import BaseSettings, SettingsConfigDict

BASE_DIR = Path(__file__)
ENV_FILE_PATH = BASE_DIR.parent.parent / ".env"


class DefaultSettings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=ENV_FILE_PATH,
        extra="ignore",
    )

class DatabaseSettings(DefaultSettings):
    PROTOCOL: str = "postgresql+asyncpg"
    POSTGRES_DB: str = "notificator"
    POSTGRES_USER: str = "postgres"
    POSTGRES_PASSWORD: SecretStr = SecretStr("postgres")
    DB_HOST: str = "localhost"
    DB_PORT: str = "5432"

    @property
    def db_domain(self) -> SecretStr:
        return SecretStr(
            f"{self.POSTGRES_USER}:"
            f"{self.POSTGRES_PASSWORD.get_secret_value()}@"
            f"{self.DB_HOST}:"
            f"{self.DB_PORT}/"
            f"{self.POSTGRES_DB}",
        )

    @property
    def sync_db_url(self) -> SecretStr:
        return SecretStr(f"postgresql://{self.db_domain.get_secret_value()}")

    @property
    def async_db_url(self) -> SecretStr:
        return SecretStr(
            f"{self.PROTOCOL}://{self.db_domain.get_secret_value()}",
        )


class TelegramSettings(DefaultSettings):
    TELEGRAM_API_ID: int
    TELEGRAM_API_HASH: str
    PHONE_NUMBER: SecretStr


class SlackSettings(DefaultSettings):
    SLACK_TOKEN: SecretStr
    SLACK_CHANNEL: str
    SLACK_NOTIFY_ABOUT_AUTH: str | None = None

class NotificatorSettings(DefaultSettings):
    TIME_TO_SLEEP: str
    TIME_TO_WOKE_UP: str
    TIME_BETWEEN_CHECK: int = 1800

class AuthSettings(DefaultSettings):
    ADMIN_USERNAME: str
    ADMIN_PASSWORD: SecretStr
    SECRET_KEY: SecretStr = SecretStr("secret")
    EXPIRE: int = 60
    ALGORITHM: str = "HS256"

class Settings(BaseSettings):
    DATABASE: DatabaseSettings = DatabaseSettings()
    TELEGRAM: TelegramSettings = TelegramSettings()
    SLACK: SlackSettings = SlackSettings()
    NOTIFICATOR: NotificatorSettings = NotificatorSettings()
    AUTH: AuthSettings = AuthSettings()

settings = Settings()
log = logging.getLogger("uvicorn")