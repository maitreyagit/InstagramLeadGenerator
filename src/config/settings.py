import os
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    concurrency: int = 3
    timeout: int = 30000  # milliseconds
    retries: int = 3
    min_delay: int = 5
    max_delay: int = 15

    
    output_folder: str = "OutputData"
    export_format: str = "json"  # json, csv, excel
    
    proxy_list_file: str | None = None

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        extra = "ignore"

settings = Settings()
