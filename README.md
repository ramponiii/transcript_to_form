## Goals
Create an LLM-based pipeline to extract the client’s answers to the questions from the 
transcript of the fact-finding call and automatically complete CIF.
 
The objectives of the tasks are: 
1.  Create an LLM-based solution to extract structured data from call transcript (LLM and 
other related costs can be reimbursed) 
2.  Evaluate the performance of the proposed solution (hint: use synthetic data for 
performance evaluation) 
3.  Suggest or implement improvements to the initial solution and evaluate metrics 
improvements

## Getting Started
First, install uv [instructions can be found here](https://docs.astral.sh/uv/getting-started/installation/#standalone-installer)

Then 

```
uv sync # creates venv, installing the dependencies you will need to play around with the code

# In a separate terminal, spin up the vector db, by running
uv run chroma run --path ./chroma_db

# Test inference on a transcript by using
uv run python -m transcript_to_form -o my_output_directory

# Create an example dataset using
uv run python scripts/create_dataset.py

# Run very basic eval on example dataset using
# this is very slow as the example set has around 3k chunks, and these all need to be ingested to the VDB (and currently embeddings are being run locally).
uv run python scripts/run_evaluation.py

# Run the (very) minimal tests on client identifier by using
uv run pytest
```

## About My Approach
I want to build something which works robustly. I don't want to have to worry about context limits, or producing very long output forms. I want to decompose the problem into small steps, each of which I have lots of control over. In this way, I can build something which I can improve more easily over time, observe better, and (attempt!) to optimize for performance.

I have built something which I evaluate into distinct parts. I evaluate retrieval, and I evaluate the writing of structured outputs. Creating separation between these two allows the LLM to do less in any one call - and allows me to understand where the weaknessess of the approach lie.

### Client Identification
I first produce a **Client Identification** object. This could have been done by extracting client names from the transcript with regex. However, I want my approach to work with different speech-to-text systems. I do not want to tie myself to the exact format of transcript given. 

This object contains aliases of the client to ensure that I can provide context to allow the model / retrieval system to know that when I want information about a name (e.g. 'James'), this is synonymous with the name used in transcript (e.g. 'CLIENT1'). This also contains a short description string, allowing me to provide the LLM with more context on the situation (as I opt not to process the transcript all at once)

### Pre-Processing
I chunk my transcript using some naive logic. Intuitively, I expect conversations between a financial advisor and client/s to be of the question, answer style. Thus initially, my chunks are formed simply by concatenating transcript messages, starting with an advisor message, with at least one client message, until the next advisor message is found. 

``` Example
(advisor, client1, advisor, client1, client2, advisor, ...) 

# I'd extract the chunks --->

(advisor, client1) , (advisor, client1, client2), (advisor, ...)
```

This is not robust as I don't control how much text is being embedded. The chunks could thus become large, and lose semantic meaning. See the Future Ideas section below for how I would improve this.

I append to each chunk an ID. This ID allows me to provide (naive) sourcing. In the pydantic models I ask the llm to produce, a sourcing field is added, so that I can quickly see what content the llm chose to identify that it used to write some content. This is not perfect, but I found it useful for debugging.

When a chunk is retrieved, I added a system to expand from this chunk to capture the surrounding conversation. This was not optimized in any way. This allows me to ensure enough context is gathered around the retrieved point for it to be fully understood.

### Structured Generation
For this I simply used the openai structured responses endpoint. I have not used this before, but thought it was pretty neat, and well suited for this task. 

### Evaluation of my Approach
In hindsight, I'd like to have done things differently. I think that's the nice thing about building things quickly: you get an idea for a problem, try it out, and have a better idea for the next iteration.

To evaluate my approach, I've placed emphasis on evaluating retrieval (which is in my opinion, the critical part of the approach I chose). If I can't retrieve the correct chunks, it all falls apart. My retrieval evaluation indicated that some sections of the form are far more sensitive (using my current implementation) to retrieval than others. 

For instance, information around the basic client information, shower really poor retrieval results. It suggests either I've not put enough care into my synthetic data generation (very likely), but also that my retrieval system is not as well suited for these sections.

With more time, I'd specifically add:
- needle in the haystack type tests, where we have lots of irrelevant content
- LLM as a judge to actually assert that the content we want to find is the content retrieved
- more variation in the way transcripts were written
- add 'wishy washy' content, which answers no question, and just pads the vector database to make retrieval harder
- confusion matrices to see which sections are getting retrieved in place of one another

### General Comments
1. I do not want to try and generate long transcripts. This sounds like a hard thing to do well.
2. I want to build a system which I can control
3. I want my system to easily work with different types of form
4. I want my system to be explainable
5. I want to be able to provide sources for any written LLM text

### Costs
- Costs around $0.10 to produce 500 examples for evaluation
- Costs around $0.05 to fill the form for the first example transcript

### Assumptions 
- I assume that conversations between advisors and clients are naturally parsable into chunks. This is a big assumption. The quality of my retrieval system will be heavily dependent on the quality of the chunking, I chose something very simple here, but this would require a lot more thought to get it production ready.

- I assume that the transcript may not necessarily contain answers to fill all of the fields.
- I assume that I want this process to be cheap to run, and set myself the limit of $0.05 per transcript.
- I assume that the user cares deeply about being able to see why given text was written. Thus, I get the LLM to (lazily) provide sources for each written field in the form.

### Approximate Time Spend
~3hrs friday, bulk of the logic around client identification and building of pydantic model objects
~6hrs saturday, got the system running end to end + added costing
~4hrs sunday, built evaluation suite + cleaning code

# Ideas Board
- lots of code cleaning is needed. Things got a bit rushed towards the end!
- unit tests...
- The retrieval setup I have used is very lazy. Something more like [Anthropic's contextual retriever](https://www.anthropic.com/news/contextual-retrieval) would suit this problem nicely in my opinion. It's extremely lazy to use the chroma built in embedder, performance would be much better using an api for the embeddings (done this way out of laziness).
- My cost counting is pretty lazy. I'd like to add traces to the code. I'd like to better understand how long the different parts of the process take to optimize them. 
- Better analysis could involve looking to see how recall is affected by transcript quality. I'd like to introduce more cases where fields are missing, allowing for better analysis to ensure the model does not hallucinate details.
- Retrieval could look to first produce summaries of the chunks. You could then finetune an embedding model on these produced summaries, to give you more control of the system.
- 