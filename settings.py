import os
from functools import lru_cache
from pydantic import BaseSettings


class Settings(BaseSettings):
    app_name: str = 'Boilerplate'
    admin_email: str = 'admin@admin.com'

    secret_key: str = 'bPVisLCKKyDIkIBVpWIukimDvyxGxVnHoszVijcZwcOLOMAaDeApkyHZuRVWlTHh'
    algorithm: str = 'HS256'
    jwt_header: str = 'Bearer'
    access_token_expire_minutes: int = 36000
    refresh_token_expire_days: int = 30

    db_host: str = os.getenv('DB_HOST')
    db_port: str = os.getenv('DB_PORT')
    db_database: str = os.getenv('DB_DATABASE')
    db_database_test: str = os.getenv('DB_DATABASE_TEST')
    db_username: str = os.getenv('DB_USERNAME')
    db_password: str = os.getenv('DB_PASSWORD')
    db_url: str = f'postgresql+asyncpg://{db_username}:{db_password}' \
                  f'@{db_host}:{db_port}/{db_database}'
    test_db_url: str = f'postgresql://{db_username}:{db_password}' \
                       f'@{db_host}:{db_port}/{db_database_test}'

    @property
    def alembic_db_url(self) -> str:
        return self.db_url.replace('+asyncpg', '')

    s3_key: str = os.getenv('S3_KEY')
    s3_secret: str = os.getenv('S3_SECRET')
    s3_bucket: str = os.getenv('S3_BUCKET')
    s3_region: str = os.getenv('S3_REGION')

    class Config:
        env_file = ".env"


@lru_cache
def get_settings() -> Settings:
    settings = Settings()
    return settings
