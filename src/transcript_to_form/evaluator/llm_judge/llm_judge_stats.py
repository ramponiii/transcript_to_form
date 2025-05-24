from collections import Counter, defaultdict

from transcript_to_form.evaluator.llm_judge.llm_judge_stats_models import (
    LLMEvaluationStatistics,
    MisplacementMatrix,
    OverallStats,
    SectionStats,
)
from transcript_to_form.evaluator.llm_judge.models import (
    EvaluationCategory,
    FormSectionEvaluation,
    LLMEvaluation,
)


class StatsGenerator:
    def __init__(self, evaluation: LLMEvaluation):
        self.evaluation = evaluation

    def generate_stats(self) -> LLMEvaluationStatistics:
        overall_stats = self._get_overall_stats()
        section_level_stats = self._get_section_stats_all_sections()
        misplacement_matrix = self._get_misplacement_matrix()

        return LLMEvaluationStatistics(
            overall=overall_stats,
            section_stats=section_level_stats,
            misplacement_matrix=misplacement_matrix,
        )

    def _get_overall_stats(self) -> OverallStats:
        total_fields = 0
        all_categories: Counter[EvaluationCategory] = Counter()

        # Iterate through all sections dynamically
        for section_name, form_section_eval in self.evaluation.model_dump().items():
            if (
                isinstance(form_section_eval, dict)
                and "field_evaluations" in form_section_eval
            ):
                for field_eval in form_section_eval["field_evaluations"]:
                    total_fields += 1
                    all_categories[EvaluationCategory(field_eval["category"])] += 1

        overall_distribution = {
            cat: (count / total_fields) * 100 if total_fields > 0 else 0
            for cat, count in all_categories.items()
        }
        return OverallStats(
            total_fields=total_fields,
            overall_category_distribution=overall_distribution,
        )

    def _get_section_stats_all_sections(self) -> dict[str, SectionStats]:
        all_section_stats: dict[str, SectionStats] = {}
        for section_name, form_section_eval in self.evaluation.model_dump().items():
            if (
                isinstance(form_section_eval, dict)
                and "field_evaluations" in form_section_eval
            ):
                section_data = FormSectionEvaluation.model_validate(form_section_eval)
                all_section_stats[section_name] = self._get_single_section_stats(
                    section_data
                )
        return all_section_stats

    def _get_single_section_stats(
        self, section_evaluation: FormSectionEvaluation
    ) -> SectionStats:
        num_fields = len(section_evaluation.field_evaluations)
        category_counts = Counter(
            fe.category for fe in section_evaluation.field_evaluations
        )

        accuracy_score = (
            (category_counts[EvaluationCategory.IDENTICAL] / num_fields) * 100
            if num_fields > 0
            else 0
        )

        category_distribution = {
            cat: (count / num_fields) * 100 if num_fields > 0 else 0
            for cat, count in category_counts.items()
        }

        problematic_categories = [
            EvaluationCategory.CONTRADICTORY,
            EvaluationCategory.INCORRECT,
            EvaluationCategory.TRUE_EMPTY_PREDICTED_PRESENT,
            EvaluationCategory.PREDICTED_EMPTY_TRUE_PRESENT,
            EvaluationCategory.MISPLACED,
        ]
        most_problematic = [
            fe.field_name
            for fe in section_evaluation.field_evaluations
            if fe.category in problematic_categories
        ]

        misplaced_predicted = sum(
            1
            for fe in section_evaluation.field_evaluations
            if fe.predicted_value_found_elsewhere_in_true
        )
        misplaced_true = sum(
            1
            for fe in section_evaluation.field_evaluations
            if fe.true_value_found_elsewhere_in_predicted
        )

        return SectionStats(
            num_fields=num_fields,
            accuracy_score=accuracy_score,
            category_distribution=category_distribution,
            most_problematic_fields=list(set(most_problematic)),
            misplaced_predicted_count=misplaced_predicted,
            misplaced_true_count=misplaced_true,
        )

    def _get_misplacement_matrix(self) -> MisplacementMatrix:
        matrix = defaultdict(lambda: defaultdict(int))

        for (
            source_section_name,
            form_section_eval,
        ) in self.evaluation.model_dump().items():
            if (
                isinstance(form_section_eval, dict)
                and "field_evaluations" in form_section_eval
            ):
                for field_eval in form_section_eval["field_evaluations"]:
                    if field_eval.get("predicted_value_found_elsewhere_in_true"):
                        for detail in field_eval[
                            "predicted_value_found_elsewhere_in_true"
                        ]:
                            matrix[source_section_name][detail["found_in_section"]] += 1
                    if field_eval.get("true_value_found_elsewhere_in_predicted"):
                        for detail in field_eval[
                            "true_value_found_elsewhere_in_predicted"
                        ]:
                            matrix[source_section_name][detail["found_in_section"]] += 1

        regular_matrix = {s: dict(t) for s, t in matrix.items()}
        return MisplacementMatrix(cross_section_misplacements=regular_matrix)
