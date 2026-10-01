# Changelog - Email triage by a local AI model

## 1.0.0 - 2026-10-01

- First public version: the emails of a folder sorted by category and urgency, with a one-sentence summary, by a model that runs on the PC; a copy of each email in the folder of its category and a CSV report. The quick try triages four emails written in the block.
- Tested on Power Automate Desktop 2.72.183 on 2026-10-01 with llama3.2:3b on a PC without GPU: the three subflows pasted (0 error); `Main` ran without error on the 12 sample emails in 168 s, 10 of 12 in their expected category; the quick try ran without error in 50 s, 4 of 4 as expected. Only comments of `Triage_Email` were edited after that run (the name of the action as the designer shows it, the header of the contract): no action changed.
