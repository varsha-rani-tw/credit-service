import pytest
from unittest.mock import patch
from fastapi.testclient import TestClient
from src.containers import Container
from app import app


@pytest.fixture
def client():
    return TestClient(app)


class TestCibilScoreAPI:

    @patch('random.randint', return_value=0)
    def test_simulate_score_success(self, mock_randint, client):

        payload = {
            "application_id": 1,
            "pan_number": "ABCDE1234F",
            "application_name": "John Doe",
            "monthly_income_inr": 80000,
            "loan_amount_inr": 500000,
            "loan_type": "HOME",
            "status": "PENDING",
            "cibil_score": 0
        }

        response = client.post("/simulate-cibil-score", json=payload)
        assert response.status_code == 200


    @patch('random.randint', return_value=0)
    def test_simulate_score_with_low_income(self, mock_randint, client):
        payload = {
            "application_id": 2,
            "pan_number": "UNKNOWN123",
            "application_name": "Jane Doe",
            "monthly_income_inr": 25000,
            "loan_amount_inr": 200000,
            "loan_type": "PERSONAL",
            "status": "pending"
        }

        response = client.post("/simulate-cibil-score", json=payload)
        assert response.status_code == 200

    def test_simulate_score_missing_required_field(self, client):
        payload = {
            "application_id": 3,
            "application_name": "Test User",
            "loan_type": "HOME"
        }

        response = client.post("/simulate-cibil-score", json=payload)

        assert response.status_code == 422

    def test_simulate_score_invalid_data_type(self, client):
        payload = {
            "application_id": "not_an_integer",
            "pan_number": "ABCDE1234F",
            "monthly_income_inr": 50000,
            "loan_type": "HOME"
        }

        response = client.post("/simulate-cibil-score", json=payload)
        assert response.status_code == 422

    @patch('random.randint', return_value=0)
    def test_simulate_score_with_minimal_data(self, mock_randint, client):
        payload = {
            "application_id": 4,
            "pan_number": "FGHIJ5678K",
            "monthly_income_inr": 60000,
            "loan_type": "AUTO"
        }

        response = client.post("/simulate-cibil-score", json=payload)
        assert response.status_code == 200

    @patch('random.randint', return_value=5)
    def test_simulate_score_with_positive_random(self, mock_randint, client):
        payload = {
            "application_id": 5,
            "pan_number": "ABCDE1234F",
            "monthly_income_inr": 100000,
            "loan_type": "HOME"
        }

        response = client.post("/simulate-cibil-score", json=payload)
        assert response.status_code == 200

    @patch('random.randint', return_value=-5)
    def test_simulate_score_with_negative_random(self, mock_randint, client):
        payload = {
            "application_id": 6,
            "pan_number": "UNKNOWN123",
            "monthly_income_inr": 50000,
            "loan_type": "AUTO"
        }

        response = client.post("/simulate-cibil-score", json=payload)
        assert response.status_code == 200

    def test_simulate_score_empty_payload(self, client):
        payload = {}
        response = client.post("/simulate-cibil-score", json=payload)
        assert response.status_code == 422

    @patch('random.randint', return_value=0)
    def test_simulate_score_with_all_optional_fields(self, mock_randint, client):
        payload = {
            "application_id": 7,
            "pan_number": "ABCDE1234F",
            "application_name": "Complete User",
            "monthly_income_inr": 90000,
            "loan_amount_inr": 1000000,
            "loan_type": "HOME",
            "status": "approved",
            "cibil_score": 800
        }

        response = client.post("/simulate-cibil-score", json=payload)
        assert response.status_code == 200

    @patch('src.service.CibilScoreService.CibilScoreService.simulate')
    def test_simulate_score_service_exception(self, mock_simulate, client):
        mock_simulate.side_effect = Exception("Service error")
        payload = {
            "application_id": 8,
            "pan_number": "ABCDE1234F",
            "monthly_income_inr": 50000,
            "loan_type": "HOME"
        }

        response = client.post("/simulate-cibil-score", json=payload)
        assert response.status_code == 500
        assert "Service error" in response.json()["detail"]

    def test_api_accepts_only_post_method(self, client):
        get_response = client.get("/simulate-cibil-score")

        assert get_response.status_code == 405  # Method not allowed

    @patch('random.randint', return_value=0)
    def test_simulate_score_idempotency(self, mock_randint, client):
        payload = {
            "application_id": 10,
            "pan_number": "ABCDE1234F",
            "monthly_income_inr": 70000,
            "loan_type": "HOME"
        }

        response1 = client.post("/simulate-cibil-score", json=payload)
        response2 = client.post("/simulate-cibil-score", json=payload)

        assert response1.status_code == 200
        assert response2.status_code == 200

    def test_openapi_docs_accessible(self, client):
        response = client.get("/docs")

        assert response.status_code == 200

    def test_openapi_json_accessible(self, client):
        response = client.get("/openapi.json")

        assert response.status_code == 200
        assert "openapi" in response.json()


