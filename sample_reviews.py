"""Draw the final-project samples from the IMDB Spoiler Dataset (Rishabh Misra, Kaggle).

Run once. It needs the two raw files, which are too big for GitHub (950 MB). Download them from
https://www.kaggle.com/datasets/rmisra/imdb-spoiler-dataset into data/raw/, or pass --raw-dir.

    python sample_reviews.py --raw-dir ../Week7-Evaluation

Writes (all small enough to commit):
  data/validation_sample.csv   100 reviews to hand-label: our answer key (feedback: "build your own answer key")
  data/train_sample.csv        10,000 other reviews for the non-AI baseline (trained on the dataset's own tag)
  data/corpus_summary.json     summary stats of the full corpus, for the Data section
  labeling/hand_labels_braxton.csv, labeling/hand_labels_teenna.csv   blank labeling sheets

Sampling on purpose (feedback: "oversample borderline reviews"): half of the validation sample is
"borderline" (mentions twists, the ending, deaths, hints, or book/comic changes), half is regular.
Within each half, half are tagged spoiler in the dataset and half are not.
"""
import argparse
import json
import re
from pathlib import Path

import pandas as pd

SEED = 42
N_VALIDATION = 100             # 50 borderline + 50 regular, each split 25 tagged spoiler / 25 not
N_TRAIN = 10_000
MIN_CHARS, MAX_CHARS = 300, 1500
BORDERLINE = re.compile(
    r"\b(?:twists?|ending|the end|dies|died|death|killed|kills|reveals?|revealed|turns out|surprise|"
    r"spoilers?|hints?|book|novel|comic|comics|adaptation)\b", re.IGNORECASE)

parser = argparse.ArgumentParser()
parser.add_argument("--raw-dir", default="data/raw")
args = parser.parse_args()
raw = Path(args.raw_dir)
out = Path(__file__).parent

# ---- descriptive stats after every step, so any data loss (or a shift in who is left) is visible
steps = []


def record_step(name, rows, spoiler_share, mean_rating, median_chars, n_movies):
    steps.append({"step": name, "rows": int(rows), "spoiler_share": round(float(spoiler_share), 4),
                  "mean_rating": round(float(mean_rating), 3), "median_chars": int(median_chars),
                  "n_movies": int(n_movies)})
    print(f"{name:<40s} rows = {rows:>9,}   spoiler share = {spoiler_share:.1%}")


def record_df(name, df):
    record_step(name, len(df), df["is_spoiler"].mean(), df["rating"].mean(),
                df["review_text"].str.len().median(), df["movie_id"].nunique())


# ---- read the 950 MB reviews file in chunks; keep light columns for ALL rows (for stats on what is dropped)
kept, light = [], []
for chunk in pd.read_json(raw / "IMDB_reviews.json", lines=True, chunksize=50_000):
    n_chars = chunk["review_text"].str.len()
    in_window = n_chars.between(MIN_CHARS, MAX_CHARS)
    light.append(pd.DataFrame({"movie_id": chunk["movie_id"], "is_spoiler": chunk["is_spoiler"],
                               "rating": chunk["rating"], "n_chars": n_chars, "in_window": in_window}))
    kept.append(chunk[in_window])
light = pd.concat(light, ignore_index=True)
reviews = pd.concat(kept, ignore_index=True)
total, n_spoiler, lengths = len(light), int(light["is_spoiler"].sum()), light["n_chars"]
assert total == 573_913, "expected 573,913 reviews in the raw file"

record_step("0 raw file", total, light["is_spoiler"].mean(), light["rating"].mean(),
            light["n_chars"].median(), light["movie_id"].nunique())
dropped = light[~light["in_window"]]
record_step("   (dropped: outside 300-1,500 chars)", len(dropped), dropped["is_spoiler"].mean(),
            dropped["rating"].mean(), dropped["n_chars"].median(), dropped["movie_id"].nunique())
record_df("1 kept 300-1,500 characters", reviews)
assert len(reviews) + len(dropped) == total, "length filter lost rows it didn't report"

# ---- cleaning: drop exact duplicate texts and blank reviews before sampling
before = len(reviews)
reviews["review_text"] = reviews["review_text"].str.strip()
reviews = reviews[reviews["review_text"].ne("")]
record_df("2 dropped blank reviews", reviews)
reviews = reviews.drop_duplicates("review_text").reset_index(drop=True)
record_df("3 dropped duplicate texts", reviews)

movies = (pd.read_json(raw / "IMDB_movie_details.json", lines=True)[["movie_id", "genre", "rating"]]
          .rename(columns={"rating": "movie_rating"}))
assert len(movies) == 1_572
movies["genre"] = movies["genre"].apply(lambda g: ", ".join(g) if isinstance(g, list) else "")
n_before_merge = len(reviews)
reviews = reviews.merge(movies, on="movie_id", how="left")
assert len(reviews) == n_before_merge, "the movie merge must not add or drop rows"
reviews = reviews[reviews["genre"].fillna("").ne("")].reset_index(drop=True)
record_df("4 dropped reviews with no genre", reviews)
reviews["borderline"] = reviews["review_text"].str.contains(BORDERLINE)
print(f"borderline share: {reviews['borderline'].mean():.1%}")

# ---- validation sample: 4 cells (borderline x tag), 25 each
per_cell = N_VALIDATION // 4
val = (reviews.groupby(["borderline", "is_spoiler"])
       .sample(n=per_cell, random_state=SEED)
       .sample(frac=1, random_state=SEED)          # shuffle so labelers can't see the strata
       .reset_index(drop=True))
val.insert(0, "review_id", [f"V{i + 1:03d}" for i in range(len(val))])
assert len(val) == N_VALIDATION
assert val.groupby(["borderline", "is_spoiler"]).size().eq(per_cell).all()

# ---- training sample for the baseline: no overlap with validation, same movies allowed
rest = reviews[~reviews["review_text"].isin(val["review_text"])]
train = rest.sample(N_TRAIN, random_state=SEED).reset_index(drop=True)
assert not set(train["review_text"]) & set(val["review_text"]), "train and validation must not overlap"

record_df("5a validation sample (stratified)", val)
record_df("5b training sample (random)", train)

# n_chars is saved so the notebook can prove the CSV round trip didn't cut or change any review text
val["n_chars"] = val["review_text"].str.len()
train["n_chars"] = train["review_text"].str.len()
cols = ["review_id", "movie_id", "genre", "movie_rating", "rating", "is_spoiler", "borderline", "n_chars",
        "review_text"]
(out / "data").mkdir(exist_ok=True)
val[cols].to_csv(out / "data/validation_sample.csv", index=False)
train[cols[1:]].to_csv(out / "data/train_sample.csv", index=False)
pd.DataFrame(steps).to_csv(out / "data/cleaning_steps.csv", index=False)

summary = {
    "total_reviews": total, "tagged_spoiler_share": round(n_spoiler / total, 4),
    "n_movies": len(movies), "chars_median": int(lengths.median()),
    "chars_p10": int(lengths.quantile(0.10)), "chars_p90": int(lengths.quantile(0.90)),
    "in_length_window": before, "after_cleaning_with_genre": len(reviews),
    "borderline_share": round(float(reviews["borderline"].mean()), 4),
    "spoiler_share_borderline": round(float(reviews.loc[reviews["borderline"], "is_spoiler"].mean()), 4),
    "spoiler_share_regular": round(float(reviews.loc[~reviews["borderline"], "is_spoiler"].mean()), 4),
    "min_chars": MIN_CHARS, "max_chars": MAX_CHARS, "seed": SEED,
}
json.dump(summary, open(out / "data/corpus_summary.json", "w"), indent=1)

# ---- blank labeling sheets, one per rater (hand labels are ours to fill in, never the model's)
(out / "labeling").mkdir(exist_ok=True)
sheet = val[["review_id", "review_text"]].assign(label="", notes="")
for rater in ("braxton", "teenna"):
    path = out / f"labeling/hand_labels_{rater}.csv"
    if path.exists():
        print(f"kept existing {path.name} (not overwritten)")
    else:
        sheet.to_csv(path, index=False)
print(f"\nsaved {N_VALIDATION} validation reviews, {N_TRAIN:,} training reviews, corpus_summary.json")
print(json.dumps(summary, indent=1))
