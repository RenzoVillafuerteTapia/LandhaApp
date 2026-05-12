# Ruta: backend/app/config.py

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
    )

    # Database
    db_host: str = "localhost"
    db_port: int = 3306
    db_name: str = "landhaapp"
    db_user: str = "root"
    db_password: str = ""

    # JWT
    secret_key: str = "change_me"
    algorithm: str = "HS256"
    access_token_expire_minutes: int = 480

    # App
    app_name: str = "LandhaApp"
    debug: bool = False

    @property
    def database_url(self) -> str:
        return (
            f"mysql+pymysql://{self.db_user}:{self.db_password}"
            f"@{self.db_host}:{self.db_port}/{self.db_name}"
        )


settings = Settings()