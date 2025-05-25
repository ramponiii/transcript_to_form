from pathlib import Path

from pydantic import BaseModel

from transcript_to_form.base_models import SavableBaseModel


class DialoguePair(BaseModel):
    advisor_message: str
    client_message: str

    def __str__(self) -> str:
        return f"ADVISOR: {self.advisor_message}\n\nCLIENT: {self.client_message}"


class FieldValuePair(BaseModel):
    field: str
    value: str


class Conversation(SavableBaseModel):
    conversation: list[DialoguePair]

    def __str__(self) -> str:
        return "\n\n".join([str(d) for d in self.conversation])


class ConversationWithFields(Conversation):
    populated_fields_based_on_transcript: dict[str, list[str] | str | int]

    def __str__(self) -> str:
        return "\n\n".join([str(d) for d in self.conversation])
