[⬅ All samples](README.md)

# Share a sample

A sample is one folder. You write the card (`sample.yml`) and the code; the tool writes the two pages (`README.md`, `SETUP.md`).

```text
samples/<what-it-does-in-kebab-case>/
├── sample.yml            ← the card: title, version, the job, files, descriptions of the inputs and outputs, tests
├── CHANGELOG.md          ← one section per version: ## 1.0.0 - <date>
├── flow/
│   ├── 1-Main.txt        ← one file per subflow: <order to create>-<exact subflow name>.txt
│   └── 2-My_Function.txt ← a local subflow starts with # local subflow: / # inputs: / # outputs:
├── input/                ← sample files, fictitious data only
├── expected/             ← what the flow produced on your PC
└── assets/               ← result.png (required), canvas.png, variables-pane.png ...
```

1. Copy [`templates/sample`](templates/sample) and rename the folder.
2. In PAD, select all of each subflow (**Ctrl+A**, **Ctrl+C**), paste into its file in `flow/`.
3. Fill `sample.yml`: the problem, the solution, the techniques (ids of [`techniques.yml`](techniques.yml)), the design
   choices you measured, the limits you know. What the code already says (subflows, contract, UI elements, line counts,
   regions, the CALL line) is **not** typed in the card.
4. `python tools/build_docs.py` writes `README.md` and `SETUP.md`. Read the overview as a senior consultant would
   (can I decide in a minute?), the setup as a junior would (can I rebuild it without help?).
5. Open a pull request. The check runs `tools/build_docs.py --check`: every input and output needs a description,
   every file in `flow/` a line under `subflows:`, every technique an entry in `techniques.yml`, the category an
   entry in `categories.yml`. A new category or technique is added in its file, in the same pull request, with its summary.

The website is built from the same pages, nothing to write twice. To see it on your PC before the pull request:

```text
pip install -r tools/requirements-site.txt
python tools/build_site.py
python -m http.server 8797 --directory site
```

Then open `http://localhost:8797`. After the merge, the workflow `site` publishes it on GitHub Pages.

## Rules

- **Tested**: the flow ran on your PC, the `tested:` line says on which PAD version.
- **English** names, comments and texts; variables named as in [Start here](START-HERE.md#conventions-in-the-code).
- **No personal or company data**: no real names, e-mails, paths with your user name, tenants, passwords.
  Practice passwords only, for a practice app shipped with the sample.
- **Regions** in the standard colours; settings in the first (cyan) region.
- **Comments for the reader**: a comment in the flow explains what the flow does or why. Nothing about how the file was
  produced (tools, generators, other files): the check warns about it.
- **Limits stated**: what the sample does not do, and what was not tested, is written in `limits:`.
- **The lightest path first**: a component ships a quick try (`quick_try:`), one block pasted into `Main` that asks
  nothing (no subflow, no input or output variable) and needs as few apps as possible. The check refuses a component without it.

## Versions

Every sample has its own version, `version:` in `sample.yml`, and a section per version in its `CHANGELOG.md`.
Change it in the same pull request as the change, with this rule:

| What changed | Version | Example |
|---|---|---|
| A fix that is pasted the same way (a message, a guard, a comment) | patch: 1.0.**1** | a wrong error text |
| Something new that does not change what the reader creates | minor: 1.**1**.0 | a new optional setting in the cyan region |
| The reader must create something again (a subflow, an input or output variable, a file) | major: **2**.0.0 | a new input of the local function |

A new sample starts at `1.0.0`. Add a line under `tested:` each time the flow ran on a new PAD version.

## Publishing (maintainers)

After the merge, the tag `<sample id>-v<version>` publishes the sample alone:

```text
git tag excel-range-to-html-table-v1.0.0
git push origin excel-range-to-html-table-v1.0.0
```

The workflow `release a sample` checks the pages, zips `samples/<id>/` and creates the release with the notes of `CHANGELOG.md`.
The **Download this sample** link of the sample page points to that zip.
