from unittest.mock import Mock

import pytest
from src.handler.IncomeHandler import IncomeHandler


class TestIncomeHandler:

    def test_handle_high_income(self, income_handler, sample_application_data):

        sample_application_data.monthly_income_inr = 80000
        initial_score = 700

        result = income_handler.handle(initial_score, sample_application_data)

        assert result == initial_score + 40

    def test_handle_low_income(self, income_handler, sample_application_data):
        sample_application_data.monthly_income_inr = 25000
        initial_score = 700

        result = income_handler.handle(initial_score, sample_application_data)

        assert result == initial_score - 20

    def test_handle_medium_income(self, income_handler, sample_application_data):
        sample_application_data.monthly_income_inr = 50000
        initial_score = 700

        result = income_handler.handle(initial_score, sample_application_data)

        assert result == initial_score

    def test_handle_income_at_upper_boundary(self, income_handler, sample_application_data):
        sample_application_data.monthly_income_inr = 75000
        initial_score = 700

        result = income_handler.handle(initial_score, sample_application_data)

        assert result == initial_score

    def test_handle_income_at_lower_boundary(self, income_handler, sample_application_data):
        sample_application_data.monthly_income_inr = 30000
        initial_score = 700

        result = income_handler.handle(initial_score, sample_application_data)

        assert result == initial_score


