import asyncio

from transcript_to_form.main import extract
from transcript_to_form.transcripts import TRANSCRIPT_1

asyncio.run(extract(TRANSCRIPT_1, output_path="scripts/transcript_1_extraction.json"))
