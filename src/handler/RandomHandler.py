import random

from src.DTO.ApplicationDataDTO import ApplicationDataDTO
from src.handler.CibilScoreHandler import CibilScoreHandler
import logging

logger = logging.getLogger(__name__)

class RandomHanlder(CibilScoreHandler):

    def handle(self, score: int, application_data: ApplicationDataDTO) -> int:
        logger.info("RandomHandler started processing for Application ID: %s", application_data.application_id)

        random_number = random.randint(-5, 5)
        score+=random_number
        logger.info("Updated Score: %s", score)
        if self.next:
            return self.next.handle(score,application_data)
        return score