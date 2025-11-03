import pytest
from unittest.mock import Mock, MagicMock
from fastapi.testclient import TestClient

from src.DTO.ApplicationDataDTO import ApplicationDataDTO
from src.handler.PanHandler import PanHandler
from src.handler.IncomeHandler import IncomeHandler
from src.handler.LoanTypeHandler import LoanTypeHandler
from src.handler.RandomHandler import RandomHanlder
from src.handler.CapHandler import CapHandler
from src.service.CibilScoreService import CibilScoreService
from src.mapper.ApplicationDataMapper import ApplicationDataMapper
from src.containers import Container


@pytest.fixture
def sample_application_data():
    return ApplicationDataDTO(
        application_id=1,
        pan_number="ABCDE1234F",
        application_name="John Doe",
        monthly_income_inr=50000,
        loan_amount_inr=500000,
        loan_type="HOME",
        status="pending",
        cibil_score=0
    )


@pytest.fixture
def sample_application_dict():
    return {
        "application_id": 1,
        "pan_number": "ABCDE1234F",
        "application_name": "John Doe",
        "monthly_income_inr": 50000,
        "loan_amount_inr": 500000,
        "loan_type": "HOME",
        "status": "pending",
        "cibil_score": 0
    }


@pytest.fixture
def pan_handler():
    return PanHandler()


@pytest.fixture
def income_handler():
    return IncomeHandler()


@pytest.fixture
def loan_handler():
    return LoanTypeHandler()


@pytest.fixture
def random_handler():
    return RandomHanlder()


@pytest.fixture
def cap_handler():
    return CapHandler()


@pytest.fixture
def cibil_service(pan_handler, income_handler, loan_handler, random_handler, cap_handler):
    return CibilScoreService(
        pan_handler=pan_handler,
        income_handler=income_handler,
        loan_handler=loan_handler,
        random_handler=random_handler,
        cap_handler=cap_handler
    )


@pytest.fixture
def application_mapper():
    return ApplicationDataMapper()


@pytest.fixture
def mock_service():
    return Mock(spec=CibilScoreService)


@pytest.fixture
def mock_mapper():
    return Mock(spec=ApplicationDataMapper)


@pytest.fixture
def test_container():
    container = Container()
    return container


@pytest.fixture
def test_client():
    from app import app
    return TestClient(app)
