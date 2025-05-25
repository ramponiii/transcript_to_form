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

    @classmethod
    def get_retrieval_queries(cls):
        return ["savings", "investment accounts"]
