"""
FastAPI application entry point with dependency injection container.
"""
import logging
from contextlib import asynccontextmanager
from fastapi import FastAPI
from src.router.CibilScoreRouter import router as cibil_router
from src.containers import Container

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Lifespan context manager for application startup and shutdown.

    Handles:
    - Kafka producer initialization on startup
    - Kafka producer cleanup on shutdown
    """
    # Startup
    logger.info("Starting up Credit Service...")
    container: Container = app.container
    kafka_producer = container.kafka_producer()

    try:
        await kafka_producer.start()
        logger.info("Kafka producer started successfully")
    except Exception as e:
        logger.error(f"Failed to start Kafka producer: {e}")
        logger.warning("Service will continue without Kafka publishing capability")

    yield

    # Shutdown
    logger.info("Shutting down Credit Service...")
    try:
        await kafka_producer.stop()
        logger.info("Kafka producer stopped successfully")
    except Exception as e:
        logger.error(f"Error stopping Kafka producer: {e}")


def create_app() -> FastAPI:
    """
    Application factory that creates and configures the FastAPI app.

    Returns:
        Configured FastAPI application instance
    """
    container = Container()

    app = FastAPI(
        title="Credit Service API",
        description="Service for simulating CIBIL scores with Kafka integration",
        version="0.1.0",
        lifespan=lifespan
    )

    # Attach container to app for access in routes
    app.container = container

    # Wire container to modules for dependency injection
    container.wire(modules=["src.router.CibilScoreRouter"])

    # Include routers
    app.include_router(cibil_router)

    logger.info("Credit Service application created successfully")

    return app


# Create the application instance
app = create_app()
