import random
from typing import Type, TypeVar

from pydantic import BaseModel

from transcript_to_form import logger
from transcript_to_form.base_structured_extractor import StructuredExtractor
from transcript_to_form.transcript_generator.modules.models import Conversation

from .advisor_message_beginnings import (
    ADVISOR_MESSAGE_BEGINNINGS,
)
from .models import Verification, VerificationWithReasoning
from .prompts import (
    SYSTEM,
    SYSTEM_MODEL,
    SYSTEM_VERIFICATION,
    USER,
    USER_MODEL,
    USER_VERIFICATION,
)
from .specific_requests import SPECIFIC_REQUESTS

T = TypeVar("T", bound=BaseModel)


class ContentSectionGenerator(StructuredExtractor):
    async def generate(
        self, desired_model: Type[T], background: str, n_models_to_generate: int = 1
    ) -> tuple[Conversation, list[T] | None]:
        # produce the model/s
        model_name = desired_model.__name__
        additional_guidance = ""
        models: list[T] = []
        for _ in range(n_models_to_generate):
            model_response = await self._make_llm_call(
                SYSTEM_MODEL,
                USER_MODEL.format(
                    background=background,
                    additional_guidance=additional_guidance,
                    model_name=model_name,
                ),
                desired_model,
            )
            additional_guidance += f"\n\nI've already got the following information for the section: {model_response.model_dump_json()} - so please provide another model which is diverse and a bit different!"
            models.append(model_response)

        required_models_as_str = "\n\n".join(
            model.model_dump_json() for model in models
        )

        # produce the transcript
        transcript_response = await self._make_llm_call(
            SYSTEM,
            USER.format(
                background=background,
                model=required_models_as_str,
                model_name=model_name,
                specific_request=random.choice(SPECIFIC_REQUESTS),
                advisor_message_begin=random.choice(ADVISOR_MESSAGE_BEGINNINGS),
            ),
            Conversation,
        )

        # verify the trancsript contains all the required info. If it doesn't this will return lines to append to the end to ensure all information is contained.
        verified = await self._make_llm_call(
            SYSTEM_VERIFICATION,
            USER_VERIFICATION.format(
                transcript=str(transcript_response),
                model=required_models_as_str,
                model_name=model_name,
            ),
            VerificationWithReasoning,
        )

        # TODO: handle properly, skipping verification on client info
        if (
            not verified.verification == Verification.ALL_INFORMATION_CONTAINED
            and model_name != "ClientInformation"
        ):
            logger.error(f"failed to generate, {verified.reasoning}")
            return Conversation(conversation=[]), []

        return transcript_response, models
