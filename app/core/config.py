from pydantic_settings import BaseSettings, SettingsConfigDict


# Settings class that contains core application configurations
# inheriting from Pydantic BaseSettings
class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file='.env', env_file_encoding='utf-8')

    ENVIROMENT: str

    # API Info
    API_VERSION: str = '1.0.0'
    API_VERSION_PREFIX: str = '/api/v1'
    API_TITLE: str = 'Social Media API'
    API_DESCRIPTION: str = 'A REST API for a mini social media app'

    # DB URL
    DATABASE_URL: str
    WORKER_DATABASE_URL: str

    #Broker URI
    BROKER_URL: str

    # Argon2 hasher
    ARGON2_PEPPER: str

    #JWT
    JWT_ALGORITHM: str
    ACCESS_TOKEN_SECRET_KEY: str
    ACCESS_TOKEN_EXPIRE_TIME: int
    REFRESH_TOKEN_SECRET_KEY: str
    REFRESH_TOKEN_EXPIRE_TIME: int

    #Admin login credentials
    ADMIN_DISPLAY_NAME: str
    ADMIN_USERNAME: str
    ADMIN_EMAIL: str
    ADMIN_PASSWORD: str
    ADMIN_DOB: str
    ADMIN_NATIONALITY: str
    ADMIN_BIO: str

    #Image path
    PROFILE_IMAGE_PATH: str
    POST_IMAGE_PATH: str

    # Sentry dsn
    SENTRY_SDK_DSN: str


settings = Settings()
