import asyncio
from pathlib import Path
from typing import Any

from openai import AsyncClient

from transcript_to_form import logger
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
from transcript_to_form.models.client import Client
from transcript_to_form.models.form import Form
from transcript_to_form.models.form_sections.expenses import Expenses
from transcript_to_form.models.form_sections.objectives import Objectives
from transcript_to_form.transcript_generator.modules.content_section_generator import (
    ContentSectionGenerator,
)
from transcript_to_form.transcript_generator.modules.intro_outro_generator import (
    IntroGenerator,
    OutroGenerator,
)
from transcript_to_form.transcript_generator.modules.models import (
    Conversation,
    ConversationWithFields,
)
from transcript_to_form.transcript_generator.modules.padding_generator import (
    PaddingGenerator,
)
from transcript_to_form.transcript_generator.modules.persona_generator import (
    PersonaGenerator,
)

from .models import MODEL_TYPES, TranscriptGenerationConfig
from .settings import OPENAI_MODEL


class TranscriptGenerator:
    def __init__(self, llm_client: AsyncClient):
        self._padding_generator = PaddingGenerator(llm_client, OPENAI_MODEL)
        self._persona_generator = PersonaGenerator(llm_client, OPENAI_MODEL)
        self._intro_generator = IntroGenerator(llm_client, OPENAI_MODEL)
        self._outro_generator = OutroGenerator(llm_client, OPENAI_MODEL)
        self._content_generator = ContentSectionGenerator(llm_client, OPENAI_MODEL)

    async def generate(
        self, config: TranscriptGenerationConfig, save_dir: str = "transcripts"
    ) -> tuple[Form, Conversation]:
        Path(save_dir).mkdir(exist_ok=True)

        extracted_form_data: dict[MODEL_TYPES, Any] = {}
        all_conversations: list[Conversation] = []

        # first generate personas
        background = (
            await self._persona_generator.generate()
            if not config.persona_description
            else config.persona_description
        )
        logger.info(f"Working with background: {background}")

        # for each desired model, generate the required count
        async with asyncio.TaskGroup() as tg:
            generated_models = {
                model_config.model: tg.create_task(
                    self._content_generator.generate(
                        model_config.model,
                        background,
                        n_models_to_generate=model_config.count,
                    )
                )
                for model_config in config.models
            }

        # populate the conversation and model info
        for attr_name, task in generated_models.items():
            conversation_segment, populated_model_instance = task.result()
            all_conversations.append(conversation_segment)
            extracted_form_data[attr_name] = populated_model_instance

        # only support one client right now
        client_info = extracted_form_data.get(ClientInformation, [])
        client_info_first = client_info[0] if client_info else None
        health_info = extracted_form_data.get(HealthDetails, [])
        health_info_first = health_info[0] if health_info else None

        clients_list = [
            Client(
                client_information=client_info_first,
                employments=extracted_form_data.get(Employment, []),
                health_details=health_info_first,
            )
        ]

        form = Form(
            clients=clients_list,
            addresses=extracted_form_data.get(Address, []),
            dependents=extracted_form_data.get(Dependent, []),
            incomes=extracted_form_data.get(Income, []),
            other_assets=extracted_form_data.get(OtherAsset, []),
            pensions=extracted_form_data.get(Pension, []),
            loans_and_mortgages=extracted_form_data.get(LoanOrMortgage, []),
            protection_policies=extracted_form_data.get(ProtectionPolicy, []),
            savings_and_investments=extracted_form_data.get(SavingOrInvestment, []),
            expenses=Expenses(
                loan_repayments=extracted_form_data.get(LoanRepayment, []),
                motoring_expenses=extracted_form_data.get(MotoringExpense, []),
                housing_expenses=extracted_form_data.get(HousingExpense, []),
                professional_expenses=extracted_form_data.get(ProfessionalExpense, []),
                personal_expenses=extracted_form_data.get(PersonalExpense, []),
                misc_expenses=extracted_form_data.get(MiscExpense, []),
            ),
            objectives=Objectives(objectives=[]),
        )
        logger.info(
            f"Got {len(all_conversations)} content sections, generating padding..."
        )
        # now produce padding messages
        padding = await asyncio.gather(
            *[
                self._padding_generator.generate(
                    conversation_start=all_conversations[i],
                    conversation_end=all_conversations[i + 1],
                )
                for i in range(len(all_conversations) - 1)
            ]
        )

        # now insert each padding item between the content !
        conversation: list[ConversationWithFields | Conversation] = []
        for i in range(len(all_conversations)):
            conversation.append(all_conversations[i])
            if i != len(all_conversations) - 1:
                conversation.append(padding[i])

        logger.info("Generating intro and outro")

        intro, outro = await asyncio.gather(
            self._intro_generator.generate(str(conversation)),
            self._outro_generator.generate(str(conversation)),
        )

        final_convo = Conversation(
            conversation=[
                dialogue_pair
                for c in [intro] + conversation + [outro]
                for dialogue_pair in c.conversation
            ]
        )
        save_dir_path = Path(save_dir)
        logger.info(f"Saving to {save_dir_path} with ID {config.id}")
        final_convo.save(save_dir_path / f"{config.id}_transcript.json")
        form.save(save_dir_path / f"{config.id}_form.json")
        return form, final_convo
