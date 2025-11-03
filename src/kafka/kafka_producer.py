import json
import logging
from typing import Dict, Any, Optional
from aiokafka import AIOKafkaProducer
from aiokafka.errors import KafkaError

from src.config.kafka_config import KafkaConfig

logger = logging.getLogger(__name__)


class KafkaProducerService:

    def __init__(self, config: KafkaConfig):
        self.config = config
        self.producer: Optional[AIOKafkaProducer] = None
        self._is_started = False

    async def start(self):

        if self._is_started:
            logger.warning("Kafka producer already started")
            return

        try:
            self.producer = AIOKafkaProducer(
                bootstrap_servers=self.config.bootstrap_servers,
                client_id=self.config.client_id,
                compression_type=self.config.compression_type,
                acks=self.config.acks,
                request_timeout_ms=self.config.request_timeout_ms,
                enable_idempotence=self.config.enable_idempotence,
                value_serializer=lambda v: json.dumps(v).encode('utf-8'),
                key_serializer=lambda k: k.encode('utf-8') if k else None,
            )

            await self.producer.start()
            self._is_started = True
            logger.info(f"Kafka producer started successfully. Connected to: {self.config.bootstrap_servers}")

        except Exception as e:
            logger.error(f"Failed to start Kafka producer: {e}")
            raise

    async def stop(self):
        if not self._is_started or not self.producer:
            logger.warning("Kafka producer not started or already stopped")
            return

        try:
            await self.producer.stop()
            self._is_started = False
            logger.info("Kafka producer stopped successfully")

        except Exception as e:
            logger.error(f"Error stopping Kafka producer: {e}")
            raise

    async def publish_message(
        self,
        topic: str,
        message: Dict[str, Any],
        key: Optional[str] = None
    ) -> bool:

        if not self._is_started or not self.producer:
            raise RuntimeError("Kafka producer is not started. Call start() first.")

        try:

            future = await self.producer.send(
                topic=topic,
                value=message,
                key=key
            )

            metadata = await future
            logger.info(
                f"Message published successfully to topic '{topic}' "
                f"[partition: {metadata.partition}, offset: {metadata.offset}]"
            )
            return True

        except KafkaError as e:
            logger.error(f"Kafka error while publishing message to topic '{topic}': {e}")
            return False

        except Exception as e:
            logger.error(f"Unexpected error while publishing message to topic '{topic}': {e}")
            return False

    async def publish_loan_application(self, application_data: Dict[str, Any]) -> bool:

        topic = self.config.topic_loan_applications
        key = str(application_data.get("application_id", ""))

        logger.info(f"Publishing loan application {key} to topic '{topic}'")

        return await self.publish_message(
            topic=topic,
            message=application_data,
            key=key
        )

    @property
    def is_healthy(self) -> bool:

        return self._is_started and self.producer is not None
