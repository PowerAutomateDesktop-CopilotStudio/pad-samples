[⬅ Start here](../START-HERE.md)

# Troubleshooting a paste

| You see | Why | Do this |
|---|---|---|
| Nothing appears after Ctrl+V | The clipboard holds only part of the block | Copy again with the copy button of the block, or **Copy raw file** on the file page |
| Errors about a variable that does not exist | An input or output variable is missing or misspelt | Compare with the sample's variables table, capitals included |
| Errors on a `CALL` line | A subflow is missing or misspelt | Compare the tab names with the sample's subflows table |
| A warning about a password field | A variable is not marked as sensitive | [Sensitive values](sensitive-values.md) |
| The run stops on a file or folder | The sample files are not where the flow looks | Redo the step "Prepare the files", or change the first region of `Main` |

Still stuck? Open an issue with the template **This sample does not work**: it asks for your PAD version and the error text.
