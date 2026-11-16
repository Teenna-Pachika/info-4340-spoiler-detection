"""Copy a partner's answers from the Word labeling sheet into their CSV sheet.

    python labeling/word_to_csv.py teenna                         # reads labeling/Hand_Labels_Teenna.docx
    python labeling/word_to_csv.py teenna "path/to/her_file.docx"  # or the file she sent back, any name

Writes labeling/hand_labels_<rater>.csv. Every review in the Word file is its own small table:
Review ID / Review / Spoiler? / Notes. The script stops if any label is not Yes or No, or if an ID or review
text doesn't match the CSV.
"""
import sys

import pandas as pd
from docx import Document

rater = sys.argv[1].lower()
docx_path = sys.argv[2] if len(sys.argv) > 2 else f"labeling/Hand_Labels_{rater.capitalize()}.docx"
csv_path = f"labeling/hand_labels_{rater}.csv"

sheet = pd.read_csv(csv_path)
rows = []
for t in Document(docx_path).tables:
    if t.cell(0, 0).text.strip() != "Review ID":
        continue
    rows.append({
        "review_id": t.cell(0, 1).text.strip(),
        "review_text_docx": t.cell(1, 1).text,
        "label": t.cell(2, 1).text.strip().capitalize(),
        "notes": t.cell(3, 1).text.strip(),
    })
answers = pd.DataFrame(rows)
print(f"Read {len(answers)} reviews from {docx_path}")

assert len(answers) == len(sheet), f"expected {len(sheet)} reviews, found {len(answers)}"
assert answers["review_id"].tolist() == sheet["review_id"].tolist(), "review IDs are out of order or changed"
same_text = (answers["review_text_docx"].str.split().str.join(" ")
             == sheet["review_text"].astype(str).str.split().str.join(" "))
assert same_text.all(), f"review text changed in: {answers.loc[~same_text, 'review_id'].tolist()}"
bad = answers[~answers["label"].isin(["Yes", "No"])]
assert bad.empty, f"labels must be Yes or No; fix these: {bad[['review_id', 'label']].values.tolist()}"

sheet["label"] = answers["label"].values
sheet["notes"] = answers["notes"].values
sheet.to_csv(csv_path, index=False)
print(f"Wrote {csv_path}: {(sheet['label'] == 'Yes').sum()} Yes, {(sheet['label'] == 'No').sum()} No")
