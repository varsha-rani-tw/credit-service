import pytest
from unittest.mock import Mock, AsyncMock, patch, MagicMock
from aiokafka.errors import KafkaError

from src.kafka.kafka_producer import KafkaProducerService
from src.config.kafka_config import KafkaConfig


@pytest.fixture
def kafka_config():
    return KafkaConfig(
        bootstrap_servers=["localhost:9092"],
        topic_loan_applications="test_topic",
        client_id="test-client"
    )


@pytest.fixture
def kafka_producer_service(kafka_config):
    return KafkaProducerService(config=kafka_config)


class TestKafkaProducerService:

    def test_initialization(self, kafka_producer_service, kafka_config):
        assert kafka_producer_service.config == kafka_config
        assert kafka_producer_service.producer is None
        assert kafka_producer_service._is_started is False

    @pytest.mark.asyncio
    @patch('src.kafka.kafka_producer.AIOKafkaProducer')
    async def test_start_producer_success(self, mock_kafka_producer_class, kafka_producer_service):
        mock_producer = AsyncMock()
        mock_kafka_producer_class.return_value = mock_producer

        await kafka_producer_service.start()

        assert kafka_producer_service._is_started is True
        assert kafka_producer_service.producer is not None
        mock_producer.start.assert_called_once()

    @pytest.mark.asyncio
    @patch('src.kafka.kafka_producer.AIOKafkaProducer')
    async def test_start_producer_already_started(self, mock_kafka_producer_class, kafka_producer_service):
        mock_producer = AsyncMock()
        mock_kafka_producer_class.return_value = mock_producer
        await kafka_producer_service.start()

        await kafka_producer_service.start()

        assert mock_kafka_producer_class.call_count == 1

    @pytest.mark.asyncio
    @patch('src.kafka.kafka_producer.AIOKafkaProducer')
    async def test_start_producer_failure(self, mock_kafka_producer_class, kafka_producer_service):

        mock_producer = AsyncMock()
        mock_producer.start.side_effect = Exception("Connection failed")
        mock_kafka_producer_class.return_value = mock_producer

        with pytest.raises(Exception, match="Connection failed"):
            await kafka_producer_service.start()

        assert kafka_producer_service._is_started is False

    @pytest.mark.asyncio
    @patch('src.kafka.kafka_producer.AIOKafkaProducer')
    async def test_stop_producer_success(self, mock_kafka_producer_class, kafka_producer_service):
        mock_producer = AsyncMock()
        mock_kafka_producer_class.return_value = mock_producer
        await kafka_producer_service.start()

        await kafka_producer_service.stop()

        assert kafka_producer_service._is_started is False
        mock_producer.stop.assert_called_once()

    @pytest.mark.asyncio
    async def test_stop_producer_not_started(self, kafka_producer_service):
        await kafka_producer_service.stop()
        assert kafka_producer_service._is_started is False

    @pytest.mark.asyncio
    @patch('src.kafka.kafka_producer.AIOKafkaProducer')
    async def test_publish_message_success(self, mock_kafka_producer_class, kafka_producer_service):

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

        result = await kafka_producer_service.publish_message(
            topic="test_topic",
            message=message,
            key="1"
        )

        assert result is True
        mock_producer.send.assert_called_once_with(
            topic="test_topic",
            value=message,
            key="1"
        )

    @pytest.mark.asyncio
    async def test_publish_message_producer_not_started(self, kafka_producer_service):
        message = {"application_id": 1}

        with pytest.raises(RuntimeError, match="Kafka producer is not started"):
            await kafka_producer_service.publish_message("test_topic", message)

    @pytest.mark.asyncio
    @patch('src.kafka.kafka_producer.AIOKafkaProducer')
    async def test_publish_message_kafka_error(self, mock_kafka_producer_class, kafka_producer_service):
        mock_producer = AsyncMock()
        mock_producer.send.side_effect = KafkaError("Broker unavailable")
        mock_kafka_producer_class.return_value = mock_producer

        await kafka_producer_service.start()

        message = {"application_id": 1}

        result = await kafka_producer_service.publish_message("test_topic", message)

        assert result is False

    @pytest.mark.asyncio
    @patch('src.kafka.kafka_producer.AIOKafkaProducer')
    async def test_publish_loan_application(self, mock_kafka_producer_class, kafka_producer_service):

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

        result = await kafka_producer_service.publish_loan_application(application_data)

        assert result is True
        mock_producer.send.assert_called_once()
        call_args = mock_producer.send.call_args
        assert call_args.kwargs['topic'] == kafka_producer_service.config.topic_loan_applications
        assert call_args.kwargs['value'] == application_data
        assert call_args.kwargs['key'] == "1"

    def test_is_healthy_not_started(self, kafka_producer_service):
        assert kafka_producer_service.is_healthy is False

    @pytest.mark.asyncio
    @patch('src.kafka.kafka_producer.AIOKafkaProducer')
    async def test_is_healthy_started(self, mock_kafka_producer_class, kafka_producer_service):
        mock_producer = AsyncMock()
        mock_kafka_producer_class.return_value = mock_producer

        await kafka_producer_service.start()

        assert kafka_producer_service.is_healthy is True

    @pytest.mark.asyncio
    @patch('src.kafka.kafka_producer.AIOKafkaProducer')
    async def test_is_healthy_stopped(self, mock_kafka_producer_class, kafka_producer_service):
        mock_producer = AsyncMock()
        mock_kafka_producer_class.return_value = mock_producer

        await kafka_producer_service.start()
        await kafka_producer_service.stop()

        assert kafka_producer_service.is_healthy is False
