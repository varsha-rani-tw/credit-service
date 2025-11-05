"""
FastAPI application entry point with dependency injection container.
"""
import logging
from contextlib import asynccontextmanager
from fastapi import FastAPI
from src.router.CibilScoreRouter import router as cibil_router
from src.containers import Container

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):

    logger.info("Starting up Credit Service...")
    container: Container = app.container
    kafka_producer = container.kafka_producer()
    kafka_consumer = container.kafka_consumer()

    try:
        await kafka_producer.start()
        logger.info("Kafka producer started successfully")
    except Exception as e:
        logger.error(f"Failed to start Kafka producer: {e}")
        logger.warning("Service will continue without Kafka publishing capability")

    try:
        await kafka_consumer.start()
        logger.info("Kafka consumer started successfully")
    except Exception as e:
        logger.error(f"Failed to start Kafka consumer: {e}")
        logger.warning("Service will continue without Kafka consumption capability")

    yield

    logger.info("Shutting down Credit Service...")

    try:
        await kafka_consumer.stop()
        logger.info("Kafka consumer stopped successfully")
    except Exception as e:
        logger.error(f"Error stopping Kafka consumer: {e}")

    try:
        await kafka_producer.stop()
        logger.info("Kafka producer stopped successfully")
    except Exception as e:
        logger.error(f"Error stopping Kafka producer: {e}")


def create_app() -> FastAPI:
    container = Container()

    app = FastAPI(
        title="Credit Service API",
        description="Service for simulating CIBIL scores with Kafka integration",
        version="0.1.0",
        lifespan=lifespan
    )

    app.container = container

    container.wire(modules=["src.router.CibilScoreRouter"])

    app.include_router(cibil_router)

    logger.info("Credit Service application created successfully")

    return app


app = create_app()
