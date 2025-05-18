from pydantic import BaseModel, Field


class Employment(BaseModel):
    """Represents a single employment of an individual."""

    country_domiciled: str | None = Field(
        default=None, description="The country where the individual is domiciled."
    )
    resident_for_tax: str | None = Field(
        default=None,
        description="Indicates if the individual is a tax resident and in the domiciled country.",
    )
    national_insurance_number: str | None = Field(
        default=None,
        description="The individual's National Insurance number or equivalent tax identifier.",
    )
    employment_status: str | None = Field(
        default=None,
        description="The current employment status (e.g., employed, self-employed, unemployed).",
    )
    desired_retirement_age: int | None = Field(
        default=None,
        description="The age at which the individual ideally wishes to retire.",
    )
    occupation: str | None = Field(
        default=None, description="The individual's job title or profession."
    )
    employer: str | None = Field(
        default=None, description="The name of the current employer."
    )
    employment_started: str | None = Field(
        default=None,
        description="The start date of the current employment (DD-MM-YYYY format).",
    )
    highest_rate_of_tax_paid: str | None = Field(
        default=None,
        description="The highest marginal rate of income tax paid by the individual.",
    )
    notes: str | None = Field(
        default=None,
        description="Any additional relevant notes or details regarding employment.",
    )
    sources: list[str] = Field(
        default_factory=list,
        description="A list of the source Chunk ID's which contained the information you used to generate the content",
    )


class Employments(BaseModel):
    employments: list[Employment] = Field(
        default_factory=list,
        description="A list of employments associated with the given client.",
    )
