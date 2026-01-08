from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    # API Info
    API_VERSION: str = '1.0.0'
    API_VERSION_PREFIX: str = 'api/v1/'
    API_TITLE: str = 'Mini Social Media API'
    API_DESCRIPTION: str = 'A REST API for a mini social media app'

    # DB credentials
    DATABASE_URL: str
    DATABASE_USERNAME: str
    DATABASE_PASSWORD: str

    class Config:
        env_file: str = '.env'
        env_file_encoding = 'utf-8'


settings: Settings = Settings()
