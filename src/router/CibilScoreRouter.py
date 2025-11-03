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
    """
    Simulate CIBIL score for a loan application.

    This endpoint:
    1. Receives application data
    2. Calculates CIBIL score using the handler chain
    3. Publishes the result to Kafka topic 'loan_applications_submitted'
    4. Returns the calculated score

    Args:
        app_data: Application request data
        service: Injected CibilScoreService
        mapper: Injected ApplicationDataMapper
        kafka_producer: Injected KafkaProducerService

    Returns:
        CibilScoreResponse with calculated score

    Raises:
        HTTPException: If simulation or Kafka publishing fails
    """
    try:
        # Step 1: Map request to DTO
        application_data_dto = mapper.from_dict(app_data)

        # Step 2: Calculate CIBIL score
        calculated_score = service.simulate(application_data_dto)

        logger.info(
            f"CIBIL score calculated for application {application_data_dto.application_id}: {calculated_score}"
        )

        # Step 3: Prepare message for Kafka
        kafka_message = {
            "application_id": application_data_dto.application_id,
            "pan_number": application_data_dto.pan_number,
            "application_name": application_data_dto.application_name,
            "monthly_income_inr": application_data_dto.monthly_income_inr,
            "loan_amount_inr": application_data_dto.loan_amount_inr,
            "loan_type": application_data_dto.loan_type,
            "status": application_data_dto.status or "pending",
            "cibil_score": calculated_score,
            "calculated_cibil_score": calculated_score,  # Explicitly show calculated score
        }

        # Step 4: Publish to Kafka
        kafka_success = await kafka_producer.publish_loan_application(kafka_message)

        if not kafka_success:
            logger.warning(
                f"Failed to publish application {application_data_dto.application_id} to Kafka, "
                "but returning calculated score"
            )

        # Step 5: Return response
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