from src.DTO.ApplicationDataDTO import ApplicationDataDTO
from src.handler.CibilScoreHandler import CibilScoreHandler

import logging

logger = logging.getLogger(__name__)

class LoanTypeHandler(CibilScoreHandler):

    def handle(self, score: int, application_data: ApplicationDataDTO) -> int:
        new_score = score
        loan_type = application_data.loan_type

        logger.info("LoanTypeHandler started processing for Application ID: %s", application_data.application_id)
        if loan_type == "PERSONAL":
            new_score-=10
        if loan_type == "HOME":
            new_score+= 10

        logger.info("Updated score: %s", new_score)
        if self.next:
            return self.next.handle(new_score, application_data)
        return new_score

