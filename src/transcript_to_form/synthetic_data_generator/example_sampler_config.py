import numpy as np
from scipy import stats

from ..models import (
    Address,
    ClientInformation,
    Dependent,
    Employment,
    Expense,
    HealthDetails,
    Income,
    LoanOrMortgage,
    Objectives,
    OtherAsset,
    Pension,
    ProtectionPolicy,
    SavingOrInvestment,
)
from .models import SamplerConfig
from .specific_user_requests import USER_REQUESTS

# lazy. I want to allow the llm to write outputs and spread them over a few different chunks,
# which is where the retrieval system will be most tested. To do this, I want to be able to know
# for some given information, how often is it spread over lots of messages. This distribution should
# vary depending on the form field being filled out, below I took a simple discrete distribution which
# will aim to spread information over 3 chunks 50% of the time, 2 chunks 40% and in one chunk 10% of the time.
SIMPLE_SAMPLER = stats.rv_discrete(
    name="SIMPLE_SAMPLER", values=(np.arange(1, 4), (0.1, 0.4, 0.5))
)


example_config = SamplerConfig(
    models=[
        Address,
        ClientInformation,
        Dependent,
        Employment,
        Expense,
        HealthDetails,
        Income,
        LoanOrMortgage,
        Objectives,
        OtherAsset,
        Pension,
        ProtectionPolicy,
        SavingOrInvestment,
    ],
    specific_requests=USER_REQUESTS,
    total_samples_per_model=20,
    segments_distribution=SIMPLE_SAMPLER,
    prop_high_quality=0.1,  # could use similar sampler setup for proportion of transcript as high quality
    prop_medium_quality=0.4,
    prop_low_quality=0.5,
)
