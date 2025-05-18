from pydantic import BaseModel, Field


class SavingOrInvestment(BaseModel):
    """Represents a single savings account or investment holding."""

    owner: str | None = Field(
        default=None,
        description="The client who owns the saving or investment.",
    )
    type: str | None = Field(
        default=None,
        description="The type of saving or investment (e.g., ISA, GIA, Bank Account, Investment Bond, Property).",
    )
    provider: str | None = Field(
        default=None,
        description="The financial institution or platform holding the saving or investment.",
    )
    value: float | None = Field(
        default=None, description="The current value of the saving or investment."
    )
    notes: str | None = Field(
        default=None,
        description="Any additional relevant notes or details regarding this saving or investment.",
    )
    sources: list[str] = Field(
        default_factory=list,
        description="A list of the source Chunk ID's which contained the information you used to generate the content",
    )


class SavingsAndInvestments(BaseModel):
    savings_and_investments: list[SavingOrInvestment] = Field(
        default_factory=list,
        description="A list of all savings accounts and investments for the client(s).",
    )
