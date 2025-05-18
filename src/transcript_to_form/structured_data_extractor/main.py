from typing import Type

from pydantic import BaseModel

from transcript_to_form import logger
from transcript_to_form.client_identification.models import ClientShortProfiles
from transcript_to_form.llm import LLMClient
from transcript_to_form.models import MODEL_RETRIEVAL_QUERY_MAPPINGS
from transcript_to_form.retrieval.main import Retriever

from .exceptions import FieldNotExtractedError
from .prompts import SYSTEM, USER
from .settings import OPENAI_MODEL


class StructuredDataExtractor:
    def __init__(
        self,
        llm_client: LLMClient,
        retriever: Retriever,
        client_short_profiles: ClientShortProfiles,
    ):
        self.__llm_client = llm_client
        self.__retriever = retriever
        self._client_short_profiles = client_short_profiles.to_text()

    async def extract(
        self, desired_pydantic_model: Type[BaseModel], client_name: str | None = None
    ):
        logger.info(f"Extracting '{desired_pydantic_model.__name__}'...")
        guidance = (
            f"You will write about the specific client: {client_name}"
            if client_name
            else "You will write about information relating to either client."
        )

        # I will retrieve on each field's description (v1), concatenating the client_name if needed
        # we could use the structured transcript to perform a hybrid search, and in this way filter to
        # only content spoken by an individual (which may be useful) however I think it is highly likely
        # that client/s make speak on behalf of one another. Thus, I do not implement it here.
        query_client_name = f"{client_name}: " if client_name else ""

        queries = [
            f"{query_client_name}{q}"
            for q in MODEL_RETRIEVAL_QUERY_MAPPINGS[desired_pydantic_model]
        ]

        transcript = await self.__retriever.query_and_expand_context(
            queries,
            query_id=desired_pydantic_model.__name__,  # note: find something better than accessing dunder
            n_results=10,
            n_neighbors=10,
        )

        response = await self.__llm_client.parse(
            model=OPENAI_MODEL,
            input=[
                {"role": "system", "content": SYSTEM},
                {
                    "role": "user",
                    "content": USER.format(
                        transcript=transcript,
                        context=self._client_short_profiles,
                        guidance=guidance,
                    ),
                },
            ],
            text_format=desired_pydantic_model,
        )
        pydantic_model = response.output_parsed
        if not pydantic_model:
            logger.error(
                f'Failed to extract model of type "{desired_pydantic_model.__name__}"'
            )
            raise FieldNotExtractedError()
        else:
            return pydantic_model
