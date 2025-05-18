from pydantic import BaseModel, Field


class Pension(BaseModel):
    """Represents a single pension policy or arrangement."""

    owner: str | None = Field(
        default=None,
        description="The client who owns the pension policy.",
    )
    type: str | None = Field(
        default=None,
        description="The type of pension (e.g., Defined Contribution, Defined Benefit, SIPP, State Pension).",
    )
    provider: str | None = Field(
        default=None,
        description="The financial institution or scheme providing the pension.",
    )
    value: float | None = Field(
        default=None,
        description="The current value or estimated value of the pension fund.",
    )
    policy_number: str | None = Field(
        default=None, description="The policy or account number for the pension."
    )
    notes: str | None = Field(
        default=None,
        description="Any additional relevant notes or details regarding this pension.",
    )
    sources: list[str] = Field(
        default_factory=list,
        description="A list of the source Chunk ID's which contained the information you used to generate the content",
    )


class Pensions(BaseModel):
    pensions: list[Pension] = Field(
        default_factory=list,
        description="A list of all pension policies for the client(s).",
    )
