from typing import Type

from pydantic import BaseModel

from transcript_to_form.models import (
    Address,
    ClientInformation,
    Dependent,
    Employment,
    HealthDetails,
    HousingExpense,
    Income,
    LoanOrMortgage,
    LoanRepayment,
    MiscExpense,
    MotoringExpense,
    OtherAsset,
    Pension,
    PersonalExpense,
    ProfessionalExpense,
    ProtectionPolicy,
    SavingOrInvestment,
)

MODEL_TYPES = Type[
    Address
    | ClientInformation
    | Dependent
    | Employment
    | HealthDetails
    | HousingExpense
    | Income
    | LoanOrMortgage
    | LoanRepayment
    | MiscExpense
    | MotoringExpense
    | OtherAsset
    | Pension
    | PersonalExpense
    | ProfessionalExpense
    | ProtectionPolicy
    | SavingOrInvestment
]


class ModelWithDesiredCount(BaseModel):
    model: MODEL_TYPES
    count: int = 1


class TranscriptGenerationConfig(BaseModel):
    persona_description: str | None = None
    models: list[ModelWithDesiredCount]
    id: str = "unnamed"
