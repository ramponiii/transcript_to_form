import asyncio
from pathlib import Path

from openai import AsyncOpenAI

from transcript_to_form import logger
from transcript_to_form.evaluator import Evaluator
from transcript_to_form.main import EnvSettings, extract
from transcript_to_form.models.form import Form
from transcript_to_form.transcript_generator.modules.models import Conversation

TRANSCRIPTS_DIR = Path("transcripts")

for transcript_path in TRANSCRIPTS_DIR.iterdir():
    if transcript_path.name.endswith(
        "_form.json"
    ) and not transcript_path.name.endswith("_pred_form.json"):
        transcript_id = transcript_path.name.replace("_form.json", "")
        logger.info(f"Working on {transcript_id}")
        if not (TRANSCRIPTS_DIR / f"{transcript_id}_eval.json").exists():
            form = Form.load(transcript_path)
            transcript = str(
                Conversation.load(TRANSCRIPTS_DIR / f"{transcript_id}_transcript.json")
            )

            # firstly, run extraction
            pred_form = asyncio.run(
                extract(
                    transcript,
                    id=transcript_id,
                    output_path=TRANSCRIPTS_DIR / f"{transcript_id}_pred_form.json",
                )
            )

            asyncio.run(
                Evaluator(
                    llm_client=AsyncOpenAI(api_key=EnvSettings().openai_api_key),
                    model="gpt-4o",
                ).evaluate(
                    pred_form,
                    form,
                    output_path=TRANSCRIPTS_DIR / f"{transcript_id}_eval.json",
                )
            )
