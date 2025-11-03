from src.DTO.ApplicationDataDTO import ApplicationDataDTO
from src.schema.CibilScoreSchema import ApplicationRequest


class ApplicationDataMapper:

    @staticmethod
    def from_dict(data: ApplicationRequest) -> ApplicationDataDTO:

        return ApplicationDataDTO(
            application_id=data.application_id,
            pan_number=data.pan_number,
            application_name=data.application_name,
            monthly_income_inr=data.monthly_income_inr,
            loan_amount_inr=data.loan_amount_inr,
            loan_type=data.loan_type,
            status=data.status,
            cibil_score=data.cibil_score
        )
