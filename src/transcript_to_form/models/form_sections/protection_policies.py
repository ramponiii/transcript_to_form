from pydantic import BaseModel, Field


class ProtectionPolicy(BaseModel):
    """Represents a single protection policy (e.g., Life Insurance, Income Protection)."""

    owner: str | None = Field(
        default=None,
        description="The client who ownes the policy or is life assured by the policy.",
    )
    type: str | None = Field(
        default=None,
        description="The type of protection policy (e.g., Life Assurance, Critical Illness Cover, Income Protection, Family Income Benefit).",
    )
    provider: str | None = Field(
        default=None, description="The insurance company providing the policy."
    )
    monthly_cost: float | None = Field(
        default=None, description="The regular monthly premium for the policy."
    )
    amount_assured: float | None = Field(
        default=None, description="The payout amount or sum assured by the policy."
    )
    in_trust: bool | None = Field(
        default=None,
        description="Indicates if the policy is written in trust (True/False/None).",
    )
    assured_until: str | None = Field(
        default=None,
        description="The date or condition until which the cover is provided (e.g., '2040-12-31', 'Retirement').",
    )
    notes: str | None = Field(
        default=None,
        description="Any additional relevant notes or details regarding this policy.",
    )
    objectives: str | None = Field(
        default=None,
        description="The purpose or objective that this protection policy is intended to meet.",
    )
    sources: list[str] = Field(
        default_factory=list,
        description="A list of the source Chunk ID's which contained the information you used to generate the content",
    )


class ProtectionPolicies(BaseModel):
    protection_policies: list[ProtectionPolicy] = Field(
        default_factory=list,
        description="A list of all protection policies (e.g., life insurance) for the client(s).",
    )
