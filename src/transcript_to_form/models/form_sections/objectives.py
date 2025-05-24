from pydantic import BaseModel, Field


class Objectives(BaseModel):
    """Represents the key objectives or goals for a financial planning session."""

    objectives: list[str] = Field(
        default_factory=list,
        description="A list of specific goals or topics the client(s) wish to discuss or achieve during the session.",
    )
