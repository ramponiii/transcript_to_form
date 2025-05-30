from pydantic import BaseModel, Field


class ClientInformation(BaseModel):
    """Represents information pertaining to a specific client."""

    title: str | None = Field(
        None, description="The person's title (e.g., Mr, Ms, Dr)."
    )
    first_name: str | None = Field(None, description="The person's first name.")
    middle_names: list[str] = Field(
        default_factory=list, description="A list of the person's middle names."
    )
    last_name: str | None = Field(None, description="The person's last name.")
    known_as: str | None = Field(
        None, description="The name the person is commonly known as."
    )
    pronouns: str | None = Field(
        None,
        description="The person's preferred pronouns (e.g., she/her, he/him, they/them).",
    )
    date_of_birth: str | None = Field(
        None, description="The person's date of birth, (DD-MM-YYYY format)."
    )
    place_of_birth: str | None = Field(None, description="The person's place of birth.")
    nationality: str | None = Field(None, description="The person's nationality.")
    gender: str | None = Field(None, description="The person's gender identity.")
    legal_sex: str | None = Field(None, description="The person's legal sex.")
    marital_status: str | None = Field(
        None,
        description="The person's marital status (e.g., Single, Married, Divorced).",
    )
    home_phone: str | None = Field(None, description="The person's home phone number.")
    mobile_phone: str | None = Field(
        None, description="The person's mobile phone number."
    )
    email_address: str | None = Field(None, description="The person's email address.")

    @classmethod
    def get_retrieval_queries(cls):
        return [
            "client information (name, gender etc)",
            "client phone number and email",
        ]
