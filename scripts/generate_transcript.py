import asyncio
import random
from uuid import uuid4

from openai import AsyncClient

from transcript_to_form.main import EnvSettings
from transcript_to_form.models import (
    Address,
    ClientInformation,
    Dependent,
    Employment,
    HealthDetails,
    HousingExpense,
    Income,
    LoanOrMortgage,
    LoanRepayment,
    MiscExpense,
    MotoringExpense,
    OtherAsset,
    Pension,
    PersonalExpense,
    ProfessionalExpense,
    ProtectionPolicy,
    SavingOrInvestment,
)
from transcript_to_form.transcript_generator import TranscriptGenerator
from transcript_to_form.transcript_generator.models import (
    ModelWithDesiredCount,
    TranscriptGenerationConfig,
)

generator = TranscriptGenerator(AsyncClient(api_key=EnvSettings().openai_api_key))

configs: list[TranscriptGenerationConfig] = []
for _ in range(1):
    config = TranscriptGenerationConfig(
        persona_description=None,
        models=[
            ModelWithDesiredCount(model=Employment, count=random.randint(1, 2)),
            ModelWithDesiredCount(model=ClientInformation, count=1),
            ModelWithDesiredCount(model=HealthDetails, count=1),
            ModelWithDesiredCount(model=Address, count=random.randint(1, 2)),
            ModelWithDesiredCount(model=Dependent, count=random.randint(1, 2)),
            ModelWithDesiredCount(model=HousingExpense, count=random.randint(1, 2)),
            ModelWithDesiredCount(model=Income, count=random.randint(1, 2)),
            ModelWithDesiredCount(model=LoanOrMortgage, count=random.randint(1, 3)),
            ModelWithDesiredCount(model=LoanRepayment, count=random.randint(1, 2)),
            ModelWithDesiredCount(model=MiscExpense, count=random.randint(1, 3)),
            ModelWithDesiredCount(model=MotoringExpense, count=random.randint(1, 2)),
            ModelWithDesiredCount(model=OtherAsset, count=random.randint(1, 3)),
            ModelWithDesiredCount(model=Pension, count=random.randint(1, 2)),
            ModelWithDesiredCount(model=PersonalExpense, count=random.randint(1, 3)),
            ModelWithDesiredCount(
                model=ProfessionalExpense, count=random.randint(1, 3)
            ),
            ModelWithDesiredCount(model=ProtectionPolicy, count=random.randint(1, 3)),
            ModelWithDesiredCount(model=SavingOrInvestment, count=random.randint(1, 3)),
        ],
        id=str(uuid4()),
    )
    configs.append(config)


async def main():
    coroutines_to_gather = [generator.generate(config) for config in configs]
    tasks = asyncio.gather(*coroutines_to_gather)
    await tasks


if __name__ == "__main__":
    asyncio.run(main())
