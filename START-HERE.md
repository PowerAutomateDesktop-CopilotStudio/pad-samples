[⬅ All samples](README.md)

# Start here: your first paste in 3 minutes

A Power Automate Desktop flow is text. You can copy it from this site and paste it into PAD, exactly like text into Word.
PAD turns it back into actions on the canvas.

## What PAD needs before the paste

The paste brings **the actions, their settings, the variables they create and the UI elements**. It does not bring:

| Not carried by the paste | Where each sample tells you | Guide |
|---|---|---|
| 🧩 Subflows other than `Main` | Step "Create the flow and its subflows" | [Create a subflow](docs/create-a-subflow.md) |
| 📥 Input and output variables | Step "Create the input and output variables" | [Create variables](docs/create-variables.md) |
| ✋ Settings such as *Mark as sensitive* | Step "The step the paste cannot do" | [Sensitive values](docs/sensitive-values.md) |
| 📁 Your files and folders | Step "Prepare the files" | |

If a sample says **none** for all four, you only paste into `Main`.

## Your first paste

1. Open a sample from the [gallery](README.md). If its page shows **In a hurry? Try it in 2 minutes**, that block is all you need.
2. In PAD select **+ New flow**, give it a name, select **Create**. The designer opens on `Main`.
3. On the sample page, open **Show the code** (or the file of the quick try), select the copy button at the top right of the block.
4. Click once on the empty canvas of `Main`, press **Ctrl+V**. The actions appear.
5. Compare with the sample page: same number of lines, Errors pane empty. Select **Run**.

## How to read a variable name

Every sample names its variables the same way, so a name tells you what it is:

```text
in_loc_txt_WorkbookPath
│  │   │   └── what it holds
│  │   └────── type: txt Text · num Number · bool Boolean · date Datetime · lst List · tbl Datatable · row Datarow · inst Instance
│  └────────── scope: glob = the whole flow · loc = one subflow
└───────────── direction: in = you give it · out = it gives back · (nothing) = working variable, created by the paste
```

## Region colours

Every flow is cut into coloured regions, always in the same colours:

| Colour | Region |
|---|---|
| 🟦 cyan | settings: the only values you change |
| 🟥 red | guards: what is checked before the work |
| 🟩 green | reading the input |
| 🟪 purple | the processing |
| 🔷 blue | sub-steps, loops |
| 🟨 gold | the output |
