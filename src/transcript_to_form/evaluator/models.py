from pathlib import Path

from pydantic import BaseModel

from .llm_judge.models import LLMEvaluation
from .statistics.models import StatisticsEval


class Evaluation(BaseModel):
    llm_eval: LLMEvaluation
    stats_eval: StatisticsEval

    def save(self, path: Path | str):
        with open(path, "w") as file:
            file.write(self.model_dump_json(indent=4))

    @classmethod
    def load(cls, path: Path | str) -> "Evaluation":
        filepath = Path(path)
        with open(filepath, "r", encoding="utf-8") as file:
            json_data = file.read()
        return cls.model_validate_json(json_data)
