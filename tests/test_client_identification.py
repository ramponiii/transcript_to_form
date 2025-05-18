import pytest
from openai import AsyncOpenAI

from tests.data import SAMPLE_TRANSCRIPT_1, SAMPLE_TRANSCRIPT_2
from transcript_to_form import env_settings
from transcript_to_form.client_identification import ClientIdentifier
from transcript_to_form.llm import LLMClient

client_identifier = ClientIdentifier(
    llm_client=LLMClient(client=AsyncOpenAI(api_key=env_settings.openai_api_key))
)


@pytest.mark.asyncio
async def test_sample_transcript_1_extracts_jerome_and_jennifer():
    clients = await client_identifier.identify_clients(SAMPLE_TRANSCRIPT_1)
    profiles = clients.profiles
    assert len(profiles) == 2
    jerome_wantsome_profile = [p for p in profiles if p.name == "Jerome Wantsome"]
    assert len(jerome_wantsome_profile) == 1
    assert "client1" == jerome_wantsome_profile[0].alias.lower()
    jennifer_wantsome_profile = [p for p in profiles if p.name == "Jennifer Wantsome"]
    assert len(jennifer_wantsome_profile) == 1
    assert "client2" == jennifer_wantsome_profile[0].alias.lower()


@pytest.mark.asyncio
async def test_sample_transcript_2_extracts_jerome_and_jennifer():
    clients = await client_identifier.identify_clients(SAMPLE_TRANSCRIPT_2)
    profiles = clients.profiles
    assert ["Samuel Smith"] == [p.name for p in profiles]
    assert profiles[0].alias.lower() == "client"
