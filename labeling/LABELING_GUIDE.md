# Hand-labeling guide (answer key)

Each of us labels **all 100 reviews on our own** (the same 100), without talking about them, in our own sheet:
`hand_labels_braxton.csv` / `hand_labels_teenna.csv`. Fill the `label` column with **Yes** or **No** only.
`notes` is optional, but write one when a call was hard; it speeds up settling disagreements.

## Definition (the same one the model gets in prompts B and C)

> A spoiler is any detail that reveals important plot events someone wouldn't know before watching,
> like the ending, a twist, a character dying, or who the villain is.
> General opinions about acting, visuals or whether the movie is good are NOT spoilers.

## Edge-case rules (agreed together after the first round of labeling; used to settle disagreements)

| Situation | Our rule |
|---|---|
| Vague hint ("the ending will shock you") | No |
| Plot from the first 10 minutes / the trailer | No |
| Says a twist exists but not what it is | No |
| Book or comic changes ("they changed who dies") | Yes if it reveals who dies or how it ends; No if it just says things changed |
| Review says "SPOILERS" but then doesn't give any | No |

## After both sheets are done (done)

1. First round: we agreed on 62 of 100 (κ = 0.30), mostly Braxton Yes / Teenna No.
2. We wrote the edge-case rules above, then settled the 38 disagreements together in `Settle_38_Disagreements.docx`
   (final call + one line on how we decided for each).
3. `answer_key.csv` holds both labels, the final label and how it was settled (agreed rows say "agreed").
   Final key: 45 Yes / 55 No.
