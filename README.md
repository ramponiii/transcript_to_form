## Getting Started
First, install uv [instructions can be found here](https://docs.astral.sh/uv/getting-started/installation/#standalone-installer)

Then you will need a pinecone api key, I made a free account [here](https://app.pinecone.io/organizations/-/keys)

```
uv sync # creates venv, installing the dependencies you will need to play around with the code

# Test inference on a transcript by using
uv run python -m scripts.run_extractor

```

# High Level Description of my work
All of my work heavily uses pydantic, and openai structured outputs. I had never used openai structured outputs before, we don't use it at work, so thought it was a good chance to have a play with it. And I'm impressed. 

I also took the chance to try out pinecone, though am not overly impressed at their async support. Earlier editions of this take home used chroma.

## Synthetic Transcripts
- I wanted these to be controllabe, so introduced a TranscriptConfig model which I'd like to be more customizable.

The steps are:
1. Generate personas for the financial and advisor if not given, using an LLM with a high temperature.
2. Generate a list of desired things we want to extract, these are populated pydantic models, and should be able to be provided in the config in the long run (though right now an LLM Generates them)
3. Use the passed in config and the desired model to generate the `form section` parts of the dialogue - these are the parts of the dialogue which should contain the answers. This is checked using a second llm call, which verifies that all of the expected information is discussed in the transcript.
4. Generate padding, using a range of seed topics, to pad the length of the conversation while not introducing new information (* can't confirm it doesn't introduce new info...)
5. Generate a long intro and outro, again to pad the conversation.

## Extraction
1. First, extract the name and basic info around the clients. This is useful at all stages of extraction to give some context on the conversation.
2. Now, extract client specific objects, while in parallel extracting all of the other sections.
3. For each section...
3a. use the retrieval queries for the model instance to query a pinecone VDB, retrieving back N chunks, and then expanding to get the prior K and following K chunks from it, so that each retrieved chunk is contextualized. 
3b. On the retrieved content, identify how many different model instances we need to extract (e.g. multiple incomes) - I call these model summaries
3c. Run extraction for the desired model summaries, producing the final desired pydantic models.
3d. run the checker, which verifies the extract content looks reasonable and does not belong in a different section.

Extraction also has a failure mechanism, whereby if openai fails to return a model object, I append to the system prompt and try again. In practice I have never seen it fail, so this work was overkill.

I spent some time trying to condense the transcript, which I think I would want to spend more time on if I had more time. Probably something akin to fact extraction.

## Evaluation
I use two types of evaluation
- Simple evaluation, using basic stats around how often fields are filled, which gives me a quick over view of how things are doing (spoiler: they are not doing well)
- LLM as a judge - I struggled to write manual code quickly to compare the fields using their actual datatypes, instead I was lazy and use an LLM to compare the results. This code is poorly written and not very well thought out. 

## Big Picture Problems
- I've tried to modularize the code, the advantage of that being that it gives me control and the ability to fine tune different parts of the system. However, I've not got far enough in to really feel the advantage of that. I'd like to be able to run my analysis, identify the troublesome area, write some failing tests, and improve, but this has not been possible in the time. 

- Lack of testing around the evaluation code is very poor work. This should be my ground truth, however there could well be some foo bar like mistakes in there. In hindsight, I think I should have gone for TDD, and tried to write expected forms frmo the two synthetic transcripts you gave me to begin with. Getting good performance on even those two would indicate it at least partially does its' job.

### Extraction Quality Analysis 
I ran an evaluation on 42 synthetic transcripts. I'm still working out the best metrics to use, but here’s what I’m currently tracking:

- Filled Proportions – Percentage of fields filled in the true vs predicted forms.

- Most Common Field Failures – Which field names fail most frequently.

- Misplacement Trends – Which sections often contain info that belongs elsewhere.

- Accuracy by Section – Identical + partial matches as a measure of section-level quality.

- Misplacements by Section – How often info ends up in the wrong plac
---
### Basic Stats Eval 
Some sections are clearly missing a lot of information. For example, Dependents has a 95% fill rate in the true forms, but only 14% in predictions — something is clearly going wrong there.

Similarly, Other Assets, Addresses, Pensions, and Health Details all have true-form fill rates over 90%, but predicted values are below 40%. I haven’t looked into these deeply yet, but I expect these failures are due to some obvious issue in retrieval, parsing, or synthetic data setup.

### LLM as a judge 

Performance varies a lot by section:

- Best performing: Client Info (51% identical matches), followed by Employments (48%).

- Worst performing: Dependents (6%), Other Assets (14%), Pensions (19%).

Interestingly, the poorly performing sections also show low misplacement rates, which suggests they’re not being extracted at all — likely a retrieval failure.

Some sections, especially the expenses categories (e.g. misc, personal), are frequently misplaced. This makes sense in hindsight. I tried to extract each expense type independently, but probably should have just pulled all expenses and then categorized them after.

I had implemented a checker to reduce this duplication, but it hasn’t helped much. There’s still frequent duplication and overlap between sections. This could be a result of poor synthetic transcript generation, which doesn’t enforce enough structure.

**Overall Results**

- Identical matches: 31%

- Partial matches: 10%

- Fields only in true form: 32% ← biggest problem category

- Incorrect fields: 8.7%

- Contradictions (true vs pred): 2% ← surprisingly low (good sign)

A lot of the "only in true" errors seem to come from isolated failures on specific forms. For instance, when Addresses fails, it tends to fail completely, which causes large gaps. This is likely a result of weak or missing retrieval logic.

Another issue is the extractor occasionally outputs empty objects — I haven’t looked closely into this yet. Could also be due to me relaxing validation constraints in the synthetic transcript generator (e.g., removing checks for client info, employments, etc.) just to get the pipeline running.

That decision — removing tests because they were failing — is not best practice... but I did it to save time. 

#### Common Field Failures
```
# most common fields which were wrong
('name', 116), ('timeframe', 107), ('amount', 102), ('owner', 89), ('frequency', 59),
```
- name and owner are probably fixable by passing in the client’s name during extraction.

- timeframe and frequency are typically properties of objects like Expense or Income. These fields are often null or partially filled — which skews things.

The extractor tends to pull either too many objects, or objects with only one field (like name) populated.

This is probably an issue with the retrieval pipeline or summary logic. I might need to break object extraction into one call per expected object.

### Proposed Improvements 
1. When generating synthetic transcripts, I should better ensure they are not contradictory. For instance right now, a loan might come through in the expenses sections or in the 'mortgages and loans' section. Because these are not aware of each other, right now, transcripts may populate both, and the expected form will be wrong. And thus I may be evaluating against incorrect 'true' forms (which is likely to be the case). To resolve this, I'd take another think about how I could go about seeding the generation.

2. Retrieval needs to be properly evaluated and tested, I suspect this is a cause of many failures, though not confirmed.

3. I would rework extraction of expenses, instead of extracting each type of expense id extract a list of expenses and categorize them. This is because my analysis suggests these fields are often misplaced.

4. I'd pass in the name of the client to each extraction call, as right now it won't have the context that 'CLIENT' has a real name, and thus evaluation is failing (and it looks silly). This would be a simple fix. This is because of the analysis around the fields with the most failures.

5. I'd improve the transcript quality by re-writing them using a re-writer, to basically make the convo more natural. I'd probably also re-introduce the transcript quality parameter to the prompt that I had implemented before. This is just a general comment, not inspired by the analysis.

6. The results show that a number of sections are performing abysmally. There is probably a foo bar mistake somewhere in my code, or thinking. I should find and fix this.

7. I should generate more transcripts with whole sections missing. These are interesting test case which I set myself up to do, then didn't take advantage of.

8. LLM as a judge is probably a bold choice here. However, I had a bit of a headache trying to write code to do manual comparisons of the fields. I opted for a hybrid approach: LLM as a judge and some baseline stats. The key thing missing in this work is evaluation and fine-tuning of the evaluator (!) This is a **major** flaw.

9. The transcripts are too LLM like. I thought about much higher temperature, and previously had implemented a `Clarity` argument which I used to try and produce more diverse transcripts (i.e. some where the information was more obscure). I would do this if I were working on this more. 
