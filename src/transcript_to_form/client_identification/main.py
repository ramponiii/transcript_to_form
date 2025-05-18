from transcript_to_form import logger
from transcript_to_form.llm import LLMClient

from .exceptions import NoClientsIdentifiedError
from .models import ClientShortProfiles
from .prompts import SYSTEM, USER
from .settings import OPENAI_MODEL


class ClientIdentifier:
    """Given a transcript, produce a list of client names, and short descriptions, present in the text."""

    def __init__(self, llm_client: LLMClient):
        self.__llm_client = llm_client

    async def identify_clients(self, transcript: str) -> ClientShortProfiles:
        response = await self.__llm_client.parse(
            model=OPENAI_MODEL,
            input=[
                {"role": "system", "content": SYSTEM},
                {
                    "role": "user",
                    "content": USER.format(transcript=transcript),
                },
            ],
            text_format=ClientShortProfiles,
        )
        identified_clients = response.output_parsed
        if not identified_clients:
            logger.error("Failed to extract or identify clients")
            raise NoClientsIdentifiedError()
        else:
            logger.info(
                f"Extracted {len(identified_clients.profiles)} client(s) for transcript"
            )
            return identified_clients
