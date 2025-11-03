
import pytest
from src.handler.LoanTypeHandler import LoanTypeHandler


class TestLoanTypeHandler:


    def test_handle_personal_loan(self, loan_handler, sample_application_data):
        sample_application_data.loan_type = "PERSONAL"
        initial_score = 700

        result = loan_handler.handle(initial_score, sample_application_data)

        assert result == initial_score - 10

    def test_handle_home_loan(self, loan_handler, sample_application_data):

        sample_application_data.loan_type = "HOME"
        initial_score = 700

        result = loan_handler.handle(initial_score, sample_application_data)

        assert result == initial_score + 10

    def test_handle_other_loan_type(self, loan_handler, sample_application_data):

        sample_application_data.loan_type = "AUTO"
        initial_score = 700

        result = loan_handler.handle(initial_score, sample_application_data)

        assert result == initial_score

    def test_handle_case_sensitivity(self, loan_handler, sample_application_data):

        sample_application_data.loan_type = "personal"
        initial_score = 700

        result = loan_handler.handle(initial_score, sample_application_data)

        assert result == initial_score



