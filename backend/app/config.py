"""
Cadê o Lixeiro? v2.0 — Backend Configuration

Carrega variáveis de ambiente via Pydantic Settings.
"""

from pydantic_settings import BaseSettings
from functools import lru_cache


class Settings(BaseSettings):
    """Configurações do backend carregadas de variáveis de ambiente."""

    # --- Banco de Dados ---
    DATABASE_URL: str = "postgresql+asyncpg://postgres:postgres@localhost:54322/postgres"

    # --- Supabase ---
    SUPABASE_URL: str = "https://your-project.supabase.co"
    SUPABASE_SERVICE_KEY: str = "your-service-role-key"
    SUPABASE_ANON_KEY: str = "your-anon-key"

    # --- JWT ---
    JWT_SECRET: str = "your-jwt-secret"
    JWT_ALGORITHM: str = "HS256"

    # --- CORS ---
    CORS_ORIGINS: list[str] = [
        "http://localhost:5173",
        "http://localhost:5174",
        "http://localhost:4173",
    ]

    # --- VAPID (Push Notifications) ---
    VAPID_PRIVATE_KEY: str = ""
    VAPID_PUBLIC_KEY: str = ""
    VAPID_CLAIMS_EMAIL: str = "mailto:contato@cadeolixeiro.com"

    # --- App ---
    APP_NAME: str = "Cadê o Lixeiro? API"
    APP_VERSION: str = "2.0.0"
    DEBUG: bool = True

    model_config = {
        "env_file": ".env",
        "env_file_encoding": "utf-8",
        "case_sensitive": True,
    }


@lru_cache
def get_settings() -> Settings:
    """Retorna instância cacheada das configurações."""
    return Settings()
