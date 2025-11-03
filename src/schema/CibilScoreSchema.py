from pydantic import  BaseModel, Field
from typing import Optional

class ApplicationRequest(BaseModel):
    application_id: int = Field(..., description="Application ID is required")
    pan_number: str = Field(..., description="PAN number is required")
    application_name: Optional[str] = None
    monthly_income_inr: int = Field(..., description="Monthly Income is required")
    loan_amount_inr: Optional[int] = None
    loan_type: str = Field(..., description="Loan Type is required")
    status: Optional[str] = None
    cibil_score: Optional[int] = None