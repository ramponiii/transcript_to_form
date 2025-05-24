from pydantic import BaseModel, Field


class HealthDetails(BaseModel):
    """Represents the health and related personal details of a single individual."""

    current_state_of_health: str | None = Field(
        default=None,
        description="A general description of the individual's current state of health.",
    )
    state_of_health_explanation: str | None = Field(
        default=None,
        description="Any additional explanation or details regarding the individual's state of health.",
    )
    smoker: bool | None = Field(
        default=None,
        description="Indicates whether the individual is a smoker (True/False/None).",
    )
    cigarettes_per_day: int | None = Field(
        default=None,
        description="If a smoker, the estimated number of cigarettes smoked per day.",
    )
    smoker_since: str | None = Field(
        default=None,
        description="If a smoker, the date or age since when the individual has been smoking (e.g., 'Age 18', '2005').",
    )
    long_term_care_needed: bool | None = Field(
        default=None,
        description="Indicates if long-term care is currently needed or anticipated (True/False/None).",
    )
    long_term_care_explanation: str | None = Field(
        default=None,
        description="Any explanation or details regarding the need for long-term care.",
    )
    will: bool | None = Field(
        default=None,
        description="Indicates whether the individual has a valid will in place (True/False/None).",
    )
    information_about_will: str | None = Field(
        default=None,
        description="Any relevant information about the will, such as location or date created.",
    )
    power_of_attorney: bool | None = Field(
        default=None,
        description="Indicates whether the individual has granted a power of attorney (True/False/None).",
    )
    details_of_individual_with_power_of_attorney: str | None = Field(
        default=None,
        description="Details of the person(s) holding the power of attorney.",
    )
