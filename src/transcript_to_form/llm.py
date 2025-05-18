import asyncio
from typing import Any

import openai
from openai.types.responses import ParsedResponse
from pydantic import BaseModel, Field

from transcript_to_form import logger

# NOTE: this is hacky and not robust, e.g. if someone tried a different method on the LLM client.
# also the async lock feels a bit messy
# the reason for this is I want an easy way to see costing of dataset production, and of running on a given transcript.


class ModelTokenUsage(BaseModel):
    total_cached_input_tokens: int = Field(default=0)
    total_not_cached_input_tokens: int = Field(default=0)
    total_output_tokens: int = Field(default=0)

    cached_input_tokens_price_per_million: float
    not_cached_input_tokens_price_per_million: float
    output_tokens_tokens_price_per_million: float


class LLMClient:
    def __init__(self, client: openai.AsyncOpenAI):
        self._client = client
        self.gpt_4o_mini_usage = ModelTokenUsage(
            cached_input_tokens_price_per_million=0.15,
            not_cached_input_tokens_price_per_million=0.075,
            output_tokens_tokens_price_per_million=0.6,
        )
        self._lock = asyncio.Lock()  # do not like this at all

    async def parse(self, *args, **kwargs) -> ParsedResponse[Any]:  # lazy typing
        response = await self._client.responses.parse(*args, **kwargs)
        if not response.usage:
            logger.warning("Could not get token usage for LLM call")
            return response

        cached_input_tokens = response.usage.input_tokens_details.cached_tokens
        not_cached_input_tokens = response.usage.input_tokens - cached_input_tokens
        output_tokens = response.usage.output_tokens

        match response.model:
            case "gpt-4o-mini-2024-07-18":
                async with self._lock:
                    self.gpt_4o_mini_usage.total_cached_input_tokens += (
                        cached_input_tokens
                    )
                    self.gpt_4o_mini_usage.total_not_cached_input_tokens += (
                        not_cached_input_tokens
                    )
                    self.gpt_4o_mini_usage.total_output_tokens += output_tokens
            case _:
                logger.warning(f"Cost counting is not set up for {response.model}")

        return response

    def log_total_usage(self) -> None:
        """Returns the accumulated token usage."""
        cached_input_cost = (
            self.gpt_4o_mini_usage.total_cached_input_tokens
            * self.gpt_4o_mini_usage.cached_input_tokens_price_per_million
            / 1_000_000
        )
        not_cached_input_cost = (
            self.gpt_4o_mini_usage.total_not_cached_input_tokens
            * self.gpt_4o_mini_usage.not_cached_input_tokens_price_per_million
            / 1_000_000
        )
        output_cost = (
            self.gpt_4o_mini_usage.total_output_tokens
            * self.gpt_4o_mini_usage.output_tokens_tokens_price_per_million
            / 1_000_000
        )

        logger.info(
            f"\n"
            f"--------------------\n"
            f"  Cached Input Tokens:     {self.gpt_4o_mini_usage.total_cached_input_tokens:,}\n"
            f"  Non-Cached Input Tokens: {self.gpt_4o_mini_usage.total_not_cached_input_tokens:,}\n"
            f"  Output Tokens:           {self.gpt_4o_mini_usage.total_output_tokens:,}\n"
            f"--------------------\n"
            f"  Estimated Cost:\n"
            f"--------------------\n"
            f"    Cached Input Cost:     ${cached_input_cost:.6f}\n"
            f"    Non-Cached Input Cost: ${not_cached_input_cost:.6f}\n"
            f"    Output Cost:           ${output_cost:.6f}\n"
            f"    Total Model Cost:      ${cached_input_cost + not_cached_input_cost + output_cost:.6f}\n"
            f"--------------------"
        )
