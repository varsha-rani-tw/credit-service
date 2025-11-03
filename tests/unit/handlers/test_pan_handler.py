
import pytest
from unittest.mock import Mock
from src.handler.PanHandler import PanHandler
from src.DTO.ApplicationDataDTO import ApplicationDataDTO
from src.Constant.CibilScoreConstant import CibilScoreConstant


class TestPanHandler:

    def test_handle_with_known_pan(self, pan_handler, sample_application_data):
        sample_application_data.pan_number = "ABCDE1234F"
        initial_score = 650

        result = pan_handler.handle(initial_score, sample_application_data)

        assert result == initial_score + 50

    def test_handle_with_another_known_pan(self, pan_handler, sample_application_data):
        sample_application_data.pan_number = "FGHIJ5678K"
        initial_score = 650

        result = pan_handler.handle(initial_score, sample_application_data)

        assert result == initial_score + 50

    def test_handle_with_unknown_pan(self, pan_handler, sample_application_data):
        sample_application_data.pan_number = "UNKNOWN1234"
        initial_score = 650

        result = pan_handler.handle(initial_score, sample_application_data)

        assert result == initial_score


