"""Configuraciones de la aplicación."""
import os
from dotenv import load_dotenv

load_dotenv()


class Settings:
    """Base settings."""
    PROJECT_NAME: str = "My FastAPI Project"
    DB_URL: str
    PAGE_LIMIT: int = 10
    PAGE_OFFSET: int = 0
    SMTP_SERVER: str = os.getenv("SMTP_SERVER")
    SMTP_PORT: int = os.getenv("SMTP_PORT")
    FROM_EMAIL: str = os.getenv("FROM_EMAIL")
    FROM_EMAIL_NAME: str = os.getenv("FROM_EMAIL_NAME")

    @property
    def DB_URL(self) -> str:
        """Constructs the database URL from environment variables."""
        db_host = os.getenv("DB_HOST", "localhost")
        db_port = os.getenv("DB_PORT", "5432")
        db_name = os.getenv("DB_NAME", "mydatabase")
        db_user = os.getenv("DB_USER", "user")
        db_pass = os.getenv("DB_PASS", "password")
        if db_host.startswith("sqlite"):
            return f"sqlite:///{os.getenv('DB_NAME_LOCAL', 'test.db')}"
        return f"postgresql://{db_user}:{db_pass}@{db_host}:{db_port}/{db_name}"

settings = Settings()
