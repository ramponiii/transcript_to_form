from enum import Enum

from pydantic import BaseModel, Field


class EvaluationCategory(Enum):
    """Categorizes the primary outcome of a field comparison."""

    IDENTICAL = "identical"
    ONLY_IN_TRUE = "only_in_true_form"
    ONLY_IN_PREDICTED = "only_in_predicted_form"
    CONTRADICTORY = "contradictory"
    PARTIAL_MATCH = "partial_match"
    MISPLACED = "misplaced_value"
    INCORRECT = "incorrect"
    TRUE_EMPTY_PREDICTED_PRESENT = "true_empty_predicted_value_present"
    PREDICTED_EMPTY_TRUE_PRESENT = "predicted_empty_true_value_present"


class MisplacementDetail(BaseModel):
    """Details if a value was found in an unexpected location."""

    found_in_section: str


class FieldEvaluation(BaseModel):
    """Evaluation details for a single field, streamlined."""

    field_name: str
    category: EvaluationCategory = Field(
        description="Categorizes the primary outcome of the field comparison."
    )
    reasoning: str = Field(
        description="A concise explanation of why the comparison resulted in this category."
    )
    predicted_value_found_elsewhere_in_true: list[MisplacementDetail] | None = Field(
        default=None,
        description="List of locations in the TRUE form where the predicted_value (if not identical at this field) was also found. Indicates a potential misplacement error by the model.",
    )
    true_value_found_elsewhere_in_predicted: list[MisplacementDetail] | None = Field(
        default=None,
        description="List of locations in the PREDICTED form where the true_value (if not identical at this field) was found. Indicates a potential correct extraction but in the wrong place for the true value.",
    )


class FormSectionEvaluation(BaseModel):
    """Evaluation of a specific instance of a form section."""

    section_name: str
    field_evaluations: list[FieldEvaluation]


class LLMEvaluation(BaseModel):
    """
    Represents the differences for all sections between two Statistics objects.
    """

    employments: FormSectionEvaluation
    health_details: FormSectionEvaluation
    client_info: FormSectionEvaluation
    incomes: FormSectionEvaluation
    pensions: FormSectionEvaluation
    savings_and_investments: FormSectionEvaluation
    addresses: FormSectionEvaluation
    dependents: FormSectionEvaluation
    housing_expenses: FormSectionEvaluation
    misc_expenses: FormSectionEvaluation
    personal_expenses: FormSectionEvaluation
    professional_expenses: FormSectionEvaluation
    motoring_expenses: FormSectionEvaluation
    loan_repayments: FormSectionEvaluation
    loans_and_mortgages: FormSectionEvaluation
    other_assets: FormSectionEvaluation
    protection_policies: FormSectionEvaluation
