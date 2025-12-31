"""ML Service configuration."""

from functools import lru_cache
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        case_sensitive=True,
        extra="ignore"
    )
    
    APP_NAME: str = "SmartRetail-AI ML Service"
    APP_VERSION: str = "1.0.0"
    APP_ENV: str = "development"
    
    # Model paths
    MODEL_PATH: str = "models"
    RECOMMENDATION_MODEL_PATH: str = "models/recommendation"
    SEGMENTATION_MODEL_PATH: str = "models/segmentation"
    FORECASTING_MODEL_PATH: str = "models/forecasting"
    
    # MLflow
    MLFLOW_TRACKING_URI: str = "http://localhost:5000"
    MLFLOW_EXPERIMENT_NAME: str = "smartretail"
    
    # Database
    DATABASE_URL: str = "postgresql+asyncpg://postgres:postgres@localhost:5432/smartretail"
    REDIS_URL: str = "redis://localhost:6379/0"
    
    # Model parameters
    RECOMMENDATION_N_FACTORS: int = 50
    SEGMENTATION_N_CLUSTERS: int = 6
    FORECAST_HORIZON_DAYS: int = 30


@lru_cache()
def get_settings() -> Settings:
    return Settings()


settings = get_settings()
