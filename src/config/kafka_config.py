"""
Kafka configuration settings.
"""
from pydantic_settings import BaseSettings
from typing import List


class KafkaConfig(BaseSettings):
    """
    Kafka configuration with environment variable support.

    Environment variables can be set with KAFKA_ prefix.
    Example: KAFKA_BOOTSTRAP_SERVERS=localhost:9092
    """

    bootstrap_servers: List[str] = ["localhost:9092"]
    topic_loan_applications: str = "loan_applications_submitted"
    client_id: str = "credit-service"
    compression_type: str = "gzip"
    acks: str = "all"  # Wait for all replicas
    retries: int = 3
    max_in_flight_requests: int = 5
    request_timeout_ms: int = 30000
    enable_idempotence: bool = True

    # Security settings (optional)
    security_protocol: str = "PLAINTEXT"  # Can be SASL_SSL, SSL, etc.
    sasl_mechanism: str = "PLAIN"
    sasl_username: str = ""
    sasl_password: str = ""

    class Config:
        env_prefix = "KAFKA_"
        case_sensitive = False


# Global config instance
kafka_config = KafkaConfig()
