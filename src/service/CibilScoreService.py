from src.Constant.CibilScoreConstant import CibilScoreConstant
from src.DTO.ApplicationDataDTO import ApplicationDataDTO
from src.handler.CapHandler import CapHandler
from src.handler.CibilScoreHandler import CibilScoreHandler
from src.handler.IncomeHandler import IncomeHandler
from src.handler.LoanTypeHandler import LoanTypeHandler
from src.handler.PanHandler import PanHandler
from src.handler.RandomHandler import RandomHanlder


class CibilScoreService:

    def __init__(
        self,
        pan_handler: PanHandler,
        income_handler: IncomeHandler,
        loan_handler: LoanTypeHandler,
        random_handler: RandomHanlder,
        cap_handler: CapHandler
    ):

        self.pan_handler = pan_handler
        self.income_handler = income_handler
        self.loan_handler = loan_handler
        self.random_handler = random_handler
        self.cap_handler = cap_handler
        self.chain = self.build_chain()

    def build_chain(self) -> CibilScoreHandler:

        self.pan_handler.set_next(self.income_handler)\
            .set_next(self.loan_handler)\
            .set_next(self.random_handler)\
            .set_next(self.cap_handler)
        return self.pan_handler


    def simulate(self, application_data: ApplicationDataDTO):
        intial_cibil_score =  CibilScoreConstant.BASE_CIBIL_SCORE
        final_cibil_score = self.chain.handle(intial_cibil_score,application_data)
        return final_cibil_score






