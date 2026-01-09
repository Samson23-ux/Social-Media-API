from pydantic_settings import BaseSettings


# Settings class that contains core application configurations
# inheriting from Pydantic BaseSettings
class Settings(BaseSettings):
    ENVIROMENT: str

    # API Info
    API_VERSION: str = '1.0.0'
    API_VERSION_PREFIX: str = 'api/v1/'
    API_TITLE: str = 'Mini Social Media API'
    API_DESCRIPTION: str = 'A REST API for a mini social media app'

    # DB credentials
    DATABASE_URL: str
    DATABASE_USERNAME: str
    DATABASE_PASSWORD: str

    # Argon2 hasher
    ARGON2_PEPPER: str

    #JWT
    JWT_ALGORITHM: str
    ACCESS_TOKEN_SECRET_KEY: str
    ACCESS_TOKEN_EXPIRE_TIME: int
    REFRESH_TOKEN_SECRET_KEY: str
    REFRESH_TOKEN_EXPIRE_TIME: int

    class Config:
        env_file: str = '.env'
        env_file_encoding = 'utf-8'


settings = Settings()
