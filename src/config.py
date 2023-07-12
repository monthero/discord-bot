from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    APP_ID: str
    DISCORD_SERVER_NAME: str
    DISCORD_TOKEN: str
    GOOGLE_PROJECT_ID: str
    PUBLIC_KEY: str

    class Config:
        env_file = ".env"
        case_sensitive = True
