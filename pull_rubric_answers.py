"""Pull ONLY the 25 Claude answers we score with the rubric: 25 borderline reviews x prompt C = 25 paid calls.

    venv-final\\Scripts\\python.exe pull_rubric_answers.py

Uses the exact prompts and call from spoiler_detection.ipynb (the prompts are read from the notebook itself),
and saves to outputs/rubric_answers_25.json. The notebook's full run later reuses these 25 answers instead of
calling again, so the answers we score are the same ones in the results. Running it twice never calls twice.
"""
import json
import os
import time

import anthropic
import pandas as pd
from dotenv import load_dotenv

OUT = "outputs/rubric_answers_25.json"
GEN_MODEL = "claude-sonnet-5-5"          # same as the notebook
N_RUBRIC_REVIEWS = 25
RUBRIC_PROMPT = "C"                      # definition + examples (best Week 7 prompt)

if os.path.exists(OUT):
    raise SystemExit(f"{OUT} already exists; no calls made.")

# the prompts, straight from the notebook cell that defines them
nb = json.load(open("spoiler_detection.ipynb", encoding="utf-8"))
prompt_cell = next("".join(c["source"]) for c in nb["cells"]
                   if c["cell_type"] == "code" and "PROMPTS = {" in "".join(c["source"]))
ns = {}
exec(prompt_cell, ns)
PROMPTS = ns["PROMPTS"]

val = pd.read_csv("data/validation_sample.csv")
rubric_reviews = val[val["borderline"]].sample(N_RUBRIC_REVIEWS, random_state=4340).sort_values("review_id")

load_dotenv()                            # reads the key from .env (never committed)
api_key = os.environ.get("ANTHROPIC_API_KEY")
assert api_key, "No API key found: put ANTHROPIC_API_KEY in the .env file first"
client = anthropic.Anthropic(api_key=api_key)


def classify_text(text, prompt_name):
    """Same call as the notebook's classify_text (Class 11-12)."""
    start = time.time()
    response = client.messages.create(
        model=GEN_MODEL,
        max_tokens=2000,
        messages=[{"role": "user", "content": PROMPTS[prompt_name].format(review=text)}]
    )
    return {
        "answer": "".join(block.text for block in response.content if block.type == "text"),
        "input_tokens": response.usage.input_tokens,
        "output_tokens": response.usage.output_tokens,
        "response_time_s": round(time.time() - start, 2),
    }


results = []
for _, row in rubric_reviews.iterrows():
    r = classify_text(row["review_text"], RUBRIC_PROMPT)
    r["prompt"], r["review_id"] = RUBRIC_PROMPT, row["review_id"]
    results.append(r)
print(f"Prompt {RUBRIC_PROMPT}: {len(results)} reviews done")

os.makedirs("outputs", exist_ok=True)
json.dump(results, open(OUT, "w"), indent=1)
cost = sum(r["input_tokens"] for r in results) * 2 / 1e6 + sum(r["output_tokens"] for r in results) * 10 / 1e6
print(f"Made {len(results)} calls, saved {OUT} (about ${cost:.3f})")
