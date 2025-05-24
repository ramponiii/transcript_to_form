from typing import Type, TypeVar

from openai import AsyncOpenAI
from pydantic import BaseModel

from .exceptions import NoModelExtractedError

T = TypeVar("T", bound=BaseModel)


class StructuredExtractor:
    def __init__(self, llm_client: AsyncOpenAI, model: str):
        self._llm_client = llm_client
        self.__model = model

    async def _make_llm_call(
        self, system_prompt: str, user_prompt: str, desired_model: Type[T]
    ) -> T:
        response = await self._llm_client.responses.parse(
            model=self.__model,
            input=[
                {"role": "system", "content": system_prompt},
                {
                    "role": "user",
                    "content": user_prompt,
                },
            ],
            text_format=desired_model,
        )
        output_model = response.output_parsed
        if not output_model:
            raise NoModelExtractedError()

        return output_model

    async def extract(
        self,
        system_prompt: str,
        user_prompt: str,
        desired_model: Type[T],
        max_retries: int = 1,
    ) -> T:
        current_system_prompt = system_prompt
        # at most 3 retries right now
        retry_messages = [
            "\n- try your best to return an object, even if it is entirely empty",
            "\n- remember - the content might not be there! Return an empty model if this is the case",
            "\n- this is your final attempt, try your best to return the desired model if the data exists",
        ]

        for attempt in range(max_retries + 1):
            try:
                return await self._make_llm_call(
                    current_system_prompt, user_prompt, desired_model
                )
            except NoModelExtractedError as e:
                if attempt < max_retries:
                    current_system_prompt = (
                        f"{system_prompt}\n{retry_messages[attempt]}"
                    )
                else:
                    raise NoModelExtractedError(
                        f"Failed to extract model after {max_retries + 1} attempts. Last parsing error: {e}"
                    ) from e
            except Exception as e:
                if attempt < max_retries:
                    current_system_prompt = (
                        f"{system_prompt}\n{retry_messages[attempt]}"
                    )
                else:
                    raise NoModelExtractedError(
                        f"An unexpected error prevented model extraction after {max_retries + 1} attempts. Last error: {e}"
                    ) from e

        raise NoModelExtractedError(
            "Unhandled state: Model extraction logic completed without return or exception."
        )
