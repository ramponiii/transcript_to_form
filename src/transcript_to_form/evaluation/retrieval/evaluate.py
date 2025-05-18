"""
This evaluator is useful for understanding how well retrieval is working broadly.
It does not make assertions around specific facts being returned, it essentially evaluates the number of
chunks returned of the desired type for each retrieval, for each model. Thus, it does not give great
insight into how well the system performs as a whole.
"""

import matplotlib

matplotlib.use("Agg")
import json
from collections import defaultdict
from pathlib import Path

from chromadb.api import AsyncClientAPI
from matplotlib import pyplot as plt

from transcript_to_form.models import MODEL_RETRIEVAL_QUERY_MAPPINGS
from transcript_to_form.retrieval import Retriever
from transcript_to_form.retrieval.chunking import TranscriptChunker
from transcript_to_form.retrieval.chunking.models import TranscriptChunk
from transcript_to_form.synthetic_data_generator.models import (
    SyntheticTranscriptSegments,
)

NAME_MAPPING = {
    "Addresses": "Address",
    "ClientInformation": "ClientInformation",
    "Dependents": "Dependent",
    "Employments": "Employment",
    "Expenses": "Expense",
    "HealthDetails": "HealthDetails",
    "Incomes": "Income",
    "LoansAndMortgages": "LoanOrMortgage",
    "Objectives": "Objectives",
    "OtherAssets": "OtherAsset",
    "Pensions": "Pension",
    "ProtectionPolicies": "ProtectionPolicy",
    "SavingsAndInvestments": "SavingOrInvestment",
}


class RetrievalEvaluator:
    def __init__(
        self,
        chroma_client: AsyncClientAPI,
        chunker: TranscriptChunker,
    ):
        self.__chroma_client = chroma_client
        self.__chunker = chunker
        pass

    async def evaluate_retrieval_on_dataset(self, dataset: Path):
        chunks, chunks_to_meta_map = _load_dataset(dataset)

        retriever = Retriever(
            transcript=chunks,
            chroma_client=self.__chroma_client,
            chunker=self.__chunker,
            n_clients=2,
        )

        # this is very slow as the embedding model runs locally
        await retriever.ingest()

        results = defaultdict(dict)
        for model, queries in MODEL_RETRIEVAL_QUERY_MAPPINGS.items():
            model_name = model.__name__
            for n_results in [3, 4, 5]:
                retrieved_ids = await retriever.query(
                    queries, query_id="testing", n_results=n_results
                )

                chunk_meta = [
                    chunks_to_meta_map[int(id)] for ids in retrieved_ids for id in ids
                ]

                results[model_name][n_results] = chunk_meta

        _produce_stats_and_graphs(output_path=Path("dataset_eval"), results=results)


def _produce_stats_and_graphs(
    output_path: Path, results: dict[str, dict[int, list[str]]]
) -> None:
    output_path.mkdir(exist_ok=True)
    output_stats: dict[str, dict[int, float]] = {}

    for model_name, result in results.items():
        output_stats[model_name] = {}
        for n_retrieved, result_list in result.items():
            prop_of_correct_type = sum(
                1 for x in result_list if x == NAME_MAPPING[model_name]
            ) / len(result_list)
            output_stats[model_name][n_retrieved] = prop_of_correct_type

        n_retrieved_values = list(output_stats[model_name].keys())
        proportion_values = list(output_stats[model_name].values())

        plt.figure(figsize=(10, 6))
        plt.plot(n_retrieved_values, proportion_values, marker="o", linestyle="-")
        plt.title(f"Proportion of Correct Type Retrieved for {model_name}")
        plt.xlabel("Number of Retrieved Items")
        plt.ylabel("Proportion of Correct Type")
        plt.grid(True)
        plt.xticks(n_retrieved_values)
        plt.ylim(0, 1.1)

        graph_filename = (
            output_path / f"retrieval_stats_{model_name.replace(' ', '_').lower()}.png"
        )
        plt.savefig(graph_filename)
        plt.close()

    # could do a confusion matrix

    with open(output_path / "stats.json", "w") as file:
        file.write(json.dumps(output_stats, indent=4))

    with open(output_path / "raw_results.json", "w") as file:
        file.write(json.dumps(results, indent=4))

    return


def _load_dataset(dataset: Path) -> tuple[list[TranscriptChunk], dict[int, str]]:
    examples: list[TranscriptChunk] = []

    id_to_meta: dict[int, str] = {}
    base_id = 0

    for obj in dataset.iterdir():
        if obj.is_dir():
            request = json.loads((obj / "request.json").read_text())
            chunks = SyntheticTranscriptSegments.model_validate_json(
                (obj / "synthetic_chunks.json").read_text()
            ).to_chunks(base_id)
            base_id += len(chunks)

            for chunk in chunks:
                id_to_meta[chunk.chunk_index] = request["model"]
            examples.extend(chunks)
    return examples, id_to_meta
