import random

from transcript_to_form.base_structured_extractor import StructuredExtractor
from transcript_to_form.modules.transcript.models import Conversation

from .padding_topics import PADDING_CONVERSATIONAL_TOPICS
from .prompts import SYSTEM, USER


class PaddingGenerator(StructuredExtractor):
    async def generate(
        self,
        conversation_start: Conversation,
        conversation_end: Conversation,
    ) -> Conversation:
        padding_choice = random.choice(PADDING_CONVERSATIONAL_TOPICS)
        response = await self._make_llm_call(
            SYSTEM,
            USER.format(
                padding_instructions=padding_choice,
                conversation_start=str(conversation_start),
                conversation_end=str(conversation_end),
            ),
            Conversation,
        )
        return response
