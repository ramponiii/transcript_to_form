import asyncio
import json
import random
import uuid
from pathlib import Path

from .. import logger
from .generator import SyntheticDataGenerator
from .models import (
    SamplerConfig,
    SyntheticDataWithRequest,
    SyntheticGenerationRequest,
    SyntheticTranscriptSegments,
    TranscriptQuality,
)

# todo: should write to file as dataset is created, rather than waiting until they are all done


class SyntheticDataSampler:
    def __init__(self, generator: SyntheticDataGenerator) -> None:
        self.__generator = generator
        pass

    async def create_dataset(
        self, output_path: Path, config: SamplerConfig, batch_size: int = 50
    ) -> list[SyntheticDataWithRequest]:
        output_path.mkdir(exist_ok=True, parents=True)
        logger.info(
            f"Creating dataset with {config.total_samples_per_model} samples per model for {len(config.models)} models. Writing to {output_path}"
        )

        # Number of samples of each quality
        n_high = round(config.total_samples_per_model * config.prop_high_quality)
        n_medium = round(config.total_samples_per_model * config.prop_medium_quality)
        n_low = config.total_samples_per_model - n_high - n_medium

        transcript_quality = (
            [TranscriptQuality.HIGH] * n_high
            + [TranscriptQuality.MEDIUM] * n_medium
            + [TranscriptQuality.LOW] * n_low
        )

        specific_requests = random.choices(
            config.specific_requests, k=config.total_samples_per_model
        )

        segment_sizes: list[int] = config.segments_distribution.rvs(
            size=config.total_samples_per_model
        )

        requests = [
            SyntheticGenerationRequest(
                model=model_to_produce,
                transcript_quality=quality,
                specific_request=specific_req,
                n_segments=n_segments,
                id=uuid.uuid4(),
            )
            for model_to_produce in config.models
            for quality, specific_req, n_segments in zip(
                transcript_quality, specific_requests, segment_sizes, strict=True
            )
        ]

        responses: list[BaseException | SyntheticTranscriptSegments] = []
        # generate in batches, don't want to make too many requests, this is lazy, some better backoff policy should be written
        for i in range(0, len(requests), batch_size):
            batch = requests[i : i + batch_size]
            batch_tasks = [
                asyncio.create_task(self.__generator.generate_example(example))
                for example in batch
            ]

            responses.extend(await asyncio.gather(*batch_tasks, return_exceptions=True))

        samples: list[SyntheticDataWithRequest] = []
        for request, response in zip(requests, responses):
            if isinstance(response, BaseException):
                logger.error(
                    "Failed to produce synthetic data sample", exc_info=response
                )
            else:
                req_specific_output_path = output_path / str(request.id)
                req_specific_output_path.mkdir(exist_ok=True)
                logger.debug(f"Writing synthetic example to {req_specific_output_path}")

                with open(req_specific_output_path / "request.json", "w") as file:
                    req_as_str = json.dumps(
                        {
                            "model": request.model.__name__,
                            "transcript_quality": str(request.transcript_quality),
                            "specific_requests": request.specific_request,
                            "segments": request.n_segments,
                            "id": str(request.id),
                        },
                        indent=4,
                    )
                    file.write(req_as_str)
                with open(
                    req_specific_output_path / "synthetic_chunks.json", "w"
                ) as file:
                    file.write(response.model_dump_json(indent=4))

                samples.append(
                    SyntheticDataWithRequest(request=request, response=response)
                )
        logger.info(
            f"Produced {len(samples)} dataset examples, find them in the directory '{output_path}'"
        )
        return samples
