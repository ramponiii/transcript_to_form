# NOTE: only evaluating first client for now,
# code is pretty lazy as is the way I'm doing LLM as a judge
import asyncio
from typing import Sequence

from pydantic import BaseModel

from transcript_to_form.base_structured_extractor import StructuredExtractor
from transcript_to_form.evaluator.llm_judge.models import (
    FormSectionEvaluation,
    LLMEvaluation,
)
from transcript_to_form.models.form import Form

from .prompts import SYSTEM, USER


class LLMJudgeEvaluator(StructuredExtractor):
    async def evaluate(self, true_form: Form, pred_form: Form) -> LLMEvaluation:
        async with asyncio.TaskGroup() as tg:
            # Create a task for each section evaluation
            addresses_task = tg.create_task(
                self._evaluate_section_with_llm(
                    true_form.addresses, pred_form.addresses, true_form, pred_form
                )
            )
            employments_task = tg.create_task(
                self._evaluate_section_with_llm(
                    true_form.clients[0].employments,
                    pred_form.clients[0].employments,
                    true_form,
                    pred_form,
                )
            )
            health_details_task = tg.create_task(
                self._evaluate_section_with_llm(
                    true_form.clients[0].health_details,
                    pred_form.clients[0].health_details,
                    true_form,
                    pred_form,
                )
            )
            client_info_task = tg.create_task(
                self._evaluate_section_with_llm(
                    true_form.clients[0].client_information,
                    pred_form.clients[0].client_information,
                    true_form,
                    pred_form,
                )
            )
            incomes_task = tg.create_task(
                self._evaluate_section_with_llm(
                    true_form.incomes, pred_form.incomes, true_form, pred_form
                )
            )
            pensions_task = tg.create_task(
                self._evaluate_section_with_llm(
                    true_form.pensions, pred_form.pensions, true_form, pred_form
                )
            )
            savings_and_investments_task = tg.create_task(
                self._evaluate_section_with_llm(
                    true_form.savings_and_investments,
                    pred_form.savings_and_investments,
                    true_form,
                    pred_form,
                )
            )
            dependents_task = tg.create_task(
                self._evaluate_section_with_llm(
                    true_form.dependents, pred_form.dependents, true_form, pred_form
                )
            )
            housing_expenses_task = tg.create_task(
                self._evaluate_section_with_llm(
                    true_form.expenses.housing_expenses,
                    pred_form.expenses.housing_expenses,
                    true_form,
                    pred_form,
                )
            )
            misc_expenses_task = tg.create_task(
                self._evaluate_section_with_llm(
                    true_form.expenses.misc_expenses,
                    pred_form.expenses.misc_expenses,
                    true_form,
                    pred_form,
                )
            )
            personal_expenses_task = tg.create_task(
                self._evaluate_section_with_llm(
                    true_form.expenses.personal_expenses,
                    pred_form.expenses.personal_expenses,
                    true_form,
                    pred_form,
                )
            )
            professional_expenses_task = tg.create_task(
                self._evaluate_section_with_llm(
                    true_form.expenses.professional_expenses,
                    pred_form.expenses.professional_expenses,
                    true_form,
                    pred_form,
                )
            )
            motoring_expenses_task = tg.create_task(
                self._evaluate_section_with_llm(
                    true_form.expenses.motoring_expenses,
                    pred_form.expenses.motoring_expenses,
                    true_form,
                    pred_form,
                )
            )
            loan_repayments_task = tg.create_task(
                self._evaluate_section_with_llm(
                    true_form.expenses.loan_repayments,
                    pred_form.expenses.loan_repayments,
                    true_form,
                    pred_form,
                )
            )
            loans_and_mortgages_task = tg.create_task(
                self._evaluate_section_with_llm(
                    true_form.loans_and_mortgages,
                    pred_form.loans_and_mortgages,
                    true_form,
                    pred_form,
                )
            )
            other_assets_task = tg.create_task(
                self._evaluate_section_with_llm(
                    true_form.other_assets, pred_form.other_assets, true_form, pred_form
                )
            )
            protection_policies_task = tg.create_task(
                self._evaluate_section_with_llm(
                    true_form.protection_policies,
                    pred_form.protection_policies,
                    true_form,
                    pred_form,
                )
            )

        return LLMEvaluation(
            addresses=addresses_task.result(),
            employments=employments_task.result(),
            health_details=health_details_task.result(),
            client_info=client_info_task.result(),
            incomes=incomes_task.result(),
            pensions=pensions_task.result(),
            savings_and_investments=savings_and_investments_task.result(),
            dependents=dependents_task.result(),
            housing_expenses=housing_expenses_task.result(),
            misc_expenses=misc_expenses_task.result(),
            personal_expenses=personal_expenses_task.result(),
            professional_expenses=professional_expenses_task.result(),
            motoring_expenses=motoring_expenses_task.result(),
            loan_repayments=loan_repayments_task.result(),
            loans_and_mortgages=loans_and_mortgages_task.result(),
            other_assets=other_assets_task.result(),
            protection_policies=protection_policies_task.result(),
        )

    async def _evaluate_section_with_llm(
        self,
        true_value: BaseModel | Sequence[BaseModel],
        predicted_value: BaseModel | Sequence[BaseModel],
        full_true_form: Form,
        full_predicted_form: Form,
    ) -> FormSectionEvaluation:
        true_value_str = (
            "\n\n".join(inst.model_dump_json(indent=4) for inst in true_value)
            if isinstance(true_value, Sequence)
            else true_value.model_dump_json(indent=4)
        )
        pred_value_str = (
            "\n\n".join(inst.model_dump_json(indent=4) for inst in predicted_value)
            if isinstance(predicted_value, Sequence)
            else predicted_value.model_dump_json(indent=4)
        )
        user_prompt_formatted = USER.format(
            true_value=true_value_str,
            predicted_value=pred_value_str,
            true_form_json=full_true_form.model_dump_json(indent=4),
            predicted_form_json=full_predicted_form.model_dump_json(indent=4),
        )
        field_eval = await self._make_llm_call(
            SYSTEM, user_prompt_formatted, FormSectionEvaluation
        )
        return field_eval
