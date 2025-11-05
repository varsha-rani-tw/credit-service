from dependency_injector import containers, providers

from src.handler.PanHandler import PanHandler
from src.handler.IncomeHandler import IncomeHandler
from src.handler.LoanTypeHandler import LoanTypeHandler
from src.handler.RandomHandler import RandomHanlder
from src.handler.CapHandler import CapHandler
from src.service.CibilScoreService import CibilScoreService
from src.mapper.ApplicationDataMapper import ApplicationDataMapper
from src.config.kafka_config import KafkaConfig, kafka_config
from src.kafka.kafka_producer import KafkaProducerService
from src.kafka.kafka_consumer import KafkaConsumerService
from src.util.KafkaUtil import KafkaUtil


class Container(containers.DeclarativeContainer):
    """
    Dependency Injection Container for Credit Service.

    This container manages all dependencies including handlers, services,
    mappers, and Kafka messaging components.
    """

    # Configuration
    config = providers.Configuration()

    # Kafka Configuration - Singleton for application-wide settings
    kafka_config_provider = providers.Singleton(
        lambda: kafka_config
    )

    # Kafka Producer - Singleton to reuse connection pool
    kafka_producer = providers.Singleton(
        KafkaProducerService,
        config=kafka_config_provider
    )


    # Handler Dependencies - Using Singleton as handlers are stateless
    pan_handler = providers.Singleton(PanHandler)

    income_handler = providers.Singleton(IncomeHandler)

    loan_handler = providers.Singleton(LoanTypeHandler)

    random_handler = providers.Singleton(RandomHanlder)

    cap_handler = providers.Singleton(CapHandler)

    kafka_util = providers.Singleton(KafkaUtil)

    # Service Dependencies - Using Factory to create new instance per request
    cibil_service = providers.Factory(
        CibilScoreService,
        pan_handler=pan_handler,
        income_handler=income_handler,
        loan_handler=loan_handler,
        random_handler=random_handler,
        cap_handler=cap_handler,
    )

    # Mapper Dependencies - Using Singleton as mapper is stateless
    application_data_mapper = providers.Singleton(ApplicationDataMapper)

    # Kafka Consumer - Singleton to maintain single consumer instance
    kafka_consumer = providers.Singleton(
        KafkaConsumerService,
        config=kafka_config_provider,
        cibil_service=cibil_service,
        mapper=application_data_mapper,
        kafka_producer=kafka_producer
    )
