# LLM Spoiler Detection on IMDb Reviews

INFO 4340 final project · Braxton Turner & Teenna Pachika

**Question:** Can an LLM flag spoilers in movie reviews well enough to replace a platform's self-reported "contains spoilers" checkbox, and at what cost?

> **Status:** complete. Hand labels, rubric scores, the paid classifier run and the judge run are all done, and the notebook runs top to bottom from the saved answers.

## Findings

- The reviewers' own spoiler checkbox disagreed with our hand-labeled answer key on 43% of reviews, so we used our own key instead.
- Claude's best prompt (C) caught 47% of spoilers (95% CI 0.32 to 0.62). The simple TF-IDF model caught 71%, and that gap is real.
- When Claude did flag a spoiler, it was right 88% of the time, but it never once said Unsure.
- Changing the prompt barely helped. Prompts A, B and C all landed between 42% and 47%.
- It's cheap, about $2.07 per 1,000 reviews, but missing spoilers is the costly mistake.
- Verdict: don't replace the checkbox with Claude alone. Use the simple model to catch spoilers, and show Claude's reason to a human moderator.

| Metric | Value |
|---|---|
| Best prompt recall on spoilers (95% CI) | 0.47 (0.32 to 0.62), prompt C |
| TF-IDF baseline recall | 0.71 (0.56 to 0.84) |
| Dataset tag agreement with our hand labels | 57% (κ 0.14) |
| Share of reviews sent to a human (Unsure) | 0% |
| API cost per 1,000 reviews | $2.07 |
| Human-human rubric κ (linear) / MDD | −0.02 (63% exact agreement) / 3.5 points of 16 |

## Data

IMDB Spoiler Dataset by **Rishabh Misra** (Kaggle: `rmisra/imdb-spoiler-dataset`). Please credit it if you reuse this work. 573,913 reviews (26.3% tagged spoiler by the reviewer) of 1,572 movies.

The raw files are 950 MB, too big for GitHub. **You don't need them to run the notebook**, because the samples are committed:

| File | What it is |
|---|---|
| `data/validation_sample.csv` | 100 reviews we hand-labeled (50 borderline + 50 regular, each split 25/25 by dataset tag) |
| `data/train_sample.csv` | 10,000 other reviews for the TF-IDF baseline |
| `data/corpus_summary.json` | summary statistics of the full corpus |

**Limitation found in the data-loss check:** the 300–1,500 character filter keeps 64.7% of reviews, and the reviews it drops are 36.4% spoilers vs. 20.8% of those kept. Results apply to short and medium reviews only. Every step's row count and descriptive stats are in `data/cleaning_steps.csv`.

To re-draw the samples: download `IMDB_reviews.json` and `IMDB_movie_details.json` into `data/raw/` and run `python sample_reviews.py` (seed 42, so you get the same rows).

## How to run

```bash
python -m venv venv-final
venv-final\Scripts\activate          # Windows (macOS/Linux: source venv-final/bin/activate)
pip install -r requirements.txt
python -m ipykernel install --user --name final-spoiler
jupyter nbconvert --to html --execute spoiler_detection.ipynb
```

The notebook runs top to bottom **without an API key**: every model answer is saved in `outputs/` (`llm_outputs.json`, `judge_runs.json`, and the smaller Class 2, 5 and 8 checks). It calls the API only if `RUN_API = True` and the cache file is missing. To re-run the calls yourself, put `ANTHROPIC_API_KEY=...` in a `.env` file (git-ignored, never committed).

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

## Limitations

- **Short and medium reviews only.** The length filter dropped longer reviews, which spoil more often (36.4% vs. 20.8%).
- **Not real-world rates.** Our 100 test reviews are half spoilers on purpose; real reviews are about 21% spoilers, so precision in practice would likely be lower.
- **Small sample, wide intervals.** Only 45 spoilers in the answer key, so recall CIs are wide (0.32 to 0.62 for prompt C).
- **Best prompt picked and scored on the same 100 reviews**, so prompt C's numbers may be slightly optimistic.
- **Small genre groups.** Several genres have only 5 to 8 spoilers, so the genre ratio is a warning, not proof.
- **TF-IDF trained on the dataset tag**, which we found unreliable, because it was the only label available for 10,000 reviews.
- **Temperature can't be set** on current Claude models, so the 3 judge runs measure the default setting.

## Workflow

- We worked in this shared GitHub repo, each committing our own work.
- Braxton built the notebook, the sampling script and the labeling files, ran the AI judge, and wrote the governance memo.
- Teenna set up the repo and `.gitignore`, built the 4-part grading rubric (from Week 7) that we both used, ran the paid classifier run (300 answers), wrote the notebook's decision and notes, wrote the README findings, limitations and workflow, and wrote the summary report.
- We each hand-labeled all 100 reviews on our own, then settled the 38 disagreements together.
- We calibrated the rubric together on our Week 7 answers, then each scored the same 25 answers on our own.
- We made the presentation slides and speaker notes together.

## AI use

Both partners used Claude (Claude Code) to help build this. Each of us keeps an individual AI use log.