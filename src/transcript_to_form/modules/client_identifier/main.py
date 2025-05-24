from transcript_to_form.base_structured_extractor import StructuredExtractor

from .models import ClientShortProfiles
from .prompts import SYSTEM, USER


class ClientIdentifier(StructuredExtractor):
    """Given a transcript, produce a list of client names, and short descriptions, present in the text."""

    async def run(self, transcript: str) -> ClientShortProfiles:
        response = await self.extract(
            SYSTEM, USER.format(transcript=transcript), ClientShortProfiles
        )
        return response
