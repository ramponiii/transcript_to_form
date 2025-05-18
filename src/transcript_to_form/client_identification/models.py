from pydantic import BaseModel, Field


class ClientShortProfile(BaseModel):
    name: str = Field(..., description="Name of the client")
    description: str | None = Field(None, description="Short description of the client")
    alias: str = Field(
        ...,
        description="The reference used in the transcription to indicate when the client is talking.",
    )


class ClientShortProfiles(BaseModel):
    profiles: list[ClientShortProfile] = Field(
        ..., description="List of client profiles"
    )

    # could define as __str__ or repr, I prefer this as it is more explicit
    def to_text(self):
        client_profiles = [
            f"Name:{p.name}\nDescription:{p.description}\nAlias:{p.alias}"
            for p in self.profiles
        ]

        return f"{'\n\n'.join(client_profiles)}"
