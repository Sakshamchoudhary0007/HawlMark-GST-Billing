from pathlib import Path
from functools import lru_cache
from urllib.parse import quote_plus
import socket
from pydantic import model_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application settings."""

    # Application
    APP_ENV: str = "development"
    APP_NAME: str = "GST Billing Application"
    DEBUG: bool = True

    # MySQL Database
    MYSQL_HOST: str = "localhost"
    MYSQL_PORT: int = 3306
    MYSQL_USER: str = "gst_billing_user"
    MYSQL_PASSWORD: str = "change_me_in_production"
    MYSQL_DATABASE: str = "gst_billing"

    # JWT Authentication
    JWT_SECRET_KEY: str = "change-this-to-a-secure-random-string-in-production"
    JWT_ALGORITHM: str = "HS256"
    JWT_ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    JWT_REFRESH_TOKEN_EXPIRE_DAYS: int = 7

    # CORS
    CORS_ORIGINS: str = "http://localhost:8000"

    # GST Provider
    GST_PROVIDER_TYPE: str = "mock"
    GST_PROVIDER_API_KEY: str = ""
    GST_PROVIDER_BASE_URL: str = ""

    model_config = SettingsConfigDict(
    env_file=Path(__file__).resolve().parents[2] / ".env",
    extra="ignore"
)

    @model_validator(mode="after")
    def auto_correct_mysql_config(self) -> "Settings":
        """Auto-correct common misconfigurations (e.g. USER=localhost or closed port 3307)."""
        if self.MYSQL_USER == "localhost":
            self.MYSQL_USER = "root"
        if self.MYSQL_PORT == 3307:
            try:
                s = socket.socket()
                s.settimeout(0.3)
                res = s.connect_ex((self.MYSQL_HOST, 3307))
                s.close()
                if res != 0:
                    self.MYSQL_PORT = 3306
            except Exception:
                self.MYSQL_PORT = 3306
        return self

    @property
    def database_url(self) -> str:
        """Computed property for the MySQL database URL."""
        encoded_password = quote_plus(self.MYSQL_PASSWORD)
        return (
            f"mysql+pymysql://{self.MYSQL_USER}:{encoded_password}"
            f"@{self.MYSQL_HOST}:{self.MYSQL_PORT}/{self.MYSQL_DATABASE}?charset=utf8mb4"
        )


@lru_cache()
def get_settings() -> Settings:
    """Return application settings."""
    return Settings()
