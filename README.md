# LLM Spoiler Detection on IMDb Reviews

INFO 4340 final project · Braxton Turner & Teenna Pachika

**Question:** Can an LLM flag spoilers in movie reviews well enough to replace a platform's self-reported
"contains spoilers" checkbox, and at what cost?

> **Status:** pipeline built and dry-run tested. Hand labels, rubric scores and the one paid API run are still to do.
> The Findings section is filled in after that run.

## Findings

*(to fill in from `outputs/headline_metrics.csv`)*

| Metric | Value |
|---|---|
| Best prompt recall on spoilers (95% CI) |  |
| TF-IDF baseline recall |  |
| Dataset tag agreement with our hand labels |  |
| Share of reviews sent to a human (Unsure) |  |
| API cost per 1,000 reviews |  |
| Human-human rubric κ (linear) / MDD |  |

## Data

IMDB Spoiler Dataset by **Rishabh Misra** (Kaggle: `rmisra/imdb-spoiler-dataset`). Please credit it if you reuse this work.
573,913 reviews (26.3% tagged spoiler by the reviewer) of 1,572 movies.

The raw files are 950 MB, too big for GitHub. **You don't need them to run the notebook**, because the samples are committed:

| File | What it is |
|---|---|
| `data/validation_sample.csv` | 100 reviews we hand-labeled (50 borderline + 50 regular, each split 25/25 by dataset tag) |
| `data/train_sample.csv` | 10,000 other reviews for the TF-IDF baseline |
| `data/corpus_summary.json` | summary statistics of the full corpus |

**Limitation found in the data-loss check:** the 300–1,500 character filter keeps 64.7% of reviews, and the
reviews it drops are 36.4% spoilers vs. 20.8% of those kept. Results apply to short and medium reviews only.
Every step's row count and descriptive stats are in `data/cleaning_steps.csv`.

To re-draw the samples: download `IMDB_reviews.json` and `IMDB_movie_details.json` into `data/raw/` and run
`python sample_reviews.py` (seed 42, so you get the same rows).

## How to run

```bash
python -m venv venv-final
venv-final\Scripts\activate          # Windows  (macOS/Linux: source venv-final/bin/activate)
pip install -r requirements.txt
python -m ipykernel install --user --name final-spoiler
jupyter nbconvert --to html --execute spoiler_detection.ipynb
```

The notebook runs top to bottom **without an API key**: every model answer is saved in `outputs/`
(`llm_outputs.json`, `judge_runs.json`, and the smaller Class 2, 5 and 8 checks). It calls the API only if `RUN_API = True` and the cache file is missing.
To re-run the calls yourself, put `ANTHROPIC_API_KEY=...` in a `.env` file (git-ignored, never committed).

## Repo layout

| Path | Purpose |
|---|---|
| `spoiler_detection.ipynb` / `.html` | the notebook: one part per class (2, 3-4, 5-6, 8, 11-12, 7, 13-14), then our results |
| `sample_reviews.py` | draws the samples from the raw Kaggle files |
| `labeling/` | labeling guide, calibration notes, our hand labels, answer key, rubric scores |
| `outputs/` | cached model answers, judge scores, result tables, figures |

## Methods (short)

- **Structure:** the notebook builds on Dr. Stefani's class notebooks in order, using her code on our data.

- **Answer key:** our own hand labels (κ reported), not the dataset tag.
- **Baselines:** majority class, keyword rule, TF-IDF + logistic regression.
- **LLM:** `claude-sonnet-5-5`, 3 prompts (basic / + definition / + definition + examples), with an Unsure option that routes to a human.
- **Metrics:** recall on spoilers (headline), precision, F1, share to human, cost-weighted error; 95% bootstrap CIs (1,000 resamples); paired-difference CIs.
- **Subgroups:** recall by borderline/regular and by genre; min/max recall ratio (0.80 rule).
- **Explanation quality:** 4-dimension rubric, linear-weighted κ, MDD = mean + 1 SD of absolute rater differences, LLM judge (`claude-opus-5-5`) run 3×.

## AI use

Both partners used Claude (Claude Code) to help build this. Each of us keeps an individual AI use log.
