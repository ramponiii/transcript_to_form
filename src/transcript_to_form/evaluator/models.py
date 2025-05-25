from transcript_to_form.base_models import SavableBaseModel
from transcript_to_form.evaluator.llm_judge.llm_judge_stats_models import (
    LLMEvaluationStatistics,
)

from .llm_judge.models import LLMEvaluation
from .statistics.models import StatisticsEval


class Evaluation(SavableBaseModel):
    llm_eval: LLMEvaluation
    stats_eval: StatisticsEval
    llm_stats_eval: LLMEvaluationStatistics
