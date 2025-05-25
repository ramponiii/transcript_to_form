from pathlib import Path

from openai import AsyncOpenAI

from transcript_to_form.evaluator.llm_judge import LLMJudgeEvaluator
from transcript_to_form.evaluator.llm_judge.llm_judge_stats import (
    LLMJudgeStatsEvaluator,
)
from transcript_to_form.evaluator.statistics import StatsEvaluator
from transcript_to_form.models.form import Form

from .models import Evaluation


class Evaluator:
    def __init__(self, llm_client: AsyncOpenAI, model: str):
        self._stats_evaluator = StatsEvaluator()
        self._llm_judge_evaluator = LLMJudgeEvaluator(llm_client, model)

    async def evaluate(
        self, pred_form: Form, true_form: Form, output_path: Path | str = "eval.json"
    ) -> Evaluation:
        llm_eval = await self._llm_judge_evaluator.evaluate(
            true_form=true_form, pred_form=pred_form
        )
        llm_stats_eval = LLMJudgeStatsEvaluator(llm_eval).generate_stats()

        evaluation = Evaluation(
            stats_eval=self._stats_evaluator.compare_forms(
                true_form=true_form, predicted_form=pred_form
            ),
            llm_eval=llm_eval,
            llm_stats_eval=llm_stats_eval,
        )

        evaluation.save(output_path)
        return evaluation
