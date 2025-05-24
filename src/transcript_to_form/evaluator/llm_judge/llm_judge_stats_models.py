from pathlib import Path

from pydantic import BaseModel

from transcript_to_form.evaluator.llm_judge.models import EvaluationCategory


class SectionStats(BaseModel):
    num_fields: int
    accuracy_score: float
    category_distribution: dict[EvaluationCategory, float]
    most_problematic_fields: list[str]
    misplaced_predicted_count: int
    misplaced_true_count: int


class OverallStats(BaseModel):
    total_fields: int
    overall_category_distribution: dict[EvaluationCategory, float]


class MisplacementMatrix(BaseModel):
    cross_section_misplacements: dict[str, dict[str, int]]


class LLMEvaluationStatistics(BaseModel):
    overall: OverallStats
    section_stats: dict[str, SectionStats]
    misplacement_matrix: MisplacementMatrix

    def save(self, path: Path | str):
        with open(path, "w") as file:
            file.write(self.model_dump_json(indent=4))

    @classmethod
    def load(cls, path: Path | str) -> "LLMEvaluationStatistics":
        filepath = Path(path)
        with open(filepath, "r", encoding="utf-8") as file:
            json_data = file.read()
        return cls.model_validate_json(json_data)
