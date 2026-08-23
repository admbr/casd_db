from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    database_url: str = "database_url"

    asaas_api_key: str = "asaas_api_key"
    asaas_base_url: str = "asaas_base_url"

    gmail_user: str = "gmail_user"
    gmail_password: str = "gmail_password"
    sender_name: str = "Financeiro Casd"

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8")


settings = Settings()
