import logging

from src.kafka.kafka_producer import KafkaProducerService

logger = logging.getLogger(__name__)

class KafkaUtil:

    def __init__(self, kafka_producer_service: KafkaProducerService):
        self.kafka_producer_service = kafka_producer_service



    async def publish_message(self, kafka_message: dict):
        kafka_success = await self.kafka_producer_service.publish_loan_application(kafka_message)

        if not kafka_success:
            logger.warning(
                f"Failed to publish application {kafka_message.get('application_id')} to Kafka, "
                "but returning calculated score"
            )

