from pydantic_settings import BaseSettings
from pydantic import ConfigDict


## Check environment variables if missing
class Settings(BaseSettings):
    model_config = ConfigDict(env_file=".env")

    DB_HOSTNAME: str
    DB_PORT: str
    DB_NAME: str
    DB_PASSWORD: str
    DB_USERNAME: str
    SECRET_KEY: str
    ALGORITHM: str
    ACCESS_TOKEN_EXPIRE_MINUTES: int

settings = Settings()
