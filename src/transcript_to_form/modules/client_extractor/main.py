import asyncio

from transcript_to_form.base_structured_extractor import StructuredExtractor
from transcript_to_form.models import (
    Client,
    ClientInformation,
    Employment,
    HealthDetails,
)
from transcript_to_form.modules.client_identifier.models import (
    ClientShortProfile,
    ClientShortProfiles,
)

from .prompts import SYSTEM, USER


class ClientExtractor(StructuredExtractor):
    """Given a transcript, produce a list of client names, and short descriptions, present in the text."""

    async def run(self, transcript: str, profiles: ClientShortProfiles) -> list[Client]:
        clients: list[Client] = []
        async with asyncio.TaskGroup() as tg:
            profile_tasks = [
                tg.create_task(
                    self._extract_client_data_for_profile(profile, transcript)
                )
                for profile in profiles.profiles
            ]
        for task in profile_tasks:
            if client := await task:
                clients.append(client)
        return clients

    async def _extract_client_data_for_profile(
        self, profile: ClientShortProfile, transcript: str
    ) -> Client:
        POPULATED_USER_PROMPT = USER.format(
            transcript=transcript, client_information=str(profile)
        )
        async with asyncio.TaskGroup() as tg:
            health_details_task = tg.create_task(
                self.extract(SYSTEM, POPULATED_USER_PROMPT, HealthDetails)
            )
            employments_task = tg.create_task(
                self.extract(SYSTEM, POPULATED_USER_PROMPT, Employment)
            )
            client_info_task = tg.create_task(
                self.extract(SYSTEM, POPULATED_USER_PROMPT, ClientInformation)
            )
        return Client(
            health_details=health_details_task.result(),
            employments=[employments_task.result()],
            client_information=client_info_task.result(),
        )
