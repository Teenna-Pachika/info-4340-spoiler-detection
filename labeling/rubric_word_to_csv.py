"""Copy rubric scores from a Word sheet into the CSV the notebook reads.

    python labeling/rubric_word_to_csv.py teenna                     # Rubric_Scoring_Teenna.docx -> rubric_scores_teenna.csv
    python labeling/rubric_word_to_csv.py teenna "path/to/her.docx"  # or the file she sent back

Stops if a score isn't a whole number 0-4 or an ID doesn't match. Blank boxes are listed, not filled.
"""
import sys

import pandas as pd
from docx import Document

D = ["correct_call", "evidence", "faithfulness", "usefulness"]
who = sys.argv[1].lower()


def score(x):
    x = x.strip()
    if x == "":
        return ""
    assert x in {"0", "1", "2", "3", "4"}, f"scores must be 0-4, found {x!r}"
    return int(x)


path = sys.argv[2] if len(sys.argv) > 2 else f"labeling/Rubric_Scoring_{who.capitalize()}.docx"
csv = f"labeling/rubric_scores_{who}.csv"
out = pd.read_csv(csv, dtype=str, keep_default_na=False)
rows = []
for t in Document(path).tables:
    if t.cell(0, 0).text.strip() != "Item":
        continue
    rows.append({"item": t.cell(0, 1).text.split()[0],
                 **{d: score(t.cell(2 + k, 1).text) for k, d in enumerate(D)},
                 "justification": " ".join(t.cell(6, 1).text.split())})
got = pd.DataFrame(rows)
assert got["item"].tolist() == out["item"].tolist(), "items are out of order or changed"
for c in D + ["justification"]:
    out[c] = got[c].values


out.to_csv(csv, index=False)
blank = [(i, d) for i, r in out.iterrows() for d in D if r[d] == ""]
print(f"Read {path} -> wrote {csv}: {len(out) * 4 - len(blank)} of {len(out) * 4} scores filled")
if blank:
    print("Still blank:", blank[:20])
