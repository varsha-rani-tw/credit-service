import logging
from fastapi import Depends, HTTPException, APIRouter
from dependency_injector.wiring import inject, Provide

from src.schema.CibilScoreSchema import ApplicationRequest
from src.service.CibilScoreService import CibilScoreService
from src.mapper.ApplicationDataMapper import ApplicationDataMapper
from src.containers import Container


logger = logging.getLogger(__name__)
router = APIRouter(tags=["cibil-score"])


@router.post("/simulate-cibil-score")
@inject
async def simulate_score(
    app_data: ApplicationRequest,
    service: CibilScoreService = Depends(Provide[Container.cibil_service]),
    mapper: ApplicationDataMapper = Depends(Provide[Container.application_data_mapper])
):

    try:
        application_data_dto = mapper.map_application_data_dto(app_data)

        calculated_score = service.simulate(application_data_dto)

        logger.info(
            f"CIBIL score calculated for application {application_data_dto.application_id}: {calculated_score}"
        )

    except Exception as e:
        logger.exception(f"Error during CIBIL score simulation: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Internal server error during CIBIL score simulation: {str(e)}"
        )