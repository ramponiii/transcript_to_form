from pydantic import BaseModel, Field


class OtherAsset(BaseModel):
    """Represents a non-standard asset."""

    owner: str | None = Field(
        default=None,
        description="The client who owns the asset .",
    )
    description: str | None = Field(
        default=None,
        description="A description of the asset (e.g., Classic Car, Art Collection, Jewellery).",
    )
    current_value: float | None = Field(
        default=None, description="The estimated current market value of the asset."
    )
    original_value: float | None = Field(
        default=None,
        description="The original purchase value or inherited value of the asset, if known.",
    )
