from pathlib import Path

from pydantic import BaseModel


class DialoguePair(BaseModel):
    advisor_message: str
    client_message: str

    def __str__(self) -> str:
        return f"Advisor: {self.advisor_message}\n\nClient: {self.client_message}"


class FieldValuePair(BaseModel):
    field: str
    value: str


class Conversation(BaseModel):
    conversation: list[DialoguePair]

    def __str__(self) -> str:
        return "\n\n".join([str(d) for d in self.conversation])

    def save(self, path: Path | str):
        with open(path, "w", encoding="utf-8") as file:
            file.write(self.model_dump_json(indent=4))


class ConversationWithFields(Conversation):
    populated_fields_based_on_transcript: dict[str, list[str] | str | int]

    def __str__(self) -> str:
        return "\n\n".join([str(d) for d in self.conversation])
