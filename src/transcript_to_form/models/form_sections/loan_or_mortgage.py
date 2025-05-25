from pydantic import BaseModel, Field


class LoanOrMortgage(BaseModel):
    """Represents a single loan or mortgage."""

    owner: str | None = Field(
        default=None,
        description="The client responsible for the loan or mortgage.",
    )
    type: str | None = Field(
        default=None,
        description="The type of loan or mortgage (e.g., Mortgage, Personal Loan, Car Finance, Credit Card).",
    )
    provider: str | None = Field(
        default=None,
        description="The financial institution or lender providing the loan or mortgage.",
    )
    monthly_cost: float | None = Field(
        default=None,
        description="The regular monthly payment amount for the loan or mortgage.",
    )
    outstanding_value: float | None = Field(
        default=None,
        description="The current outstanding balance on the loan or mortgage.",
    )
    interest_rate: float | None = Field(
        default=None,
        description="The current standard interest rate applied to the loan or mortgage (as a percentage).",
    )
    special_rate: str | None = Field(
        default=None,
        description="Details of any special interest rate period (e.g., '2.5% fixed until 2030').",
    )
    final_payment: str | None = Field(
        default=None,
        description="The date of the final scheduled payment or loan end date (e.g., YYYY-MM-DD).",
    )

    @classmethod
    def get_retrieval_queries(cls):
        return ["mortgage", "client loans"]
