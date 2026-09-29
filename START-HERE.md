[All samples](README.md)

# How the samples are organised

Every sample follows the same layout, the same page structure and the same conventions.
Once you have read one, you know where to find everything in all the others.

## Who makes these samples

**Anne** is an AI agent specialised in Power Automate Desktop and Copilot Studio projects. Anne designs, builds and
tests every sample, and publishes all of it: the flow or agent files, the sample data, the expected results and the
test record of each version. [Franck Mongo](https://www.linkedin.com/in/franckmongo/) (HyperAutomatisation) runs Anne and maintains the collections.

Have an automation challenge you would like Anne to take on? [Submit it](https://github.com/anne-automates/anne-automates.github.io/issues/new?template=submit-a-challenge.yml): the next samples come from
your challenges. For a private request, write to [Franck Mongo on LinkedIn](https://www.linkedin.com/in/franckmongo/).

## One folder per sample

```text
samples/<what-it-does>/
├── README.md        overview: problem, solution, contract, design, limits, tested versions
├── SETUP.md         step by step: files, subflows, variables, paste, run, adapt, troubleshooting
├── CHANGELOG.md     one section per version
├── sample.yml       the card both pages are generated from
├── flow/            one text file per subflow, named <order to create>-<exact subflow name>.txt
├── input/           sample files (fictitious data)
├── expected/        what the flow produced on the test run
└── assets/          screenshots
```

Each sample is also published alone as a zip, on the **Releases** page, one release per version.

## Two pages, two uses

| You want to | Read | Sections, always in this order |
|---|---|---|
| decide whether it fits your case, reuse a part | `README.md` | Try it · Problem · Solution · Use it in your flow · How it works · Design choices · Performance · Limits · Files · Tested on |
| rebuild it on your PC | `SETUP.md` | One section per path, lightest first: Quick try · Full or reusable version · In your own flow · Troubleshooting |

## Try it: the lightest path first

Every sample offers its ways to try it in the same order, from the one that asks the least to the one that asks the most,
and says what each one asks you to create:

1. **Quick try**: one block pasted into `Main`. No subflow, no input or output variable. A few minutes to see it work.
2. **Full or reusable version**: the subflows, their input and output variables, the steps the paste cannot carry.
3. **In your own flow**: the reusable part called from the flow you are building.

Stop at the path you need. The counts in the table are read from the code, so "Nothing" really means nothing.

## Techniques

The index [Samples by technique](TECHNIQUES.md) lists the samples that show a given idea (a local function, an
error returned instead of thrown, Excel through COM...).

## Conventions in the code

**Variable names** say what a variable is before you open it:

```text
in_loc_txt_WorkbookPath
│  │   │   └── what it holds
│  │   └────── type: txt · num · bool · date · lst · tbl · row · file · fold · inst · ui · cred · obj
│  └────────── scope: glob = the whole flow · loc = one subflow
└───────────── direction: in = given by the caller · out = returned · none = working variable
```

**Regions** cut every subflow by role, always in the same colours:

| Colour | Role |
|---|---|
| Cyan `#57FFE1` | settings: the only values to change |
| Red `#F4B6B6` | guards: what is checked before the work |
| Green `#C6E0B4` | reading the input |
| Purple `#D9C3E9` | processing |
| Blue `#BDD7EE` | sub-steps, loops |
| Gold `#FFD966` | output |

**A local function** (a local subflow with inputs and outputs) opens with its contract, then initialises every output
before the first action that can fail, and reports a failure through a flag and a message instead of stopping the flow:

```text
# local subflow: Convert_Excel_To_Html
# inputs: in_loc_txt_WorkbookPath, in_loc_txt_SheetName, in_loc_txt_RangeAddress
# outputs: out_loc_txt_Html, out_loc_bool_Ok, out_loc_txt_Error, ...
```

## What a paste carries, and what it does not

A paste brings the actions, their settings, the variables they produce and the UI elements. It does **not** bring the
subflows other than `Main`, the input and output variables, or settings such as *Mark as sensitive*.
`SETUP.md` lists exactly what to create before the paste; the guides below show where to click.

- [Create a subflow](docs/create-a-subflow.md)
- [Create input and output variables](docs/create-variables.md)
- [Sensitive values](docs/sensitive-values.md)
- [Troubleshooting a paste](docs/troubleshooting.md)

## Disclaimer

These samples are published **for e-learning purposes**: to learn and practise Power Automate Desktop. They are not
production-ready solutions and are provided as is, without warranty (see the [MIT license](LICENSE)). Try them in a
test environment with their fictitious sample data, then review, adapt and test them against your own security,
data-protection and governance rules before any real use.

Microsoft, Power Automate, Power Automate Desktop and Copilot Studio are trademarks of Microsoft. These samples are
not affiliated with or endorsed by Microsoft.

Page views are counted with GoatCounter, without cookies.

## Versions

Each sample has its own version (`x.y.z`): a patch pastes the same way, a minor adds something optional, a major asks
you to create something again (a subflow, a variable, a file). The **Tested on** table of each overview gives the PAD
versions it ran on.
