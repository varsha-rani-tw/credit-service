"""
Router for CIBIL score simulation endpoints.
"""
import logging
from fastapi import Depends, HTTPException, APIRouter
from dependency_injector.wiring import inject, Provide
from pydantic import BaseModel
from typing import Optional

from src.schema.CibilScoreSchema import ApplicationRequest
from src.service.CibilScoreService import CibilScoreService
from src.mapper.ApplicationDataMapper import ApplicationDataMapper
from src.kafka.kafka_producer import KafkaProducerService
from src.containers import Container


logger = logging.getLogger(__name__)
router = APIRouter(tags=["cibil-score"])


class CibilScoreResponse(BaseModel):
    """Response model for CIBIL score simulation."""
    application_id: int
    cibil_score: int
    status: str
    message: str


@router.post("/simulate-cibil-score", response_model=CibilScoreResponse)
@inject
async def simulate_score(
    app_data: ApplicationRequest,
    service: CibilScoreService = Depends(Provide[Container.cibil_service]),
    mapper: ApplicationDataMapper = Depends(Provide[Container.application_data_mapper]),
    kafka_producer: KafkaProducerService = Depends(Provide[Container.kafka_producer])
):

    try:
        application_data_dto = mapper.from_dict(app_data)

        calculated_score = service.simulate(application_data_dto)

        logger.info(
            f"CIBIL score calculated for application {application_data_dto.application_id}: {calculated_score}"
        )

        kafka_message = {
            "application_id": application_data_dto.application_id,
            "pan_number": application_data_dto.pan_number,
            "application_name": application_data_dto.application_name,
            "monthly_income_inr": application_data_dto.monthly_income_inr,
            "loan_amount_inr": application_data_dto.loan_amount_inr,
            "loan_type": application_data_dto.loan_type,
            "status": application_data_dto.status or "pending",
            "cibil_score": calculated_score,
            "calculated_cibil_score": calculated_score,
        }

        kafka_success = await kafka_producer.publish_loan_application(kafka_message)

        if not kafka_success:
            logger.warning(
                f"Failed to publish application {application_data_dto.application_id} to Kafka, "
                "but returning calculated score"
            )

        return CibilScoreResponse(
            application_id=application_data_dto.application_id,
            cibil_score=calculated_score,
            status="success" if kafka_success else "partial_success",
            message=(
                "CIBIL score calculated and published to Kafka successfully"
                if kafka_success
                else "CIBIL score calculated but Kafka publishing failed"
            )
        )

    except Exception as e:
        logger.exception(f"Error during CIBIL score simulation: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Internal server error during CIBIL score simulation: {str(e)}"
        )