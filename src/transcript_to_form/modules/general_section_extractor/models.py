from pydantic import BaseModel


class ExtractionItem(BaseModel):
    item_name: str
    item_desc: str

    def __str__(self):
        return f"Name: {self.item_name}, Description: {self.item_desc}"


class ExtractionPreview(BaseModel):
    items_to_extract: list[ExtractionItem]

    def __str__(self):
        return f"All Items: {'\n\n'.join(str(e) for e in self.items_to_extract)}"


class ModelIndexVerification(BaseModel):
    index: int
    valid: bool
    reasoning: str


class VerifiedExtraction(BaseModel):
    results: list[ModelIndexVerification]
