import json
import asyncio
from aiokafka import AIOKafkaConsumer, AIOKafkaProducer
from .config import settings
from typhoon_ocr import ocr_document

class KafkaOCRWorker:
    def __init__(self):
        self.consumer = None
        self.producer = None
        self._stop_event = asyncio.Event()

    async def start(self):
        # 1. 프로듀서 시작
        self.producer = AIOKafkaProducer(
            bootstrap_servers=settings.kafka_bootstrap_servers
        )
        await self.producer.start()

        # 2. 컨슈머 시작
        self.consumer = AIOKafkaConsumer(
            settings.kafka_input_topic,
            bootstrap_servers=settings.kafka_bootstrap_servers,
            group_id=settings.kafka_group_id,
            value_deserializer=lambda v: json.loads(v.decode('utf-8'))
        )
        await self.consumer.start()
        print(f"[*] Kafka Worker Started: listening on {settings.kafka_input_topic}")

    async def stop(self):
        self._stop_event.set()
        if self.consumer:
            await self.consumer.stop()
        if self.producer:
            await self.producer.stop()
        print("[*] Kafka Worker Stopped")

    async def run_forever(self):
        """메시지 루프 실행"""
        try:
            async for msg in self.consumer:
                if self._stop_event.is_set():
                    break
                
                # 비즈니스 로직 호출
                await self._process_message(msg.value)
        except Exception as e:
            print(f"[!] Consumer Loop Error: {e}")

    async def _process_message(self, data: dict):
        """실제 OCR 처리 및 결과 전송 로직"""
        file_id = data.get("file_id")
        file_path = data.get("file_path") # 혹은 이미지 바이트

        try:
            # 1. OCR 수행
            # (주의: CPU 환경에서 오래 걸리므로 비동기 실행이 필요할 수 있으나, 
            # 워커 자체가 별도 태스크이므로 순차 처리가 안전함)
            text = ocr_document(
                file_path,
                base_url=settings.ollama_base_url,
                model=settings.ollama_model_name
            )

            # 2. 결과 전송
            result = {"file_id": file_id, "text": text, "status": "success"}
            await self.producer.send_and_wait(
                settings.kafka_output_topic,
                json.dumps(result).encode('utf-8')
            )
            print(f"[+] Success: {file_id}")

        except Exception as e:
            print(f"[!] OCR Processing Error for {file_id}: {e}")
            # 에러 메시지 전송 로직 추가 가능