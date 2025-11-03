from src.DTO.ApplicationDataDTO import ApplicationDataDTO
import logging

logger = logging.getLogger(__name__)


class CibilScoreHandler:

    def __init__(self):
        self.next = None

    def set_next(self, next_handler: "CibilScoreHandler") -> "ScoreHandler":
        self.next = next_handler
        return next_handler

    def calculate_cibil_score(self, score: int, application_data : ApplicationDataDTO) -> int:
        return score

    def handle(self, score: int, application_data: ApplicationDataDTO) -> int:
        pass











