from pydantic_settings import BaseSettings
from functools import lru_cache


class Settings(BaseSettings):
    app_name: str = "Trop-Med"
    app_locale: str = "fr"
    debug: bool = False

    mongodb_uri: str = "mongodb://localhost:27017/tropmed"
    jwt_secret: str = "change-me-in-production"
    jwt_algorithm: str = "HS256"
    jwt_access_expire_minutes: int = 15
    jwt_refresh_expire_days: int = 7

    aws_s3_bucket: str = "tropmed-files-local"
    aws_region: str = "us-east-1"
    aws_endpoint_url: str | None = None  # LocalStack override

    ai_inference_url: str = "http://ai-mock:8080"
    redis_url: str = "redis://localhost:6379"
    sqs_task_queue_url: str = ""
    sns_notification_topic: str = ""
    fhir_base_url: str = ""

    rate_limit_patient: int = 60
    rate_limit_clinician: int = 300
    rate_limit_admin: int = 600

    model_config = {"env_file": ".env", "extra": "ignore"}


@lru_cache
def get_settings() -> Settings:
    return Settings()
