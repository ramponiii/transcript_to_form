from collections import Counter, defaultdict
from pathlib import Path

from transcript_to_form.evaluator.llm_judge.llm_judge_stats_models import OverallStats
from transcript_to_form.evaluator.models import Evaluation
from transcript_to_form.evaluator.statistics.models import StatisticsEval

evals: list[Evaluation] = [
    Evaluation.load(x)
    for x in Path("transcripts").iterdir()
    if x.name.endswith("_eval.json")
]


def analyze_evaluations(evaluations: list[Evaluation]):
    """
    Analyzes a list of Evaluation objects to extract key performance statistics.
    """
    num_transcripts = len(evaluations)
    if num_transcripts == 0:
        print("No evaluations to analyze.")
        return
    print(f"Evaluating {num_transcripts} transcripts.")
    llm_stats_evals = [e.llm_stats_eval for e in evaluations]
    llm_overall_stats = [x.overall for x in llm_stats_evals]
    regular_stats_eval = analyze_stats_eval_list(e.stats_eval for e in evaluations)
    output = average_overall_stats(llm_overall_stats)
    section_stats = summarize_section_stats_dict(llm_stats_evals)

    top_problem_fields = Counter(
        f
        for stat in llm_stats_evals
        for sec in stat.section_stats.values()
        for f in sec.most_problematic_fields
    ).most_common(5)

    print()


def average_overall_stats(overall_stats_list: list[OverallStats]):
    total_weight = sum(stat.total_fields for stat in overall_stats_list)
    avg_distribution = defaultdict(float)

    for stat in overall_stats_list:
        for category, value in stat.overall_category_distribution.items():
            avg_distribution[category] += value * stat.total_fields

    return {
        category: total / total_weight for category, total in avg_distribution.items()
    }


def summarize_section_stats_dict(stats_list):
    summary = defaultdict(
        lambda: {
            "num_fields": 0,
            "accuracy_sum": 0.0,
            "count": 0,
            "misplaced_predicted": 0,
            "misplaced_true": 0,
        }
    )

    for stat in stats_list:
        for section, sec_stats in stat.section_stats.items():
            s = summary[section]
            s["num_fields"] += sec_stats.num_fields
            s["accuracy_sum"] += sec_stats.accuracy_score
            s["count"] += 1
            s["misplaced_predicted"] += sec_stats.misplaced_predicted_count
            s["misplaced_true"] += sec_stats.misplaced_true_count

    # Finalize: compute average accuracy
    return {
        section: {
            "num_fields": values["num_fields"],
            "accuracy": values["accuracy_sum"] / values["count"],
            "misplaced_predicted": values["misplaced_predicted"],
            "misplaced_true": values["misplaced_true"],
        }
        for section, values in summary.items()
    }


def analyze_stats_eval_list(
    stats_eval_list: list[StatisticsEval], underfill_threshold=-10
):
    agg = defaultdict(
        lambda: {
            "true_pct_sum": 0.0,
            "pred_pct_sum": 0.0,
            "diff_sum": 0.0,
            "count": 0,
        }
    )

    for eval in stats_eval_list:
        for section, sec_stats in eval.__dict__.items():
            if section == "same_n_clients":
                continue
            agg[section]["true_pct_sum"] += sec_stats.true_form_filled_fields_percentage
            agg[section]["pred_pct_sum"] += (
                sec_stats.predicted_form_filled_fields_percentage
            )
            agg[section]["diff_sum"] += sec_stats.percentage_difference
            agg[section]["count"] += 1

    result = {}
    underfilled = {}
    overfilled = {}

    for section, data in agg.items():
        count = data["count"]
        avg_true = data["true_pct_sum"] / count
        avg_pred = data["pred_pct_sum"] / count
        avg_diff = data["diff_sum"] / count

        result[section] = {
            "avg_true_pct": avg_true,
            "avg_predicted_pct": avg_pred,
            "avg_diff": avg_diff,
            "num_samples": count,
        }

        if avg_diff < underfill_threshold:
            underfilled[section] = result[section]
        elif avg_diff > 0:
            overfilled[section] = result[section]

    return {
        "per_section_stats": result,
        "underfilled_sections": underfilled,
        "overfilled_sections": overfilled,
    }


analyze_evaluations(evals)
