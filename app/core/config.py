from pydantic_settings import BaseSettings, SettingsConfigDict


# Settings class that contains core application configurations
# inheriting from Pydantic BaseSettings
class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file='.env', env_file_encoding='utf-8')

    ENVIROMENT: str

    # Fastapi Port
    API_PORT: str

    # API Info
    API_VERSION: str = '1.0.0'
    API_VERSION_PREFIX: str = '/api/v1'
    API_TITLE: str = 'Social Media API'
    API_DESCRIPTION: str = 'A REST API for a mini social media app'

    # DB URL
    DATABASE_URL: str
    WORKER_DATABASE_URL: str

    #API DB Credentials
    API_DB: str
    API_DB_USER: str
    API_DB_PASSWORD: str
    API_DB_PORT: str

    #Test DB Credentials
    TEST_DB: str
    TEST_DB_USER: str
    TEST_DB_PASSWORD: str
    TEST_DB_PORT: str

    # TEST DB URL
    TEST_DATABASE_URL: str

    # Broker Credentials
    BROKER_USER: str
    BROKER_PASSWORD: str
    BROKER_VHOST: str
    BROKER_PORT: str
    BROKER_PLUGIN_PORT: str

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
