## Getting Started
First, install uv [instructions can be found here](https://docs.astral.sh/uv/getting-started/installation/#standalone-installer)

Then 

```
uv sync # creates venv, installing the dependencies you will need to play around with the code

# Test inference on a transcript by using
uv run python -m scripts.run_extractor

# Create an example dataset using
uv run python -m scripts.generate_transcript

```

# Flaws Register
- I should be able to generate transcripts with whole sections missing.
- I want to re-implement a retrieval system, but have not had time to do that.
- I might instead write a 'fact extractor' which reads chunks and essentially extracts facts, which are then assigned to sections.
- When generating transcripts, I've done a bad job at making it consistent. For instance, it writes about incomes and employments separately, so these can contradict.

### Evaluation
- LLM as a judge is probably a bold choice here. However, I had a bit of a headache trying to write code to do manual comparisons of the fields. I opted for a hybrid approach: LLM as a judge and some baseline stats. The key thing missing in this work is evaluation and fine-tuning of the evaluator (!) This is a **major** flaw.

### Transcript Generation
- Biggest flaw is that I'm using an LLM in two separate calls to extract the true information. If my structured extractor is wrong, I'm going to have INCORRECT `true` data. This is super bad. However, it was the cleanest way I could think to do it without introducing a whole bunch new pydantic models. I experimented with doing this in both directions, i.e. create the model first and then write the transcript, or write the transcript and then extract the model. I think if I had more time I would do it the opposite way to as I have now - i.e. I would want to generate the models first, and from those generate transcripts. =
- The conversations do not flow naturally. If I had more time, I'd implement a `TranscriptFlowRewriter` which would take chunks of the transcript, and essentially correct the bridges between the starts of the `section` content and the `padding` content. Right now they are very jumpy, and do not look like real transcripts. 
- The transcripts are probably too perfect. I thought about much higher temperature, and previously had implemented a `Clarity` argument which I used to try and produce more diverse transcripts (i.e. some where the information was more obscure). I would do this if I were working on this more. 
- Transcript generation should be controllable by some set parameters. I want to be able to identify where my approach struggles, and generate a bunch of test cases with those exact characteristics. Again, my previous attempt at this did do this to some extent, however it was still lazy.
- I want to be able to give a free text description of the type of transcript I want generated, and I want to be able to build a test case from this. e.g. I want cases where people have many ISA accounts.   
- Persona generation is a bit lazy. Should add functionality to let the user specify the personas they want. 
- Padding generation is very lazy, another big area of improvement. I'd aim to make the padding more realistic - right now it is quite jumpy between topics.

### Lazy Implementations
- The retries for the `base_structured_extractor` are lazy. I haven't seen it cause issues, however this should really be redone.

### Code Standards
- I do not like the way I've setup the async task groups. There's lots and lots of code repetition. 
- 

