# Hand-labeling guide (answer key)

Each of us labels **all 100 reviews on our own** (the same 100), without talking about them, in our own sheet:
`hand_labels_braxton.csv` / `hand_labels_teenna.csv`. Fill the `label` column with **Yes** or **No** only.
`notes` is optional, but write one when a call was hard; it speeds up settling disagreements.

## Definition (the same one the model gets in prompts B and C)

> A spoiler is any detail that reveals important plot events someone wouldn't know before watching,
> like the ending, a twist, a character dying, or who the villain is.
> General opinions about acting, visuals or whether the movie is good are NOT spoilers.

## Edge cases we decide on BEFORE labeling (fill in together, then label)

| Situation | Our rule |
|---|---|
| Vague hint ("the ending will shock you") |  |
| Plot from the first 10 minutes / the trailer |  |
| Says a twist exists but not what it is |  |
| Book or comic changes ("they changed who dies") |  |
| Review says "SPOILERS" but then doesn't give any |  |

## After both sheets are done

1. Run the notebook through section 3: it prints κ and writes `answer_key.csv`.
2. For every row with a blank `final_label`, talk it through, type the final **Yes/No**, and write one line in `how_settled`.
3. Rerun. The notebook stops if any disagreement is unsettled.
