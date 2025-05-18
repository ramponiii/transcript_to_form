from pydantic import BaseModel, Field

from .client import Client
from .form_sections.address import Addresses
from .form_sections.dependents import Dependents
from .form_sections.expenses import Expenses
from .form_sections.incomes import Incomes
from .form_sections.loan_and_mortgages import LoansAndMortgages
from .form_sections.objectives import Objectives
from .form_sections.other_assets import OtherAssets
from .form_sections.pensions import Pensions
from .form_sections.protection_policies import ProtectionPolicies
from .form_sections.saving_and_investments import (
    SavingsAndInvestments,
)


# note: a loan may appear as both an 'expense' and under 'loans and mortgages' currently.
class Form(BaseModel):
    """Represents the complete financial data form for a client session."""

    clients: list[Client] = Field(
        default_factory=list,
        description="A list of clients associated with this form and associated information.",
    )

    addresses: Addresses
    dependents: Dependents
    incomes: Incomes
    expenses: Expenses
    pensions: Pensions
    savings_and_investments: SavingsAndInvestments
    other_assets: OtherAssets
    loans_and_mortgages: LoansAndMortgages
    protection_policies: ProtectionPolicies
    objectives: Objectives
