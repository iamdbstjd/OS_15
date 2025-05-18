from pydantic import BaseSettings
from dotenv import load_dotenv
import os

# .env 파일 로드
load_dotenv(dotenv_path=os.path.join(os.path.dirname(__file__), '../../.env'))

class Settings(BaseSettings):
    azure_speech_key: str
    azure_region: str
    # 필요한 다른 설정도 추가 가능
    class Config:
        env_file = ".env"  # 환경변수 파일 이름

settings = Settings()
