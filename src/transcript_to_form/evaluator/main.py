from openai import AsyncOpenAI

from transcript_to_form.evaluator.llm_judge import LLMJudgeEvaluator
from transcript_to_form.evaluator.statistics import StatsEvaluator
from transcript_to_form.models.form import Form

from .models import Evaluation


class Evaluator:
    def __init__(self, llm_client: AsyncOpenAI, model: str):
        self._stats_evaluator = StatsEvaluator()
        self._llm_judge_evaluator = LLMJudgeEvaluator(llm_client, model)

    async def evaluate(self, pred_form: Form, true_form: Form) -> Evaluation:
        llm_eval = await self._llm_judge_evaluator.evaluate(
            true_form=true_form, pred_form=pred_form
        )
        evaluation = Evaluation(
            stats_eval=self._stats_evaluator.compare_forms(
                true_form=true_form, predicted_form=pred_form
            ),
            llm_eval=llm_eval,
        )
        return evaluation
