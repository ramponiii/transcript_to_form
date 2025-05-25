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
from transcript_to_form.retrieval import TranscriptPineconeClient

from .prompts import SYSTEM, USER


class ClientExtractor(StructuredExtractor):
    """Given a transcript, produce a list of client names, and short descriptions, present in the text."""

    async def run(
        self, retriever: TranscriptPineconeClient, profiles: ClientShortProfiles
    ) -> list[Client]:
        clients: list[Client] = []
        async with asyncio.TaskGroup() as tg:
            profile_tasks = [
                tg.create_task(
                    self._extract_client_data_for_profile(profile, retriever)
                )
                for profile in profiles.profiles
            ]
        for task in profile_tasks:
            if client := await task:
                clients.append(client)
        return clients

    async def _extract_client_data_for_profile(
        self, profile: ClientShortProfile, retriever: TranscriptPineconeClient
    ) -> Client:
        health_details_transcript_subset = retriever.query(
            HealthDetails.get_retrieval_queries()
        )
        employment_transcript_subset = retriever.query(
            Employment.get_retrieval_queries()
        )
        ci_transcript_subset = retriever.query(
            ClientInformation.get_retrieval_queries()
        )

        async with asyncio.TaskGroup() as tg:
            health_details_task = tg.create_task(
                self.extract(
                    SYSTEM,
                    USER.format(
                        transcript=health_details_transcript_subset,
                        client_information=str(profile),
                    ),
                    HealthDetails,
                )
            )
            employments_task = tg.create_task(
                self.extract(
                    SYSTEM,
                    USER.format(
                        transcript=employment_transcript_subset,
                        client_information=str(profile),
                    ),
                    Employment,
                )
            )
            client_info_task = tg.create_task(
                self.extract(
                    SYSTEM,
                    USER.format(
                        transcript=ci_transcript_subset, client_information=str(profile)
                    ),
                    ClientInformation,
                )
            )
        return Client(
            health_details=health_details_task.result(),
            employments=[employments_task.result()],
            client_information=client_info_task.result(),
        )
