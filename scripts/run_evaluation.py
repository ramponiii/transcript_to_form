import asyncio
from pathlib import Path

import chromadb

from transcript_to_form import env_settings
from transcript_to_form.evaluation.retrieval.evaluate import RetrievalEvaluator
from transcript_to_form.retrieval.chunking.main import TranscriptChunker

DATASET_PATH = Path("example_dataset")


async def main():
    chroma_client = await chromadb.AsyncHttpClient(
        host=env_settings.chroma_host, port=env_settings.chroma_port
    )

    evaluator = RetrievalEvaluator(
        chroma_client=chroma_client, chunker=TranscriptChunker()
    )
    await evaluator.evaluate_retrieval_on_dataset(DATASET_PATH)


if __name__ == "__main__":
    asyncio.run(main())
