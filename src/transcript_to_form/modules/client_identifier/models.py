from pydantic import BaseModel, Field


class ClientShortProfile(BaseModel):
    name: str = Field(..., description="Name of the client")
    description: str | None = Field(None, description="Short description of the client")
    employments: list[str] = Field(
        default_factory=list,
        description="A list of employments associated with the client, just include job title + organisation",
    )
    alias: str = Field(
        ...,
        description="The reference used in the transcription to indicate when the client is talking.",
    )

    def __str__(self) -> str:
        return f"Name: {self.name} (alias: {self.alias})\nDesc: {self.description}\nIdentified Employments{', '.join(self.employments)}"


class ClientShortProfiles(BaseModel):
    profiles: list[ClientShortProfile] = Field(
        ..., description="List of client profiles"
    )

    def __str__(self) -> str:
        return "\n\n".join(str(x) for x in self.profiles)
