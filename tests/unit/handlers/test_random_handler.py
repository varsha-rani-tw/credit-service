import pytest
from unittest.mock import patch
from src.handler.RandomHandler import RandomHanlder


class TestRandomHandler:

    @patch('random.randint')
    def test_handle_with_positive_random(self, mock_randint, random_handler, sample_application_data):

        mock_randint.return_value = 5
        initial_score = 700

        result = random_handler.handle(initial_score, sample_application_data)

        assert result == initial_score + 5
        mock_randint.assert_called_once_with(-5, 5)

    @patch('random.randint')
    def test_handle_with_negative_random(self, mock_randint, random_handler, sample_application_data):
        mock_randint.return_value = -5
        initial_score = 700

        result = random_handler.handle(initial_score, sample_application_data)

        assert result == initial_score - 5
        mock_randint.assert_called_once_with(-5, 5)

    @patch('random.randint')
    def test_handle_with_zero_random(self, mock_randint, random_handler, sample_application_data):
        mock_randint.return_value = 0
        initial_score = 700

        result = random_handler.handle(initial_score, sample_application_data)

        assert result == initial_score
        mock_randint.assert_called_once_with(-5, 5)


