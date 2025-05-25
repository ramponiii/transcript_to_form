from pydantic import BaseModel, Field


class Dependent(BaseModel):
    """Represents a dependent individual ."""

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

    @classmethod
    def get_retrieval_queries(cls):
        return ["children or dependents"]
