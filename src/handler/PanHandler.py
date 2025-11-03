from src.DTO.ApplicationDataDTO import ApplicationDataDTO
from src.handler.CibilScoreHandler import CibilScoreHandler
from src.Constant.CibilScoreConstant import CibilScoreConstant
import logging

logger = logging.getLogger(__name__)

class PanHandler(CibilScoreHandler):

    def handle(self, score: int, application_data: ApplicationDataDTO) -> int:
        new_score = score
        applicant_pan = application_data.pan_number

        logger.info("PANHandler started processing for Application ID: %s", application_data.application_id)
        if applicant_pan in CibilScoreConstant.PAN_CIBIL_SCORE :
            new_score = score+50
            logger.info("Updated score : %s", new_score)
            return new_score
        if self.next:
            return self.next.handle(new_score, application_data)
        return new_score


