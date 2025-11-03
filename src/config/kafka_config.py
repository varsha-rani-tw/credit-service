from pydantic_settings import BaseSettings
from typing import List


class KafkaConfig(BaseSettings):

    bootstrap_servers: List[str] = ["localhost:9092"]
    topic_loan_applications: str = "loan_applications_submitted"
    client_id: str = "credit-service"
    compression_type: str = "gzip"
    acks: str = "all"
    retries: int = 3
    max_in_flight_requests: int = 5
    request_timeout_ms: int = 30000
    enable_idempotence: bool = True

    # Security settings (optional)
    security_protocol: str = "PLAINTEXT"
    sasl_mechanism: str = "PLAIN"
    sasl_username: str = ""
    sasl_password: str = ""

    class Config:
        env_prefix = "KAFKA_"
        case_sensitive = False

kafka_config = KafkaConfig()
