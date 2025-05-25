from pydantic import BaseModel

from transcript_to_form.models.form_sections.employment import Employment

from .form_sections.client_information import ClientInformation
from .form_sections.health_details import HealthDetails


class Client(BaseModel):
    client_information: ClientInformation | None
    employments: list[Employment]
    health_details: HealthDetails | None
