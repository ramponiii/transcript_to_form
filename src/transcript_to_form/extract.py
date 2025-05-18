import asyncio
from pathlib import Path

import chromadb
import httpx
from openai import AsyncOpenAI

from transcript_to_form.retrieval.chunking.main import TranscriptChunker

from . import env_settings, logger
from .client_identification import ClientIdentifier
from .exceptions import ChromaDbNotRunningError
from .llm import LLMClient
from .models import (
    Addresses,
    Client,
    ClientInformation,
    Dependents,
    Employments,
    Expenses,
    Form,
    HealthDetails,
    Incomes,
    LoansAndMortgages,
    Objectives,
    OtherAssets,
    Pensions,
    ProtectionPolicies,
    SavingsAndInvestments,
)
from .retrieval import Retriever
from .structured_data_extractor import StructuredDataExtractor


async def extract(transcript: str, output_path: Path) -> Form:
    llm_client = LLMClient(client=AsyncOpenAI(api_key=env_settings.openai_api_key))
    try:
        chroma_client = await chromadb.AsyncHttpClient(
            host=env_settings.chroma_host, port=env_settings.chroma_port
        )
    except httpx.ConnectError as e:
        logger.critical(
            "Could not connect to vector database. Ensure you have run `uv run chroma run --path ./chroma_db`",
            exc_info=e,
        )
        raise ChromaDbNotRunningError(
            "Chroma is probably not running, please run it with `uv run chroma run --path ./chroma_db`"
        )

    client_identifier = ClientIdentifier(llm_client=llm_client)
    identified_clients = await client_identifier.identify_clients(transcript)

    chunker = TranscriptChunker()
    retriever = Retriever(
        chroma_client=chroma_client,
        transcript=transcript,
        chunker=chunker,
        n_clients=len(identified_clients.profiles),
    )

    await retriever.ingest()

    structured_data_extractor = StructuredDataExtractor(
        llm_client=llm_client,
        retriever=retriever,
        client_short_profiles=identified_clients,
    )
    client_results = []

    # this is not good, needs re-written, lots of repetition of code
    logger.info("Starting tasks to extract forms in parallel...")

    async with asyncio.TaskGroup() as task_group:
        for client in identified_clients.profiles:
            client_name = f"{client.name} ({client.alias})"
            res = {
                "client_information": task_group.create_task(
                    structured_data_extractor.extract(ClientInformation, client_name)
                ),
                "health_details": task_group.create_task(
                    structured_data_extractor.extract(HealthDetails, client_name)
                ),
                "employments": task_group.create_task(
                    structured_data_extractor.extract(Employments, client_name)
                ),
            }
            client_results.append(res)

        addresses_task = task_group.create_task(
            structured_data_extractor.extract(Addresses)
        )
        dependents_task = task_group.create_task(
            structured_data_extractor.extract(Dependents)
        )
        expenses_task = task_group.create_task(
            structured_data_extractor.extract(Expenses)
        )
        incomes_task = task_group.create_task(
            structured_data_extractor.extract(Incomes)
        )
        loans_and_mortgages_task = task_group.create_task(
            structured_data_extractor.extract(LoansAndMortgages)
        )
        objectives_task = task_group.create_task(
            structured_data_extractor.extract(Objectives)
        )
        other_assets_task = task_group.create_task(
            structured_data_extractor.extract(OtherAssets)
        )
        pensions_task = task_group.create_task(
            structured_data_extractor.extract(Pensions)
        )
        protection_policies_task = task_group.create_task(
            structured_data_extractor.extract(ProtectionPolicies)
        )
        savings_and_investments_task = task_group.create_task(
            structured_data_extractor.extract(SavingsAndInvestments)
        )

    clients = [
        Client(
            client_information=res["client_information"].result(),
            employments=res["employments"].result(),
            health_details=res["health_details"].result(),
        )
        for res in client_results
    ]

    completed_form = Form(
        clients=clients,
        addresses=addresses_task.result(),
        dependents=dependents_task.result(),
        expenses=expenses_task.result(),
        incomes=incomes_task.result(),
        loans_and_mortgages=loans_and_mortgages_task.result(),
        objectives=objectives_task.result(),
        other_assets=other_assets_task.result(),
        pensions=pensions_task.result(),
        protection_policies=protection_policies_task.result(),
        savings_and_investments=savings_and_investments_task.result(),
    )

    with open(output_path / "form.json", "w") as file:
        file.write(completed_form.model_dump_json(indent=4))

    llm_client.log_total_usage()

    return completed_form
