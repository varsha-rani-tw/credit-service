"""
Unit tests for KafkaProducerService.
"""
import pytest
from unittest.mock import Mock, AsyncMock, patch, MagicMock
from aiokafka.errors import KafkaError

from src.kafka.kafka_producer import KafkaProducerService
from src.config.kafka_config import KafkaConfig


@pytest.fixture
def kafka_config():
    """Fixture providing Kafka configuration."""
    return KafkaConfig(
        bootstrap_servers=["localhost:9092"],
        topic_loan_applications="test_topic",
        client_id="test-client"
    )


@pytest.fixture
def kafka_producer_service(kafka_config):
    """Fixture providing KafkaProducerService instance."""
    return KafkaProducerService(config=kafka_config)


class TestKafkaProducerService:
    """Test cases for KafkaProducerService."""

    def test_initialization(self, kafka_producer_service, kafka_config):
        """Test that service is initialized correctly."""
        assert kafka_producer_service.config == kafka_config
        assert kafka_producer_service.producer is None
        assert kafka_producer_service._is_started is False

    @pytest.mark.asyncio
    @patch('src.kafka.kafka_producer.AIOKafkaProducer')
    async def test_start_producer_success(self, mock_kafka_producer_class, kafka_producer_service):
        """Test successful Kafka producer start."""
        # Given
        mock_producer = AsyncMock()
        mock_kafka_producer_class.return_value = mock_producer

        # When
        await kafka_producer_service.start()

        # Then
        assert kafka_producer_service._is_started is True
        assert kafka_producer_service.producer is not None
        mock_producer.start.assert_called_once()

    @pytest.mark.asyncio
    @patch('src.kafka.kafka_producer.AIOKafkaProducer')
    async def test_start_producer_already_started(self, mock_kafka_producer_class, kafka_producer_service):
        """Test starting producer when already started."""
        # Given
        mock_producer = AsyncMock()
        mock_kafka_producer_class.return_value = mock_producer
        await kafka_producer_service.start()

        # When - Try to start again
        await kafka_producer_service.start()

        # Then - Should not create new producer
        assert mock_kafka_producer_class.call_count == 1

    @pytest.mark.asyncio
    @patch('src.kafka.kafka_producer.AIOKafkaProducer')
    async def test_start_producer_failure(self, mock_kafka_producer_class, kafka_producer_service):
        """Test handling of start failure."""
        # Given
        mock_producer = AsyncMock()
        mock_producer.start.side_effect = Exception("Connection failed")
        mock_kafka_producer_class.return_value = mock_producer

        # When/Then
        with pytest.raises(Exception, match="Connection failed"):
            await kafka_producer_service.start()

        assert kafka_producer_service._is_started is False

    @pytest.mark.asyncio
    @patch('src.kafka.kafka_producer.AIOKafkaProducer')
    async def test_stop_producer_success(self, mock_kafka_producer_class, kafka_producer_service):
        """Test successful producer stop."""
        # Given
        mock_producer = AsyncMock()
        mock_kafka_producer_class.return_value = mock_producer
        await kafka_producer_service.start()

        # When
        await kafka_producer_service.stop()

        # Then
        assert kafka_producer_service._is_started is False
        mock_producer.stop.assert_called_once()

    @pytest.mark.asyncio
    async def test_stop_producer_not_started(self, kafka_producer_service):
        """Test stopping producer when not started."""
        # When/Then - Should not raise exception
        await kafka_producer_service.stop()
        assert kafka_producer_service._is_started is False

    @pytest.mark.asyncio
    @patch('src.kafka.kafka_producer.AIOKafkaProducer')
    async def test_publish_message_success(self, mock_kafka_producer_class, kafka_producer_service):
        """Test successful message publication."""
        # Given
        mock_producer = AsyncMock()
        mock_metadata = MagicMock()
        mock_metadata.partition = 0
        mock_metadata.offset = 123

        mock_future = AsyncMock()
        mock_future.return_value = mock_metadata

        mock_producer.send.return_value = mock_future
        mock_kafka_producer_class.return_value = mock_producer

        await kafka_producer_service.start()

        message = {"application_id": 1, "score": 750}

        # When
        result = await kafka_producer_service.publish_message(
            topic="test_topic",
            message=message,
            key="1"
        )

        # Then
        assert result is True
        mock_producer.send.assert_called_once_with(
            topic="test_topic",
            value=message,
            key="1"
        )

    @pytest.mark.asyncio
    async def test_publish_message_producer_not_started(self, kafka_producer_service):
        """Test publishing message when producer not started."""
        # Given
        message = {"application_id": 1}

        # When/Then
        with pytest.raises(RuntimeError, match="Kafka producer is not started"):
            await kafka_producer_service.publish_message("test_topic", message)

    @pytest.mark.asyncio
    @patch('src.kafka.kafka_producer.AIOKafkaProducer')
    async def test_publish_message_kafka_error(self, mock_kafka_producer_class, kafka_producer_service):
        """Test handling of Kafka errors during publish."""
        # Given
        mock_producer = AsyncMock()
        mock_producer.send.side_effect = KafkaError("Broker unavailable")
        mock_kafka_producer_class.return_value = mock_producer

        await kafka_producer_service.start()

        message = {"application_id": 1}

        # When
        result = await kafka_producer_service.publish_message("test_topic", message)

        # Then
        assert result is False

    @pytest.mark.asyncio
    @patch('src.kafka.kafka_producer.AIOKafkaProducer')
    async def test_publish_loan_application(self, mock_kafka_producer_class, kafka_producer_service):
        """Test publishing loan application."""
        # Given
        mock_producer = AsyncMock()
        mock_metadata = MagicMock()
        mock_metadata.partition = 0
        mock_metadata.offset = 123

        mock_future = AsyncMock()
        mock_future.return_value = mock_metadata

        mock_producer.send.return_value = mock_future
        mock_kafka_producer_class.return_value = mock_producer

        await kafka_producer_service.start()

        application_data = {
            "application_id": 1,
            "pan_number": "ABCDE1234F",
            "cibil_score": 750
        }

        # When
        result = await kafka_producer_service.publish_loan_application(application_data)

        # Then
        assert result is True
        mock_producer.send.assert_called_once()
        call_args = mock_producer.send.call_args
        assert call_args.kwargs['topic'] == kafka_producer_service.config.topic_loan_applications
        assert call_args.kwargs['value'] == application_data
        assert call_args.kwargs['key'] == "1"

    def test_is_healthy_not_started(self, kafka_producer_service):
        """Test health check when producer not started."""
        assert kafka_producer_service.is_healthy is False

    @pytest.mark.asyncio
    @patch('src.kafka.kafka_producer.AIOKafkaProducer')
    async def test_is_healthy_started(self, mock_kafka_producer_class, kafka_producer_service):
        """Test health check when producer is started."""
        # Given
        mock_producer = AsyncMock()
        mock_kafka_producer_class.return_value = mock_producer

        # When
        await kafka_producer_service.start()

        # Then
        assert kafka_producer_service.is_healthy is True

    @pytest.mark.asyncio
    @patch('src.kafka.kafka_producer.AIOKafkaProducer')
    async def test_is_healthy_stopped(self, mock_kafka_producer_class, kafka_producer_service):
        """Test health check after stopping producer."""
        # Given
        mock_producer = AsyncMock()
        mock_kafka_producer_class.return_value = mock_producer

        await kafka_producer_service.start()
        await kafka_producer_service.stop()

        # Then
        assert kafka_producer_service.is_healthy is False
