import uuid

from pydantic import BaseModel


class SpeechLine(BaseModel):
    speaker: str
    timestamp: str | None
    dialogue: str


class TranscriptChunk(BaseModel):
    lines: list[SpeechLine]
    chunk_index: int
    id: uuid.UUID = uuid.uuid4()

    def __str__(self) -> str:
        return f"**Chunk ID [{self.chunk_index}]**" + "\n\n".join(
            f"{line.speaker}: [{line.timestamp}] {line.dialogue}" for line in self.lines
        )
