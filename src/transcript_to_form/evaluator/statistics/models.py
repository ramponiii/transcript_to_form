from pydantic import BaseModel


class SectionStats(BaseModel):
    filled_fields: int
    total_fields: int
    total_instances: int = 1

    @property
    def fill_percentage(self) -> float:
        if self.total_fields == 0:
            return 0.0
        return round((self.filled_fields / self.total_fields) * 100, 2)


class Statistics(BaseModel):
    employments: SectionStats
    health_details: SectionStats
    client_info: SectionStats
    incomes: SectionStats
    pensions: SectionStats
    savings_and_investments: SectionStats
    addresses: SectionStats
    dependents: SectionStats
    housing_expenses: SectionStats
    misc_expenses: SectionStats
    personal_expenses: SectionStats
    professional_expenses: SectionStats
    motoring_expenses: SectionStats
    loan_repayments: SectionStats
    loans_and_mortgages: SectionStats
    other_assets: SectionStats
    protection_policies: SectionStats


class SectionStatsDifference(BaseModel):
    """
    Represents the difference between two SectionStats objects,
    including percentages and their difference.
    """

    true_form_filled_fields_percentage: float
    predicted_form_filled_fields_percentage: float
    percentage_difference: float
    true_form_total_models: int
    pred_form_total_models: int


class StatisticsEval(BaseModel):
    """
    Represents the differences for all sections between two Statistics objects.
    """

    same_n_clients: bool
    employments: SectionStatsDifference
    health_details: SectionStatsDifference
    client_info: SectionStatsDifference
    incomes: SectionStatsDifference
    pensions: SectionStatsDifference
    savings_and_investments: SectionStatsDifference
    addresses: SectionStatsDifference
    dependents: SectionStatsDifference
    housing_expenses: SectionStatsDifference
    misc_expenses: SectionStatsDifference
    personal_expenses: SectionStatsDifference
    professional_expenses: SectionStatsDifference
    motoring_expenses: SectionStatsDifference
    loan_repayments: SectionStatsDifference
    loans_and_mortgages: SectionStatsDifference
    other_assets: SectionStatsDifference
    protection_policies: SectionStatsDifference
