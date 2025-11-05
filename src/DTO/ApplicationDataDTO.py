from uuid import UUID

class ApplicationDataDTO:

    application_id: UUID
    pan_number: str
    application_name: str
    monthly_income_inr : float
    loan_amount_inr: float
    loan_type: str
    status: str
    cibil_score: int

    def __init__(self, application_id, pan_number, application_name, monthly_income_inr, loan_amount_inr, loan_type, status, cibil_score ):
        self.application_id = application_id
        self.pan_number = pan_number
        self.application_name = application_name
        self.monthly_income_inr = monthly_income_inr
        self.loan_amount_inr = loan_amount_inr
        self.loan_type = loan_type
        self.status = status
        self.cibil_score = cibil_score




