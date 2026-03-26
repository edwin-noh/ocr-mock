# config.py
import os
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    # OpenShift 환경변수에서 값을 읽어옴 (대소문자 구분 없음)
    # 환경변수가 설정되어 있지 않으면 지정된 기본값을 사용함
    
    # 예: OCR_BASE_URL=http://ollama-service:11434/v1
    ocr_base_url: str = "http://localhost:11434/v1"
    
    # 예: OCR_API_KEY=my-secret-key
    ocr_api_key: str = "ollama"
    
    # 예: OCR_MODEL_NAME=scb10x/typhoon-ocr1.5-3b
    ocr_model_name: str = "scb10x/typhoon-ocr1.5-3b"

    # [추가] 카프카 설정 (OpenShift 환경변수 대응)
    kafka_bootstrap_servers: str = "localhost:9092"
    kafka_input_topic: str = "ocr-request-topic"
    kafka_output_topic: str = "ocr-result-topic"
    kafka_group_id: str = "typhoon-ocr-group"

    class Config:
        # .env 파일이 있다면 거기서도 읽어올 수 있게 설정 (로컬 테스트용)
        env_file = ".env"

# 싱글톤 패턴으로 인스턴스 생성
settings = Settings()