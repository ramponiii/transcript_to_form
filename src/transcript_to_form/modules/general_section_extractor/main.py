import asyncio
import json
from typing import Type

from transcript_to_form import logger
from transcript_to_form.base_structured_extractor import StructuredExtractor, T
from transcript_to_form.modules.client_identifier.models import (
    ClientShortProfiles,
)

from .model_extractor_prompts import SYSTEM_EXTRACT, USER_EXTRACT
from .models import ExtractionPreview, VerifiedExtraction
from .summary_extractor_prompts import SYSTEM_SUMMARY, USER_SUMMARY
from .verification_prompts import SYSTEM_VERIFICATION, USER_VERIFICATION

# SUPER LAZY using full transcripts, this is beyond not optimal...
# just wanted something simpler to work with and planned to re-introduce retrieval
# system but ran out of time


class GeneralSectionExtractor(StructuredExtractor):
    """Given a transcript, produce a list of client names, and short descriptions, present in the text."""

    async def run(
        self, transcript: str, profiles: ClientShortProfiles, model: Type[T]
    ) -> list[T]:
        profiles_str = str(profiles)
        summary = await self.extract(
            SYSTEM_SUMMARY,
            USER_SUMMARY.format(
                transcript=transcript,
                client_information=str(profiles),
                model=json.dumps(model().model_json_schema()),
                model_name=model.__name__,
            ),
            ExtractionPreview,
        )
        logger.debug(f"Successfully got extraction preview: {summary}")
        if len(summary.items_to_extract) == 0:
            return []

        models = await self._produce_models_from_summary(
            transcript, profiles_str, model, summary
        )

        # now , verification, if we have models to verify. Should this content be somewhere else? Is any of it un-substantiated?
        if len(models) > 0:
            models = await self._check_extraction(models, transcript)

        return models

    async def _check_extraction(self, extraction: list[T], transcript: str) -> list[T]:
        required_models_as_str = "\n\n".join(
            f"[{index}] {model.model_dump_json()}"
            for index, model in enumerate(extraction)
        )
        model_str = type(extraction[0]).__name__
        # currently, this cannot remove singular fields from an instance, it just removes whole instances.
        extraction_check_results = await self.extract(
            SYSTEM_VERIFICATION,
            USER_VERIFICATION.format(
                transcript=transcript,
                models=required_models_as_str,
                section=model_str,
            ),
            VerifiedExtraction,
        )

        verified_models: list[T] = []
        for check in extraction_check_results.results:
            if check.valid:
                verified_models.append(extraction[check.index])
            else:
                logger.warning(
                    f"Content deemed to be invalid... for model `{model_str}` got reasoning: '{check.reasoning}'"
                )
                continue

        return verified_models

    async def _produce_models_from_summary(
        self,
        transcript: str,
        profiles: str,
        model: Type[T],
        extraction_summary: ExtractionPreview,
    ) -> list[T]:
        tasks = [
            self.extract(
                SYSTEM_EXTRACT,
                USER_EXTRACT.format(
                    transcript=transcript,
                    client_information=profiles,
                    all_items=str(extraction_summary),
                    item_to_extract=str(item),
                    model_name=model.__name__,
                ),
                model,
            )
            for item in extraction_summary.items_to_extract
        ]
        results = await asyncio.gather(*tasks)
        return results
