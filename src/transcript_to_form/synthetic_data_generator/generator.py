from transcript_to_form import logger
from transcript_to_form.llm import LLMClient

from .exceptions import SyntheticDataNotExtractedError, WrongNumberOfProducedChunksError
from .models import (
    SyntheticGenerationRequest,
    SyntheticTranscriptSegments,
)
from .prompts import SYSTEM, USER
from .settings import OPENAI_MODEL


class SyntheticDataGenerator:
    def __init__(
        self,
        llm_client: LLMClient,
    ) -> None:
        self.__llm_client = llm_client

    async def generate_example(
        self, request: SyntheticGenerationRequest
    ) -> SyntheticTranscriptSegments:
        model_str = str(request.model.model_fields)
        response = await self.__llm_client.parse(
            model=OPENAI_MODEL,
            input=[
                {"role": "system", "content": SYSTEM},
                {
                    "role": "user",
                    "content": USER.format(
                        field_with_context=model_str,
                        transcript_quality=request.transcript_quality,
                        specific_request=request.specific_request,
                        n_segments=request.n_segments,
                    ),
                },
            ],
            text_format=SyntheticTranscriptSegments,
        )
        pydantic_model: SyntheticTranscriptSegments | None = response.output_parsed

        if not pydantic_model:
            logger.error("Failed to create synthetic transcript segment")
            raise SyntheticDataNotExtractedError()

        if not len(pydantic_model.segments) == request.n_segments:
            logger.error(
                f"Synthetic data did not have the desired number of chunks. Wanted {request.n_segments}, got {len(pydantic_model.segments)}"
            )
            raise WrongNumberOfProducedChunksError()
        logger.debug("Generated synthetic example with the required number of segments")
        return pydantic_model
