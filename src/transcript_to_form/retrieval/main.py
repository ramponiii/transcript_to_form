"""Lazy VDB implementation. Lots to improve in here."""

import hashlib

from chromadb import IDs
from chromadb.api import AsyncClientAPI
from chromadb.api.models.AsyncCollection import AsyncCollection
from chromadb.errors import NotFoundError

from transcript_to_form import logger
from transcript_to_form.retrieval.chunking.models import TranscriptChunk

from .chunking import TranscriptChunker
from .models import TranscriptChunkWithSurroundingContext


class Retriever:
    def __init__(
        self,
        transcript: str | list[TranscriptChunk],
        chroma_client: AsyncClientAPI,
        chunker: TranscriptChunker,
        n_clients: int,
    ):
        self._chroma_client = chroma_client
        self._chunker = chunker

        if isinstance(transcript, str):
            self._chunks = self._chunker.chunk(transcript, n_clients)
            self._collection_name = hashlib.sha256(transcript.encode()).hexdigest()
        else:
            # ran out of time, lazy logic, always ingest to same collection
            self._collection_name = "retrieval-testing"
            self._chunks = transcript

        self._n_chunks = len(self._chunks)
        self._chunk_id_map = {c.chunk_index: c for c in self._chunks}
        self._collection: None | AsyncCollection = None

    async def ingest(self):
        logger.info("Starting ingestion to VDB")
        transcript_text_chunks = [str(c) for c in self._chunks]
        transcript_chunk_id = [str(c.chunk_index) for c in self._chunks]
        self._n_chunks = len(self._chunks)

        collections = await self._chroma_client.list_collections()
        if self._collection_name in [c.name for c in collections]:
            logger.info("Found existing collection, collection will not be re-created")
            self._collection = await self._chroma_client.get_collection(
                name=self._collection_name
            )
            return
        collection = await self._chroma_client.create_collection(
            name=self._collection_name
        )
        await collection.add(
            documents=transcript_text_chunks,
            ids=transcript_chunk_id,
        )
        logger.info(f"Successfully added {self._n_chunks} to the vector database")
        self._collection = collection

    async def query(
        self,
        queries: list[str],
        query_id: str,
        n_results: int = 10,
    ) -> list[IDs]:
        if not self._collection:
            raise Exception(
                "Tried to query chroma before the collection had been loaded."
            )
        try:
            query_results = await self._collection.query(
                query_texts=queries, n_results=n_results, include=["metadatas"]
            )
        except NotFoundError as e:
            logger.error(
                "Failed to query collection",
                exc_info=e,
                extra={
                    "query_id": query_id,
                    "queries": queries,
                    "collection_name": self._collection_name,
                },
            )
            raise e
        logger.debug(f"Executed {len(queries)} queries for '{query_id}'")
        returned_ids = query_results["ids"]
        return returned_ids

    async def expanded_context(self, returned_ids: list[IDs], n_neighbors: int) -> str:
        # ugly code that has a clear optimization,
        # should not await in a for loop (!!!)
        # could just pool them, leaving it be as it executes quickly as is.
        unique_chunks_dict: dict[int, TranscriptChunk] = {}
        for ids in returned_ids:
            for id_val in ids:
                expanded_chunks = await self._expand_chunk(
                    id_val, n_neighbors=n_neighbors
                )
                for chunk in expanded_chunks.chunks:
                    unique_chunks_dict[chunk.chunk_index] = chunk

        output = _chunks_dict_to_string(unique_chunks_dict)
        return output

    async def _expand_chunk(
        self, hit_id: str, n_neighbors: int
    ) -> TranscriptChunkWithSurroundingContext:
        """Expand chunk to get more surrounding context"""
        hit_original_index = int(hit_id)
        if not (0 <= hit_original_index < self._n_chunks):
            raise ValueError("Retrieved a chunk with index outwith the expected range")

        start_index = max(0, hit_original_index - n_neighbors)
        end_index = min(self._n_chunks, hit_original_index + n_neighbors + 1)

        neighboring_chunks = await self._collection.get(
            ids=[str(x) for x in range(start_index, end_index)]
        )

        expanded_chunks = [
            self._chunk_id_map.get(int(id), None) for id in neighboring_chunks["ids"]
        ]
        if any(c is None for c in expanded_chunks):
            logger.warning(
                "Some chunks were missing ids"
            )  # todo: need to re-write code to understand what ids were missing

        expanded_chunks = [c for c in expanded_chunks if c is not None]
        return TranscriptChunkWithSurroundingContext(
            retrieved_chunk_idx=hit_original_index, chunks=expanded_chunks
        )

    # todo: this needs properly tested and evaluated, its a blind spot in my current eval setup
    async def query_and_expand_context(
        self,
        queries: list[str],
        query_id: str,
        n_results: int,
        n_neighbors: int,
    ):
        ids = await self.query(queries=queries, query_id=query_id, n_results=n_results)

        context = await self.expanded_context(ids, n_neighbors=n_neighbors)

        return context


def _chunks_dict_to_string(
    chunks: dict[int, TranscriptChunk],
) -> str:
    sorted_unique_chunks = sorted(chunks.values(), key=lambda chunk: chunk.chunk_index)

    output_parts: list[str] = []
    prev_index = -2
    for chunk in sorted_unique_chunks:
        if output_parts and chunk.chunk_index > prev_index + 1:
            output_parts.append("(...)")
        output_parts.append(str(chunk))
        prev_index = chunk.chunk_index

    final_transcript_string = "\n\n".join(output_parts)

    return final_transcript_string
