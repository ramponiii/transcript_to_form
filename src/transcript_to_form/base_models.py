from pathlib import Path

from pydantic import BaseModel


class SavableBaseModel(BaseModel):
    def save(self, path: Path | str):
        with open(path, "w") as file:
            file.write(self.model_dump_json(indent=4))

    @classmethod
    def load(cls, path: Path | str) -> "SavableBaseModel":
        filepath = Path(path)
        with open(filepath, "r", encoding="latin-1") as file:
            json_data = file.read()
        return cls.model_validate_json(json_data)
