import uuid
from enum import StrEnum
from typing import Type

from pydantic import BaseModel, ConfigDict, Field
from scipy import stats

from transcript_to_form.retrieval.chunking.models import SpeechLine

from ..retrieval.models import TranscriptChunk


class SyntheticTranscriptSegment(BaseModel):
    advisor_message: str
    client_message: str
    field_names_covered: list[str] = Field(
        default_factory=list[str],
        description="A list of the field names from the provided model which are covered by **THIS SPECIFIC** transcript chunk",
    )


class SyntheticTranscriptSegments(BaseModel):
    segments: list[SyntheticTranscriptSegment]

    def to_chunks(self, base_id: int) -> list[TranscriptChunk]:
        chunks = [
            TranscriptChunk(
                lines=[
                    SpeechLine(
                        speaker="ADVISOR",
                        timestamp=None,
                        dialogue=segment.advisor_message,
                    ),
                    SpeechLine(
                        speaker="CLIENT",
                        timestamp=None,
                        dialogue=segment.client_message,
                    ),
                ],
                chunk_index=base_id + i,
            )
            for i, segment in enumerate(self.segments)
        ]
        return chunks


class TranscriptQuality(StrEnum):
    HIGH = "HIGH"
    MEDIUM = "MEDIUM"
    LOW = "LOW"


class SamplerConfig(BaseModel):
    # in the future, specific config should be used per model
    # to allow for more representative sampling. For instance,
    # some fields are likely to be spread in far more chunks than others.
    models: list[Type[BaseModel]]

    specific_requests: list[
        str
    ]  # if you want to set specific user requests to sample from

    total_samples_per_model: int

    # control sampling of number of segments
    # discrete for ease right now
    segments_distribution: stats.rv_discrete

    # must sum to 1, should have pydantic validator added
    prop_high_quality: float
    prop_medium_quality: float
    prop_low_quality: float

    model_config = ConfigDict(arbitrary_types_allowed=True)


class SyntheticGenerationRequest(BaseModel):
    model: Type[BaseModel]
    transcript_quality: TranscriptQuality
    specific_request: str
    n_segments: int
    id: uuid.UUID = uuid.uuid4()


class SyntheticDataWithRequest(BaseModel):
    request: SyntheticGenerationRequest
    response: SyntheticTranscriptSegments
