from pydantic import BaseModel, Field


class Income(BaseModel):
    """Represents a single source of income."""

    owner: str | None = Field(
        default=None, description="The client who owns the income."
    )
    name: str | None = Field(
        default=None,
        description="A descriptive name for the income source (e.g., Salary, Rental Income, Pension).",
    )
    amount: float | None = Field(default=None, description="The value of the income.")
    frequency: str | None = Field(
        default=None,
        description="The frequency at which the income is received (e.g., Monthly, Annually, Weekly).",
    )
    net_gross: str | None = Field(
        default=None,
        description="Indicates whether the income amount is Net (after tax) or Gross (before tax).",
    )
    timeframe: str | None = Field(
        default=None,
        description="Specifies the period the income relates to, if not ongoing (e.g., 'until 2030').",
    )
