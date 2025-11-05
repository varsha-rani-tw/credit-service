from pydantic_settings import BaseSettings
from typing import List


class KafkaConfig(BaseSettings):

    bootstrap_servers: List[str] = ["localhost:9092"]
    topic_credit_reports: str = "credit_reports_generated"
    topic_loan_applications: str = "loan_applications_submitted"
    client_id: str = "credit-service"
    compression_type: str = "gzip"
    acks: str = "all"
    retries: int = 3
    max_in_flight_requests: int = 5
    request_timeout_ms: int = 30000
    enable_idempotence: bool = True

    # Consumer settings
    consumer_group_id: str = "credit-service-consumer-group"
    auto_offset_reset: str = "earliest"
    enable_auto_commit: bool = True
    auto_commit_interval_ms: int = 5000
    session_timeout_ms: int = 30000
    max_poll_records: int = 100

    # Security settings (optional)
    security_protocol: str = "PLAINTEXT"
    sasl_mechanism: str = "PLAIN"
    sasl_username: str = ""
    sasl_password: str = ""

    class Config:
        env_prefix = "KAFKA_"
        case_sensitive = False

kafka_config = KafkaConfig()
