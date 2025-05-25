import re

from pinecone import Pinecone

from transcript_to_form import logger


# Pinecone asyncio support does not look to be great, so this is super slow...
class TranscriptPineconeClient:
    def __init__(self, api_key: str, transcript: str, id: str):
        self._pinecone_client = Pinecone(api_key=api_key)
        self._transcript = transcript
        self._index_name = f"index-{id}"
        self.namespace = "example-namespace"
        self._index = None
        self._chunk_map: dict[str, str] = {}

        self.initialize()

    def delete(self):
        self._pinecone_client.delete_index(name=self._index_name)

    def initialize(self, BATCH_SIZE: int = 96):
        if not self._pinecone_client.has_index(self._index_name):
            logger.info("Index did not exist. Creating...")
            self._create_index()

        # chunk - super duper lazy
        chunks = self._transcript.split("\n\n")

        if not chunks:
            logger.error("No chunks found...")
            raise ValueError("No chunks found... something is wrong")

        self._chunk_map = {str(idx): chunk for idx, chunk in enumerate(chunks)}
        logger.info(f"Working with {len(chunks)} chunks...")
        records = [
            {"_id": str(idx), "chunk_text": chunk} for idx, chunk in enumerate(chunks)
        ]

        self._index = self._pinecone_client.Index(self._index_name)
        stats = self._index.describe_index_stats()

        if stats["total_vector_count"] == 0:
            # can only do batches of at most 96? Also should be async...
            # maybe pinecone was a mistake!
            for i in range(0, len(records), BATCH_SIZE):
                batch = records[i : i + BATCH_SIZE]
                self._index.upsert_records(self.namespace, batch)
        logger.info("Vector Database Created...")

    def query(self, queries: list[str]) -> str:
        all_ids: set[int] = set()
        for query in queries:
            response = self._index.search(
                namespace=self.namespace,
                query={"top_k": 10, "inputs": {"text": query}},
            )

            ids: list[int] = [int(x["_id"]) for x in response["result"]["hits"]]
            all_ids.update(ids)
        # expand  either side of the ID to ensure we cover all the content
        expanded = sorted(
            list(set(num for i in all_ids for num in range(max(1, i - 4), i + 5)))
        )

        combined_text: list[str] = []
        for i, chunk_id in enumerate(expanded):
            str_chunk_id = str(chunk_id)
            if str_chunk_id in self._chunk_map:
                # If it's not the first chunk and there's a gap, add "..."
                if i > 0 and chunk_id - expanded[i - 1] > 1:
                    combined_text.append("...")
                combined_text.append(self._chunk_map[str_chunk_id])

        return "\n\n".join(combined_text)

    def _create_index(self):
        # NOTE: logic to clear VDB needed, should be controllable
        self._pinecone_client.create_index_for_model(
            name=self._index_name,
            cloud="aws",
            region="us-east-1",
            embed={
                "model": "llama-text-embed-v2",
                "field_map": {"text": "chunk_text"},
            },
        )
