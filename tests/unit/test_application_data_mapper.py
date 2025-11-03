from src.DTO.ApplicationDataDTO import ApplicationDataDTO
from src.schema.CibilScoreSchema import ApplicationRequest


class TestApplicationDataMapper:

    def test_from_dict_with_complete_data(self, application_mapper):
        request = ApplicationRequest(
            application_id=1,
            pan_number="ABCDE1234F",
            application_name="John Doe",
            monthly_income_inr=50000,
            loan_amount_inr=500000,
            loan_type="HOME",
            status="pending",
            cibil_score=700
        )

        result = application_mapper.from_dict(request)

        assert isinstance(result, ApplicationDataDTO)
        assert result.application_id == 1
        assert result.pan_number == "ABCDE1234F"
        assert result.application_name == "John Doe"
        assert result.monthly_income_inr == 50000
        assert result.loan_amount_inr == 500000
        assert result.loan_type == "HOME"
        assert result.status == "pending"
        assert result.cibil_score == 700

    def test_from_dict_with_missing_optional_fields(self, application_mapper):
        request = ApplicationRequest(
            application_id=1,
            pan_number="ABCDE1234F",
            monthly_income_inr=50000,
            loan_type="HOME"
        )

        result = application_mapper.from_dict(request)

        assert isinstance(result, ApplicationDataDTO)
        assert result.application_id == 1
        assert result.pan_number == "ABCDE1234F"
        assert result.application_name is None
        assert result.monthly_income_inr == 50000
        assert result.loan_amount_inr is None
        assert result.loan_type == "HOME"
        assert result.status is None
        assert result.cibil_score is None

    def test_from_dict_with_different_data_types(self, application_mapper):

        request = ApplicationRequest(
            application_id=12345,
            pan_number="ABCDE1234F",
            application_name="Jane Doe",
            monthly_income_inr=75000,
            loan_amount_inr=1000000,
            loan_type="PERSONAL",
            status="approved",
            cibil_score=750
        )


        result = application_mapper.from_dict(request)

        assert isinstance(result.application_id, int)
        assert isinstance(result.pan_number, str)
        assert isinstance(result.application_name, str)
        assert isinstance(result.loan_type, str)
        assert isinstance(result.status, str)

