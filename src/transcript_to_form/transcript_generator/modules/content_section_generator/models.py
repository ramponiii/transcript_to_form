from enum import StrEnum

from pydantic import BaseModel


class Verification(StrEnum):
    ALL_INFORMATION_CONTAINED = "ALL_CONTAINED"
    MISSING_INFO = "MISSING_INFO"


class VerificationWithReasoning(BaseModel):
    verification: Verification
    reasoning: str
