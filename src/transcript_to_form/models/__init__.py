from typing import Type

from pydantic import BaseModel

from .client import Client
from .form import Form
from .form_sections.address import Address, Addresses
from .form_sections.client_information import ClientInformation
from .form_sections.dependents import Dependent, Dependents
from .form_sections.employments import Employment, Employments
from .form_sections.expenses import Expense, Expenses
from .form_sections.health_details import HealthDetails
from .form_sections.incomes import Income, Incomes
from .form_sections.loan_and_mortgages import LoanOrMortgage, LoansAndMortgages
from .form_sections.objectives import Objectives
from .form_sections.other_assets import OtherAsset, OtherAssets
from .form_sections.pensions import Pension, Pensions
from .form_sections.protection_policies import ProtectionPolicies, ProtectionPolicy
from .form_sections.saving_and_investments import (
    SavingOrInvestment,
    SavingsAndInvestments,
)

MODEL_RETRIEVAL_QUERY_MAPPINGS: dict[Type[BaseModel], list[str]] = {
    Addresses: [
        "Client's current home address details",
        "Any previous addresses the client has lived at",
        "Client's preferred mailing or correspondence address",
        "Address details mentioned for spouse, partner, or dependents",
        "Work address or business address mentioned by client",
        "Address of any property owned other than primary residence",
    ],
    ClientInformation: [
        "Client's full legal name as stated",
        "Client's date and place of birth",
        "Client's primary email address for contact",
        "Client's best contact phone number",
        "Client's current marital status (single, married, etc.)",
        "Client's citizenship(s) or nationalities mentioned",
        "Country of tax residency discussed",
        "Any mention of client's identification documents (passport, driver's license)",
    ],
    Dependents: [
        "Total number of people financially dependent on the client",
        "Names and ages of the client's children",
        "Details about any other dependents (e.g., elderly parents, relatives)",
        "Information about dependents' specific needs (education, health, etc.)",
        "Dependents' circumstances relevant to financial planning discussed",
    ],
    Employments: [
        "Client's current employer and job title",
        "How long has the client worked at their current job?",
        "Details about previous employers or work history",
        "Is the client self-employed, retired, or a business owner?",
        "What industry does the client work in?",
        "Any expected changes in the client's employment status or career plans?",
        "Details on profession or type of work performed",
    ],
    Expenses: [
        "Total estimated monthly living expenses",
        "Breakdown of major monthly expenditures (housing, transport, food)",
        "Spending on discretionary items or lifestyle costs (hobbies, holidays, entertainment)",
        "Details on any significant upcoming large expenses (e.g., wedding, home renovation)",
        "Discussion about unexpected costs or emergency fund needs",
        "Monthly costs associated with dependents (childcare, schooling)",
        "Utility bills or household running costs mentioned",
        "motoring expenses",
    ],
    HealthDetails: [
        "Any significant health conditions or diagnoses mentioned by the client",
        "Client's smoking habits or other health-related lifestyle factors discussed",
        "Family medical history relevant to life expectancy or future health costs",
        "Health issues mentioned that might impact life or critical illness insurance needs",
        "Discussion about long-term care needs or related costs due to health",
        "Client's general state of health as described",
    ],
    Incomes: [
        "Client's primary source of income (salary, business profit, etc.)",
        "Amount of client's main salary or wage (annual/monthly)",
        "Details about secondary income sources (rent, freelance, dividends, etc.)",
        "Information on variable income like bonuses or commissions",
        "Partner's income details if discussed in the context of household finances",
        "Expectations about future income changes (raises, job change, retirement impact)",
        "Discussion about income stability or job security",
        "Gross vs Net income mentioned",
    ],
    LoansAndMortgages: [
        "Outstanding balance on the client's mortgage(s)",
        "Interest rate, term, and repayment amount for the mortgage",
        "Details of other outstanding personal loans (car loan, student loan, etc.)",
        "Current balances on credit cards or revolving debt",
        "Total monthly payments across all loans and mortgages",
        "Secured vs unsecured debts mentioned",
        "Details about specific lenders for loans or mortgages",
        "Expected payoff dates or duration remaining on debts",
    ],
    Objectives: [
        "Client's primary long-term financial goals (e.g., retirement age, wealth transfer)",
        "Medium-term objectives (e.g., paying off mortgage, funding child's education)",
        "Short-term financial goals (e.g., saving for a holiday, buying a car)",
        "Discussion about desired lifestyle in retirement or future",
        "Client's motivation or reasons for seeking financial advice",
        "Prioritization of different financial goals discussed",
        "Goals related to leaving an inheritance or supporting family",
        "Risk tolerance discussed in relation to achieving financial objectives",
    ],
    OtherAssets: [
        "Details about vehicles owned (make, model, value)",
        "Mention of valuable personal property (art, jewelry, collectibles)",
        "Ownership stakes in private companies, partnerships, or businesses",
        "Value or details of assets held overseas",
        "Any significant assets not categorized as property, investments, or pensions",
        "Discussion about selling or acquiring other assets",
    ],
    Pensions: [
        "Details of defined contribution pension plans (e.g., 401k, SIPP)",
        "Information about defined benefit or final salary pensions",
        "Current value or projected value of pension funds",
        "Regular contributions being made to pensions by client and employer",
        "Discussion about state pension entitlement or expectations",
        "Details of spouse's pension arrangements if relevant to joint planning",
        "Names of pension providers or platforms",
        "Desired retirement age or plans for accessing pension funds",
    ],
    ProtectionPolicies: [
        "Details of any life insurance policies held",
        "Mention of critical illness cover",
        "Details about income protection policies",
        "Total sum assured or coverage amount for life insurance",
        "Monthly or annual premiums paid for insurance policies",
        "Names of insurance providers or companies",
        "Who are the beneficiaries on life insurance policies?",
    ],
    SavingsAndInvestments: [
        "Total cash held in bank accounts (checking, savings)",
        "Details about ISAs, GIA, or taxable brokerage investment accounts",
        "Names of investment platforms or brokers used",
        "Types of investments held (stocks, bonds, funds, property funds, etc.)",
        "Approximate current value of investment portfolio",
        "Discussion about investment risk tolerance or attitude to risk",
        "Details of any recent large contributions or withdrawals from investments/savings",
        "Savings goals or reasons for holding cash/investments",
    ],
}
