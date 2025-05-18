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
    notes: str | None = Field(
        default=None,
        description="Any additional relevant notes or details regarding this income source.",
    )
    sources: list[str] = Field(
        default_factory=list,
        description="A list of the source Chunk ID's which contained the information you used to generate the content",
    )


class Incomes(BaseModel):
    incomes: list[Income] = Field(
        default_factory=list,
        description="A list of all income sources for the client(s).",
    )
