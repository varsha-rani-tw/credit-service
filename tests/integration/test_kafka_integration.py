import pytest
from unittest.mock import patch, AsyncMock, MagicMock
from fastapi.testclient import TestClient
from app import app


@pytest.fixture
def client():
    return TestClient(app)



class TestKafkaIntegration:

    @patch('random.randint', return_value=0)
    @patch('src.kafka.kafka_producer.KafkaProducerService.publish_loan_application')
    async def test_simulate_score_publishes_to_kafka(
        self,
        mock_publish,
        mock_randint,
        client
    ):
        mock_publish.return_value = True

        payload = {
            "application_id": 1,
            "pan_number": "ABCDE1234F",
            "application_name": "John Doe",
            "monthly_income_inr": 80000,
            "loan_amount_inr": 500000,
            "loan_type": "HOME",
            "status": "pending"
        }

        response = client.post("/simulate-cibil-score", json=payload)

        assert response.status_code == 200
        response_data = response.json()
        assert response_data["status"] == "success"
        assert response_data["cibil_score"] == 700  # Known PAN returns early
        assert "published to Kafka successfully" in response_data["message"]

    @patch('random.randint', return_value=0)
    @patch('src.kafka.kafka_producer.KafkaProducerService.publish_loan_application')
    async def test_simulate_score_kafka_failure_returns_partial_success(
        self,
        mock_publish,
        mock_randint,
        client
    ):
        mock_publish.return_value = False  # Kafka publish fails

        payload = {
            "application_id": 2,
            "pan_number": "UNKNOWN123",
            "monthly_income_inr": 50000,
            "loan_type": "AUTO"
        }

        response = client.post("/simulate-cibil-score", json=payload)

        # Then
        assert response.status_code == 200
        response_data = response.json()
        assert response_data["status"] == "partial_success"
        assert "Kafka publishing failed" in response_data["message"]
        assert response_data["cibil_score"] == 650  # Score still calculated

    @patch('random.randint', return_value=0)
    @patch('src.kafka.kafka_producer.KafkaProducerService.publish_loan_application')
    async def test_kafka_message_contains_correct_data(
        self,
        mock_publish,
        mock_randint,
        client
    ):
        mock_publish.return_value = True

        payload = {
            "application_id": 3,
            "pan_number": "FGHIJ5678K",
            "application_name": "Jane Smith",
            "monthly_income_inr": 60000,
            "loan_amount_inr": 300000,
            "loan_type": "PERSONAL",
            "status": "processing"
        }

        response = client.post("/simulate-cibil-score", json=payload)

        assert response.status_code == 200

        mock_publish.assert_called_once()

        kafka_message = mock_publish.call_args[0][0]
        assert kafka_message["application_id"] == 3
        assert kafka_message["pan_number"] == "FGHIJ5678K"
        assert kafka_message["application_name"] == "Jane Smith"
        assert kafka_message["monthly_income_inr"] == 60000
        assert kafka_message["loan_amount_inr"] == 300000
        assert kafka_message["loan_type"] == "PERSONAL"
        assert kafka_message["status"] == "processing"
        assert "cibil_score" in kafka_message
        assert "calculated_cibil_score" in kafka_message

    @patch('random.randint', return_value=0)
    @patch('src.kafka.kafka_producer.KafkaProducerService.publish_loan_application')
    async def test_kafka_message_with_default_status(
        self,
        mock_publish,
        mock_randint,
        client
    ):
        mock_publish.return_value = True

        payload = {
            "application_id": 4,
            "pan_number": "UNKNOWN123",
            "monthly_income_inr": 50000,
            "loan_type": "HOME"
        }
        response = client.post("/simulate-cibil-score", json=payload)

        assert response.status_code == 200

        kafka_message = mock_publish.call_args[0][0]
        assert kafka_message["status"] == "pending"

    @patch('random.randint', return_value=0)
    @patch('src.kafka.kafka_producer.KafkaProducerService.publish_loan_application')
    async def test_multiple_requests_publish_separately(
        self,
        mock_publish,
        mock_randint,
        client
    ):
        mock_publish.return_value = True

        payload1 = {
            "application_id": 5,
            "pan_number": "ABCDE1234F",
            "monthly_income_inr": 70000,
            "loan_type": "HOME"
        }

        payload2 = {
            "application_id": 6,
            "pan_number": "FGHIJ5678K",
            "monthly_income_inr": 80000,
            "loan_type": "PERSONAL"
        }

        response1 = client.post("/simulate-cibil-score", json=payload1)
        response2 = client.post("/simulate-cibil-score", json=payload2)

        assert response1.status_code == 200
        assert response2.status_code == 200
        assert mock_publish.call_count == 2

        call1_message = mock_publish.call_args_list[0][0][0]
        call2_message = mock_publish.call_args_list[1][0][0]

        assert call1_message["application_id"] == 5
        assert call2_message["application_id"] == 6

    @patch('random.randint', return_value=-5)
    @patch('src.kafka.kafka_producer.KafkaProducerService.publish_loan_application')
    async def test_kafka_publishes_calculated_score(
        self,
        mock_publish,
        mock_randint,
        client
    ):
        mock_publish.return_value = True

        payload = {
            "application_id": 7,
            "pan_number": "UNKNOWN123",
            "monthly_income_inr": 20000,
            "loan_type": "PERSONAL"
        }

        response = client.post("/simulate-cibil-score", json=payload)

        assert response.status_code == 200

        kafka_message = mock_publish.call_args[0][0]
        assert kafka_message["calculated_cibil_score"] == 615

    @patch('src.kafka.kafka_producer.KafkaProducerService.publish_loan_application')
    async def test_api_validation_error_does_not_publish(
        self,
        mock_publish,
        client
    ):
        payload = {
            "application_id": 8,
        }

        response = client.post("/simulate-cibil-score", json=payload)

        assert response.status_code == 422  # Validation error
        mock_publish.assert_not_called()
