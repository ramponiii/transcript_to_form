import asyncio

from openai import AsyncOpenAI
from pydantic_settings import BaseSettings, SettingsConfigDict

from transcript_to_form.models import (
    Address,
    Dependent,
    Expenses,
    Form,
    HousingExpense,
    Income,
    LoanOrMortgage,
    LoanRepayment,
    MiscExpense,
    MotoringExpense,
    Objectives,
    OtherAsset,
    Pension,
    PersonalExpense,
    ProfessionalExpense,
    ProtectionPolicy,
    SavingOrInvestment,
)
from transcript_to_form.modules.client_extractor import ClientExtractor
from transcript_to_form.modules.client_identifier import ClientIdentifier
from transcript_to_form.modules.general_section_extractor import GeneralSectionExtractor


class EnvSettings(BaseSettings):
    openai_api_key: str | None = None
    model_config = SettingsConfigDict(env_file=".env")


async def extract(transcript: str, output_path: str = "output_form.json") -> Form:
    env_settings = EnvSettings()
    llm_client = AsyncOpenAI(api_key=env_settings.openai_api_key)
    client_identifier = ClientIdentifier(llm_client, model="gpt-4o-mini")
    client_extractor = ClientExtractor(llm_client, model="gpt-4o-mini")
    general_section_extractor = GeneralSectionExtractor(llm_client, model="gpt-4o")

    # First, condense the transcript to save on tokens
    # NOTE: ran out of time, did not implement

    # need to generate this first before doing everything in parallel
    client_profiles = await client_identifier.run(transcript)

    async with asyncio.TaskGroup() as tg:
        clients_task = tg.create_task(client_extractor.run(transcript, client_profiles))

        addresses_task = tg.create_task(
            general_section_extractor.run(transcript, client_profiles, Address)
        )
        dependents_task = tg.create_task(
            general_section_extractor.run(transcript, client_profiles, Dependent)
        )
        incomes_task = tg.create_task(
            general_section_extractor.run(transcript, client_profiles, Income)
        )
        other_assets_task = tg.create_task(
            general_section_extractor.run(transcript, client_profiles, OtherAsset)
        )
        pensions_task = tg.create_task(
            general_section_extractor.run(transcript, client_profiles, Pension)
        )
        loans_and_mortgages_task = tg.create_task(
            general_section_extractor.run(transcript, client_profiles, LoanOrMortgage)
        )
        protection_policies_task = tg.create_task(
            general_section_extractor.run(transcript, client_profiles, ProtectionPolicy)
        )
        savings_and_investments_task = tg.create_task(
            general_section_extractor.run(
                transcript, client_profiles, SavingOrInvestment
            )
        )
        loan_repayments_task = tg.create_task(
            general_section_extractor.run(transcript, client_profiles, LoanRepayment)
        )
        housing_expenses_task = tg.create_task(
            general_section_extractor.run(transcript, client_profiles, HousingExpense)
        )
        motoring_expenses_task = tg.create_task(
            general_section_extractor.run(transcript, client_profiles, MotoringExpense)
        )
        personal_expenses_task = tg.create_task(
            general_section_extractor.run(transcript, client_profiles, PersonalExpense)
        )
        professional_expenses_task = tg.create_task(
            general_section_extractor.run(
                transcript, client_profiles, ProfessionalExpense
            )
        )
        misc_expenses_task = tg.create_task(
            general_section_extractor.run(transcript, client_profiles, MiscExpense)
        )

    form = Form(
        clients=clients_task.result(),
        addresses=addresses_task.result(),
        dependents=dependents_task.result(),
        incomes=incomes_task.result(),
        other_assets=other_assets_task.result(),
        pensions=pensions_task.result(),
        loans_and_mortgages=loans_and_mortgages_task.result(),
        protection_policies=protection_policies_task.result(),
        savings_and_investments=savings_and_investments_task.result(),
        expenses=Expenses(
            loan_repayments=loan_repayments_task.result(),
            housing_expenses=housing_expenses_task.result(),
            motoring_expenses=motoring_expenses_task.result(),
            personal_expenses=personal_expenses_task.result(),
            professional_expenses=professional_expenses_task.result(),
            misc_expenses=misc_expenses_task.result(),
        ),
        objectives=Objectives(objectives=[]),
    )
    form.save(output_path)
    return form
