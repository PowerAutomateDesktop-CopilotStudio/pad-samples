# Changelog - Excel range to an email-ready HTML table

## 1.1.1 - 2026-10-01

- The gallery card shows an illustration (`assets/cover.png`); the card names Anne among the authors; the pages follow the new layout of the lab (prerequisites, cards). The flow did not change: no new run needed.

## 1.1.0 - 2026-09-29

- The quick try (`Test`) needs Excel only: the table opens in the browser. The Outlook email becomes an option, `bool_SendToOutlook` in the first region (`False` by default).
- Comments of `Convert_Excel_To_Html` and `Test` no longer refer to files and tools that are not in the sample. No action of `Convert_Excel_To_Html` changed (44 lines).
- Tested on Power Automate Desktop 2.72.183 on 2026-09-29: the quick try pasted into `Main` (77 lines, 0 error), run without error in 46 s, table opened in the browser; it runs the same conversion script as `Convert_Excel_To_Html`.

## 1.0.0 - 2026-09-28

- First public version: `Main` (example call), the local function `Convert_Excel_To_Html` (3 inputs, 8 outputs) and the one-block demo `Test`.
- Tested on Power Automate Desktop 2.72.183 on 2026-09-26: the table written by `Main` is identical to `expected/Sales_Report_2026-Q3_table.html`.
