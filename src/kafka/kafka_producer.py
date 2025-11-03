"""
Kafka producer for publishing messages.
"""
import json
import logging
from typing import Dict, Any, Optional
from aiokafka import AIOKafkaProducer
from aiokafka.errors import KafkaError

from src.config.kafka_config import KafkaConfig

logger = logging.getLogger(__name__)


class KafkaProducerService:
    """
    Kafka producer service for publishing messages to Kafka topics.

    This service handles connection management, message serialization,
    and error handling for Kafka message publishing.
    """

    def __init__(self, config: KafkaConfig):
        """
        Initialize Kafka producer service.

        Args:
            config: Kafka configuration settings
        """
        self.config = config
        self.producer: Optional[AIOKafkaProducer] = None
        self._is_started = False

    async def start(self):
        """
        Start the Kafka producer.

        Creates and starts the AIOKafkaProducer instance.
        Should be called during application startup.
        """
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
        """
        Stop the Kafka producer.

        Flushes pending messages and closes the connection.
        Should be called during application shutdown.
        """
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
        """
        Publish a message to a Kafka topic.

        Args:
            topic: Kafka topic name
            message: Message payload as dictionary
            key: Optional message key for partitioning

        Returns:
            True if message was published successfully, False otherwise

        Raises:
            RuntimeError: If producer is not started
        """
        if not self._is_started or not self.producer:
            raise RuntimeError("Kafka producer is not started. Call start() first.")

        try:
            # Send message to Kafka
            future = await self.producer.send(
                topic=topic,
                value=message,
                key=key
            )

            # Get metadata about the sent message
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
        """
        Publish loan application data to the loan_applications_submitted topic.

        Args:
            application_data: Application data including CIBIL score

        Returns:
            True if published successfully, False otherwise
        """
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
        """
        Check if the Kafka producer is healthy and ready to send messages.

        Returns:
            True if producer is started and ready, False otherwise
        """
        return self._is_started and self.producer is not None
