import pytest
from unittest.mock import Mock, MagicMock, patch
from src.service.CibilScoreService import CibilScoreService
from src.handler.PanHandler import PanHandler
from src.handler.IncomeHandler import IncomeHandler
from src.handler.LoanTypeHandler import LoanTypeHandler
from src.handler.RandomHandler import RandomHanlder
from src.handler.CapHandler import CapHandler
from src.DTO.ApplicationDataDTO import ApplicationDataDTO
from src.Constant.CibilScoreConstant import CibilScoreConstant


class TestCibilScoreService:

    def test_service_initialization(self, cibil_service):

        assert cibil_service.pan_handler is not None
        assert cibil_service.income_handler is not None
        assert cibil_service.loan_handler is not None
        assert cibil_service.random_handler is not None
        assert cibil_service.cap_handler is not None
        assert cibil_service.chain is not None

    def test_build_chain_creates_proper_chain(self, cibil_service):
        assert cibil_service.chain == cibil_service.pan_handler
        assert cibil_service.pan_handler.next == cibil_service.income_handler
        assert cibil_service.income_handler.next == cibil_service.loan_handler
        assert cibil_service.loan_handler.next == cibil_service.random_handler
        assert cibil_service.random_handler.next == cibil_service.cap_handler


    @patch('random.randint', return_value=0)
    def test_simulate_with_known_pan_high_income_home_loan(self, mock_randint, cibil_service, sample_application_data):

        sample_application_data.pan_number = "ABCDE1234F"  # +50 (returns early, no other handlers called)
        sample_application_data.monthly_income_inr = 80000
        sample_application_data.loan_type = "HOME"
        result = cibil_service.simulate(sample_application_data)

        assert result == 700

    @patch('random.randint', return_value=0)
    def test_simulate_with_unknown_pan_low_income_personal_loan(self, mock_randint, cibil_service, sample_application_data):
        sample_application_data.pan_number = "UNKNOWN123"
        sample_application_data.monthly_income_inr = 25000
        sample_application_data.loan_type = "PERSONAL"

        result = cibil_service.simulate(sample_application_data)

        assert result == 620

    @patch('random.randint', return_value=5)
    def test_simulate_with_score_exceeding_maximum(self, mock_randint, cibil_service, sample_application_data):

        sample_application_data.pan_number = "ABCDE1234F"
        sample_application_data.monthly_income_inr = 100000
        sample_application_data.loan_type = "HOME"

        result = cibil_service.simulate(sample_application_data)

        assert result == 700
        assert result <= CibilScoreConstant.MAX_CIBIL_SCORE

    @patch('random.randint', return_value=-5)
    def test_simulate_with_medium_income_auto_loan(self, mock_randint, cibil_service, sample_application_data):

        sample_application_data.pan_number = "UNKNOWN123"
        sample_application_data.monthly_income_inr = 50000
        sample_application_data.loan_type = "AUTO"

        result = cibil_service.simulate(sample_application_data)

        assert result == 645

    def test_simulate_returns_integer(self, cibil_service, sample_application_data):

        result = cibil_service.simulate(sample_application_data)

        assert isinstance(result, int)

