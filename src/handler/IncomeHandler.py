from src.DTO.ApplicationDataDTO import ApplicationDataDTO
from src.handler.CibilScoreHandler import CibilScoreHandler
import logging

logger = logging.getLogger(__name__)


class IncomeHandler(CibilScoreHandler):

    def handle(self, score: int, application_data: ApplicationDataDTO) -> int:
        new_score = score
        applicant_income = application_data.monthly_income_inr

        logger.info("CapHandler started processing for Application ID: %s", application_data.application_id)
        if applicant_income > 75000:
            new_score+= 40
        if applicant_income < 30000:
            new_score-=20

        logger.info("Updated Score: %s", new_score)

        if self.next:
            return self.next.handle(new_score, application_data)
        return new_score


