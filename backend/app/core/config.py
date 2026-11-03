from typing import List, Optional
from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    PROJECT_NAME: str = "PULSAR AI"
    VERSION: str = "2.0.0"
    ENVIRONMENT: str = Field(default="production")
    DEBUG: bool = False
    
    # API & CORS
    API_V1_STR: str = "/api/v1"
    SECRET_KEY: str = Field(default="pulsar-super-secret-jwt-key-change-in-production-2026")
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24 * 7  # 7 days
    CORS_ORIGINS: List[str] = [
        "http://localhost:3000",
        "https://*.vercel.app",
        "https://pulsar-ai.vercel.app"
    ]

    # Supabase PostgreSQL
    DATABASE_URL: str = Field(
        default="postgresql+asyncpg://postgres:postgres@localhost:5432/postgres",
        description="Async PostgreSQL connection string"
    )
    DATABASE_SYNC_URL: Optional[str] = Field(
        default="postgresql://postgres:postgres@localhost:5432/postgres",
        description="Sync PostgreSQL connection string for migrations/workers"
    )
    SUPABASE_URL: Optional[str] = None
    SUPABASE_KEY: Optional[str] = None
    SUPABASE_SERVICE_ROLE_KEY: Optional[str] = None

    # Market Data
    PRIMARY_DATA_PROVIDER: str = "binance"
    FALLBACK_DATA_PROVIDER: str = "bybit"
    ACTIVE_PAIRS: List[str] = ["BTCUSDT", "ETHUSDT", "SOLUSDT", "BNBUSDT", "XRPUSDT", "DOGEUSDT", "ADAUSDT", "AVAXUSDT"]
    PRIORITY_PAIRS: List[str] = ["BTCUSDT", "ETHUSDT", "SOLUSDT"]
    TIMEFRAMES: List[str] = ["5m", "15m", "1h", "4h", "1d", "1w"]
    CANDLE_LIMIT_SCAN: int = 250
    REQUEST_TIMEOUT_SECONDS: int = 15

    # Signal Defaults
    MIN_CONFLUENCE_SCORE: float = 70.0
    MIN_RR_RATIO: float = 2.0
    DEFAULT_RISK_PERCENT: float = 1.0
    DEFAULT_STRATEGY: str = "sniper"
    SIGNAL_COOLDOWN_MINUTES: int = 30

    # Telegram
    TELEGRAM_BOT_TOKEN: Optional[str] = None
    TELEGRAM_CHAT_ID: Optional[str] = None
    TELEGRAM_ALERTS_ENABLED: bool = True

    # Cloud Scheduler / Worker
    SCAN_INTERVAL_SECONDS: int = 60
    WORKER_LOCK_TIMEOUT_SECONDS: int = 55
    DEMO_MODE_FALLBACK: bool = True

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=True,
        extra="ignore"
    )


settings = Settings()
