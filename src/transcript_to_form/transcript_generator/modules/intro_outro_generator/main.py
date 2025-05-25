from transcript_to_form.base_structured_extractor import StructuredExtractor
from transcript_to_form.transcript_generator.modules.models import Conversation

from .prompts import SYSTEM, USER_INTRO, USER_OUTRO


class IntroGenerator(StructuredExtractor):
    async def generate(self, transcript: str) -> Conversation:
        response = await self._make_llm_call(
            SYSTEM,
            USER_INTRO.format(transcript=transcript),
            Conversation,
        )
        return response


class OutroGenerator(StructuredExtractor):
    async def generate(self, transcript: str) -> Conversation:
        response = await self._make_llm_call(
            SYSTEM,
            USER_OUTRO.format(transcript=transcript),
            Conversation,
        )
        return response
