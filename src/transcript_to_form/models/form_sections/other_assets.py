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
    notes: str | None = Field(
        default=None,
        description="Any additional relevant notes or details regarding this asset.",
    )
    sources: list[str] = Field(
        default_factory=list,
        description="A list of the source Chunk ID's which contained the information you used to generate the content",
    )


class OtherAssets(BaseModel):
    other_assets: list[OtherAsset] = Field(
        default_factory=list,
        description="A list of other significant assets owned by the client(s).",
    )
