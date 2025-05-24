# lots of repeated code here
from typing import Sequence

from pydantic import BaseModel

from transcript_to_form.models.form import Form

from .models import (
    SectionStats,
    SectionStatsDifference,
    Statistics,
    StatisticsEval,
)


class StatsEvaluator:
    pass

    def compare_forms(self, true_form: Form, predicted_form: Form) -> StatisticsEval:
        """
        Compares two Form instances and returns the differences in their statistics.

        Args:
            true_form: The ground truth Form instance.
            predicted_form: The predicted Form instance.

        Returns:
            A StatisticsEval object detailing the differences for each section.
        """
        true_form_stats = self._get_form_stats(true_form)
        pred_form_stats = self._get_form_stats(predicted_form)

        same_n_clients = len(true_form.clients) == len(predicted_form.clients)

        return StatisticsEval(
            same_n_clients=same_n_clients,
            employments=_calculate_section_stats_difference(
                true_form_stats.employments, pred_form_stats.employments
            ),
            health_details=_calculate_section_stats_difference(
                true_form_stats.health_details, pred_form_stats.health_details
            ),
            client_info=_calculate_section_stats_difference(
                true_form_stats.client_info, pred_form_stats.client_info
            ),
            incomes=_calculate_section_stats_difference(
                true_form_stats.incomes, pred_form_stats.incomes
            ),
            pensions=_calculate_section_stats_difference(
                true_form_stats.pensions, pred_form_stats.pensions
            ),
            savings_and_investments=_calculate_section_stats_difference(
                true_form_stats.savings_and_investments,
                pred_form_stats.savings_and_investments,
            ),
            addresses=_calculate_section_stats_difference(
                true_form_stats.addresses, pred_form_stats.addresses
            ),
            dependents=_calculate_section_stats_difference(
                true_form_stats.dependents, pred_form_stats.dependents
            ),
            housing_expenses=_calculate_section_stats_difference(
                true_form_stats.housing_expenses, pred_form_stats.housing_expenses
            ),
            misc_expenses=_calculate_section_stats_difference(
                true_form_stats.misc_expenses, pred_form_stats.misc_expenses
            ),
            personal_expenses=_calculate_section_stats_difference(
                true_form_stats.personal_expenses, pred_form_stats.personal_expenses
            ),
            professional_expenses=_calculate_section_stats_difference(
                true_form_stats.professional_expenses,
                pred_form_stats.professional_expenses,
            ),
            motoring_expenses=_calculate_section_stats_difference(
                true_form_stats.motoring_expenses, pred_form_stats.motoring_expenses
            ),
            loan_repayments=_calculate_section_stats_difference(
                true_form_stats.loan_repayments, pred_form_stats.loan_repayments
            ),
            loans_and_mortgages=_calculate_section_stats_difference(
                true_form_stats.loans_and_mortgages, pred_form_stats.loans_and_mortgages
            ),
            other_assets=_calculate_section_stats_difference(
                true_form_stats.other_assets, pred_form_stats.other_assets
            ),
            protection_policies=_calculate_section_stats_difference(
                true_form_stats.protection_policies, pred_form_stats.protection_policies
            ),
        )

    def _get_form_stats(self, form: Form) -> Statistics:
        client_info_stats: list[SectionStats] = []
        employments_stats: list[SectionStats] = []
        health_details_stats: list[SectionStats] = []

        for client in form.clients:
            if client.client_information:
                client_info_stats.append(
                    get_empty_field_proportion(client.client_information)
                )
            employments_stats.append(
                get_empty_field_proportion_over_list_of_objects(client.employments)
            )
            if client.health_details:
                health_details_stats.append(
                    get_empty_field_proportion(client.health_details)
                )

        return Statistics(
            employments=_sum_section_stats(employments_stats),
            health_details=_sum_section_stats(health_details_stats),
            client_info=_sum_section_stats(client_info_stats),
            incomes=get_empty_field_proportion_over_list_of_objects(form.incomes),
            pensions=get_empty_field_proportion_over_list_of_objects(form.pensions),
            savings_and_investments=get_empty_field_proportion_over_list_of_objects(
                form.savings_and_investments
            ),
            addresses=get_empty_field_proportion_over_list_of_objects(form.addresses),
            dependents=get_empty_field_proportion_over_list_of_objects(form.dependents),
            housing_expenses=get_empty_field_proportion_over_list_of_objects(
                form.expenses.housing_expenses
            ),
            misc_expenses=get_empty_field_proportion_over_list_of_objects(
                form.expenses.misc_expenses
            ),
            personal_expenses=get_empty_field_proportion_over_list_of_objects(
                form.expenses.personal_expenses
            ),
            professional_expenses=get_empty_field_proportion_over_list_of_objects(
                form.expenses.professional_expenses
            ),
            motoring_expenses=get_empty_field_proportion_over_list_of_objects(
                form.expenses.motoring_expenses
            ),
            loan_repayments=get_empty_field_proportion_over_list_of_objects(
                form.expenses.loan_repayments
            ),
            loans_and_mortgages=get_empty_field_proportion_over_list_of_objects(
                form.loans_and_mortgages
            ),
            other_assets=get_empty_field_proportion_over_list_of_objects(
                form.other_assets
            ),
            protection_policies=get_empty_field_proportion_over_list_of_objects(
                form.protection_policies
            ),
        )


def _calculate_section_stats_difference(
    true_stats: SectionStats, predicted_stats: SectionStats
) -> SectionStatsDifference:
    """
    Calculates the difference between two SectionStats objects, focusing on percentages.
    """
    return SectionStatsDifference(
        true_form_filled_fields_percentage=true_stats.fill_percentage,
        predicted_form_filled_fields_percentage=predicted_stats.fill_percentage,
        percentage_difference=round(
            predicted_stats.fill_percentage - true_stats.fill_percentage, 2
        ),
        true_form_total_models=true_stats.total_instances,
        pred_form_total_models=predicted_stats.total_instances,
    )


def get_empty_field_proportion(model_instance: BaseModel) -> SectionStats:
    fields = list(model_instance)
    empty_fields = sum(
        1
        for _, value in fields
        if value is None or (isinstance(value, list) and not value)
    )
    return SectionStats(
        filled_fields=len(fields) - empty_fields,
        total_fields=len(fields),
        total_instances=1,
    )


def get_empty_field_proportion_over_list_of_objects(
    model_instances: Sequence[BaseModel],
) -> SectionStats:
    instance_stats = [
        get_empty_field_proportion(instance) for instance in model_instances
    ]
    return _sum_section_stats(instance_stats)


def _sum_section_stats(stats_list: list[SectionStats]) -> SectionStats:
    return SectionStats(
        filled_fields=sum(stats.filled_fields for stats in stats_list),
        total_fields=sum(stats.total_fields for stats in stats_list),
        total_instances=sum(stats.total_instances for stats in stats_list),
    )
