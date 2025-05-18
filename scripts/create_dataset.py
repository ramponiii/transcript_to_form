import asyncio
from pathlib import Path

from openai import AsyncOpenAI

from transcript_to_form import env_settings
from transcript_to_form.llm import LLMClient
from transcript_to_form.synthetic_data_generator.example_sampler_config import (
    example_config,
)
from transcript_to_form.synthetic_data_generator.generator import SyntheticDataGenerator
from transcript_to_form.synthetic_data_generator.sampler import SyntheticDataSampler

llm_client = LLMClient(client=AsyncOpenAI(api_key=env_settings.openai_api_key))

generator = SyntheticDataGenerator(llm_client=llm_client)
sampler = SyntheticDataSampler(generator=generator)

asyncio.run(sampler.create_dataset(output_path=Path("dataset"), config=example_config))

llm_client.log_total_usage()
