from src.DTO.ApplicationDataDTO import ApplicationDataDTO
from src.handler.CibilScoreHandler import CibilScoreHandler
from src.Constant.CibilScoreConstant import CibilScoreConstant
import logging

logger = logging.getLogger(__name__)


class CapHandler(CibilScoreHandler):

    def handle(self, score: int, application_data: ApplicationDataDTO) -> int:
        logger.info("CapHandler started processing for Application ID: %s", application_data.application_id)

        capped_score = max(CibilScoreConstant.MIN_CIBIL_SCORE ,min(CibilScoreConstant.MAX_CIBIL_SCORE, score))
        logger.info("Score after capping: %s", capped_score)
        if self.next:
            return self.next.handle(capped_score, application_data)
        return capped_score