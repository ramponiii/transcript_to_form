from pydantic import BaseModel, Field


class Dependent(BaseModel):
    """Represents a dependent individual."""

    name: str | None = Field(
        default=None, description="The full name of the dependent."
    )
    date_of_birth: str | None = Field(
        default=None,
        description="The date of birth of the dependent (DD-MM-YYYY format).",
    )
    dependent_until: str | None = Field(
        default=None,
        description="The date until which the individual is considered a dependent (DD-MM-YYYY format), if applicable.",
    )
    sources: list[str] = Field(
        default_factory=list,
        description="A list of the source Chunk ID's which contained the information you used to generate the content",
    )


class Dependents(BaseModel):
    dependents: list[Dependent] = Field(
        default_factory=list,
        description="A list of dependents associated with the client(s). These should not include the client(s) themselves.",
    )
