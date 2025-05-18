from pydantic import BaseModel

from .chunking.models import TranscriptChunk


class TranscriptChunkWithSurroundingContext(BaseModel):
    retrieved_chunk_idx: int
    chunks: list[TranscriptChunk]
