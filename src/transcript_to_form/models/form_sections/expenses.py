from pydantic import BaseModel, Field


class Expense(BaseModel):
    """Represents a single financial expense."""

    owner: str | None = Field(
        default=None,
        description="The owner responsible for the expense (e.g., client, spouse).",
    )
    name: str | None = Field(
        default=None,
        description="A descriptive name for the expense (e.g., Mortgage Payment, Car Insurance, Groceries).",
    )
    amount: float | None = Field(default=None, description="The value of the expense.")
    frequency: str | None = Field(
        default=None,
        description="The frequency at which the expense occurs (e.g., Monthly, Annually, Weekly, One-time).",
    )
    priority: str | None = Field(
        default=None,
        description="The priority level of the expense (e.g., Essential, Discretionary, Important).",
    )
    timeframe: str | None = Field(
        default=None,
        description="Specifies the period the expense relates to, if not ongoing (e.g., 'until 2035').",
    )
    notes: str | None = Field(
        default=None,
        description="Any additional relevant notes or details regarding this expense.",
    )
    sources: list[str] = Field(
        default_factory=list,
        description="A list of the source Chunk ID's which contained the information you used to generate the content",
    )


class Expenses(BaseModel):
    loan_repayments: list[Expense] = Field(
        default_factory=list,
        description="A list of expenses related to loan repayments (e.g., mortgage, personal loans, student loans).",
    )
    housing_expenses: list[Expense] = Field(
        default_factory=list,
        description="A list of expenses related to housing (e.g., rent, mortgage payments, property taxes, insurance, utilities).",
    )
    motoring_expenses: list[Expense] = Field(
        default_factory=list,
        description="A list of expenses related to vehicles (e.g., car payments, insurance, fuel, maintenance, taxes).",
    )
    personal_expenses: list[Expense] = Field(
        default_factory=list,
        description="A list of general personal living expenses (e.g., groceries, clothing, entertainment, healthcare, subscriptions).",
    )
    professional_expenses: list[Expense] = Field(
        default_factory=list,
        description="A list of expenses related to one's profession or business (e.g., professional body fees, training costs, business travel).",
    )
    misc_expenses: list[Expense] = Field(
        default_factory=list,
        description="A list of miscellaneous expenses that do not fit into other categories.",
    )
