from pydantic import Field

from transcript_to_form.base_models import SavableBaseModel

from .client import Client
from .form_sections.address import Address
from .form_sections.dependent import Dependent
from .form_sections.expenses import Expenses
from .form_sections.income import Income
from .form_sections.loan_or_mortgage import LoanOrMortgage
from .form_sections.objectives import Objectives
from .form_sections.other_asset import OtherAsset
from .form_sections.pension import Pension
from .form_sections.protection_policy import ProtectionPolicy
from .form_sections.saving_or_investment import SavingOrInvestment


class Form(SavableBaseModel):
    """Represents the complete financial data form for a client session."""

    clients: list[Client] = Field(
        default_factory=list,
        description="A list of clients associated with this form and associated information.",
    )

    addresses: list[Address] | None
    dependents: list[Dependent] | None
    incomes: list[Income] | None
    expenses: Expenses | None
    pensions: list[Pension] | None
    savings_and_investments: list[SavingOrInvestment] | None
    other_assets: list[OtherAsset] | None
    loans_and_mortgages: list[LoanOrMortgage] | None
    protection_policies: list[ProtectionPolicy] | None
    objectives: Objectives | None
