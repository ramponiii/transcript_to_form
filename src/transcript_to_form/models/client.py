from pydantic import BaseModel

from .form_sections.client_information import ClientInformation
from .form_sections.employments import Employments
from .form_sections.health_details import HealthDetails


class Client(BaseModel):
    client_information: ClientInformation
    employments: Employments
    health_details: HealthDetails
