import json
import logging
import asyncio
from typing import Optional
from aiokafka import AIOKafkaConsumer
from aiokafka.errors import KafkaError

from src.config.kafka_config import KafkaConfig
from src.service.CibilScoreService import CibilScoreService
from src.mapper.ApplicationDataMapper import ApplicationDataMapper
from src.kafka.kafka_producer import KafkaProducerService

logger = logging.getLogger(__name__)


class KafkaConsumerService:

    def __init__(
        self,
        config: KafkaConfig,
        cibil_service: CibilScoreService,
        mapper: ApplicationDataMapper,
        kafka_producer: KafkaProducerService
    ):
        self.config = config
        self.cibil_service = cibil_service
        self.mapper = mapper
        self.kafka_producer = kafka_producer
        self.consumer: Optional[AIOKafkaConsumer] = None
        self._is_started = False
        self._consumer_task: Optional[asyncio.Task] = None

    async def start(self):

        if self._is_started:
            logger.warning("Kafka consumer already started")
            return

        try:
            self.consumer = AIOKafkaConsumer(
                self.config.topic_loan_applications,
                bootstrap_servers=self.config.bootstrap_servers,
                group_id=self.config.consumer_group_id,
                auto_offset_reset=self.config.auto_offset_reset,
                enable_auto_commit=self.config.enable_auto_commit,
                auto_commit_interval_ms=self.config.auto_commit_interval_ms,
                session_timeout_ms=self.config.session_timeout_ms,
                max_poll_records=self.config.max_poll_records,
                value_deserializer=lambda m: json.loads(m.decode('utf-8')),
            )

            await self.consumer.start()
            self._is_started = True
            logger.info(
                f"Kafka consumer started successfully. "
                f"Subscribed to topic: {self.config.topic_loan_applications}"
            )

            # Start consuming messages in background
            self._consumer_task = asyncio.create_task(self._consume_messages())

        except Exception as e:
            logger.error(f"Failed to start Kafka consumer: {e}")
            raise

    async def stop(self):
        if not self._is_started or not self.consumer:
            logger.warning("Kafka consumer not started or already stopped")
            return

        try:
            # Cancel the consumer task
            if self._consumer_task and not self._consumer_task.done():
                self._consumer_task.cancel()
                try:
                    await self._consumer_task
                except asyncio.CancelledError:
                    logger.info("Consumer task cancelled successfully")

            await self.consumer.stop()
            self._is_started = False
            logger.info("Kafka consumer stopped successfully")

        except Exception as e:
            logger.error(f"Error stopping Kafka consumer: {e}")
            raise

    async def _consume_messages(self):

        logger.info("Starting to consume messages from Kafka...")

        try:
            async for message in self.consumer:
                try:
                    logger.info(
                        f"Received message from topic '{message.topic}' "
                        f"[partition: {message.partition}, offset: {message.offset}]"
                    )

                    # Process the message
                    await self._process_loan_application(message.value)

                except Exception as e:
                    logger.error(f"Error processing message: {e}", exc_info=True)
                    # Continue processing other messages even if one fails

        except asyncio.CancelledError:
            logger.info("Message consumption cancelled")
            raise
        except Exception as e:
            logger.error(f"Unexpected error in consumer loop: {e}", exc_info=True)

    async def _process_loan_application(self, message_data: dict):

        try:
            application_id = message_data.get("application_id", "unknown")
            logger.info(f"Processing loan application: {application_id}")

            # Map the message to DTO
            application_data_dto = self.mapper.map_application_data_dto(message_data)

            # Calculate CIBIL score
            calculated_score = self.cibil_service.simulate(application_data_dto)

            logger.info(
                f"CIBIL score calculated for application {application_id}: {calculated_score}"
            )

            # Publish the result to credit_reports_generated topic
            await self._publish_credit_report(calculated_score, application_data_dto)

        except Exception as e:
            logger.error(
                f"Error processing loan application {message_data.get('application_id', 'unknown')}: {e}",
                exc_info=True
            )
            raise

    async def _publish_credit_report(self, cibil_score: int, application_data):

        kafka_message = {
            "application_id": application_data.application_id,
            "pan_number": application_data.pan_number,
            "application_name": application_data.application_name,
            "monthly_income_inr": application_data.monthly_income_inr,
            "loan_amount_inr": application_data.loan_amount_inr,
            "loan_type": application_data.loan_type,
            "status": application_data.status or "pending",
            "cibil_score": cibil_score,
        }

        try:
            success = await self.kafka_producer.publish_message(
                topic=self.config.topic_credit_reports,
                message=kafka_message,
                key=str(application_data.application_id)
            )

            if success:
                logger.info(
                    f"Credit report published successfully for application {application_data.application_id}"
                )
            else:
                logger.warning(
                    f"Failed to publish credit report for application {application_data.application_id}"
                )

        except Exception as e:
            logger.error(
                f"Error publishing credit report for application {application_data.application_id}: {e}"
            )

    @property
    def is_healthy(self) -> bool:
        return self._is_started and self.consumer is not None
