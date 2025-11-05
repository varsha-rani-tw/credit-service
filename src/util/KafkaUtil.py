import logging

from dependency_injector.wiring import Provide
from fastapi import Depends

from src.containers import Container
from src.kafka.kafka_producer import KafkaProducerService

logger = logging.getLogger(__name__)

class KafkaUtil:

    async def publish_message(self, kafka_message, kafka_producer: KafkaProducerService = Depends(Provide[Container.kafka_producer])):
        kafka_success = await kafka_producer.publish_loan_application(kafka_message)

        if not kafka_success:
            logger.warning(
                f"Failed to publish application {kafka_message.get('application_id')} to Kafka, "
                "but returning calculated score"
            )

