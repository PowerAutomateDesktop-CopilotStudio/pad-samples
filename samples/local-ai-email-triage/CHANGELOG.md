# Changelog - Email triage by a local AI model

## 1.1.2 - 2026-10-01

- Setup page: the path Reusable version asks for 3 inputs and 8 outputs (the optional trained subflows were counted in it); the values to change in the quick try each have their own description, and a text on several lines shows its first line. One comment added in `Test` above the four sample emails: no action changed, no new run needed.

## 1.1.1 - 2026-10-01

- The catalogue (`samples.json`) lists Ollama as one requirement instead of two pieces cut at a comma. The gallery card shows an illustration (`assets/cover.png`). Card only: the flow did not change, no new run needed.

## 1.1.0 - 2026-10-01

- Optional: a classifier trained on emails a person already sorted, for 92 % right instead of 68 % (cross-validated on 192 fictitious emails). New section Make it more accurate, two optional subflows (`Classify_Email_Trained`, `Triage_Trained`), the scripts `train_triage.py` and `classify_triage.py`, and 180 sorted emails in `model/`. Nothing changes for the reader who keeps the language model.
- Tested on Power Automate Desktop 2.72.183 on 2026-10-01: the five subflows pasted (0 error); `Triage_Trained` ran without error on the 12 sample emails in 77 s, 12 of 12 in their expected category, 0 to review; the training on the 180 sorted emails took 41 s and gave 91.7 % cross-validated.

## 1.0.0 - 2026-10-01

- First public version: the emails of a folder sorted by category and urgency, with a one-sentence summary, by a model that runs on the PC; a copy of each email in the folder of its category and a CSV report. The quick try triages four emails written in the block.
- Tested on Power Automate Desktop 2.72.183 on 2026-10-01 with llama3.2:3b on a PC without GPU: the three subflows pasted (0 error); `Main` ran without error on the 12 sample emails in 168 s, 10 of 12 in their expected category; the quick try ran without error in 50 s, 4 of 4 as expected. Only comments of `Triage_Email` were edited after that run (the name of the action as the designer shows it, the header of the contract): no action changed.
