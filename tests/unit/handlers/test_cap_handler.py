from unittest.mock import Mock

import pytest
from src.handler.CapHandler import CapHandler
from src.Constant.CibilScoreConstant import CibilScoreConstant


class TestCapHandler:

    def test_handle_score_within_range(self, cap_handler, sample_application_data):
        initial_score = 700

        result = cap_handler.handle(initial_score, sample_application_data)

        assert result == initial_score

    def test_handle_score_above_maximum(self, cap_handler, sample_application_data):

        initial_score = 950

        result = cap_handler.handle(initial_score, sample_application_data)

        assert result == CibilScoreConstant.MAX_CIBIL_SCORE

    def test_handle_score_below_minimum(self, cap_handler, sample_application_data):
        initial_score = 200

        result = cap_handler.handle(initial_score, sample_application_data)

        assert result == CibilScoreConstant.MIN_CIBIL_SCORE

    def test_handle_score_at_maximum(self, cap_handler, sample_application_data):
        initial_score = CibilScoreConstant.MAX_CIBIL_SCORE

        result = cap_handler.handle(initial_score, sample_application_data)

        assert result == CibilScoreConstant.MAX_CIBIL_SCORE

    def test_handle_score_at_minimum(self, cap_handler, sample_application_data):
        initial_score = CibilScoreConstant.MIN_CIBIL_SCORE

        result = cap_handler.handle(initial_score, sample_application_data)

        assert result == CibilScoreConstant.MIN_CIBIL_SCORE


    def test_handle_extremely_high_score(self, cap_handler, sample_application_data):
        initial_score = 10000

        result = cap_handler.handle(initial_score, sample_application_data)

        assert result == CibilScoreConstant.MAX_CIBIL_SCORE

    def test_handle_extremely_low_score(self, cap_handler, sample_application_data):
        initial_score = -100

        result = cap_handler.handle(initial_score, sample_application_data)

        assert result == CibilScoreConstant.MIN_CIBIL_SCORE

