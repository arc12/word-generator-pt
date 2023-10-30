# Word Generator Plaything
_This documents the configuration files which allow the Plaything to be customised and notes how they relate to various useage scenarios._

## Plaything Specification
The collection of configuration files is referred to a __specification__ for how the plaything should be realised. The starting point for the specification is a JSON file inside the plaything configuration folder. For the Attribute Issues Plaything, the folder path is Config/attribute-issues-pt. The __specification id__ is the file-name less the ".json" extension and this file is generically called the "specification core file".

The specification core file contains the following elements which are common to all playthings:
- enabled
- title
- summary
- lang
- detail = a container for plaything-specific specification
- menu, for which the valid values are "about" and "questionnaire"
- asset_map, for which the valid keys are "about" and "attributes"

### "detail"
The structure of the "detail" container comprises:
- instruction [simple text]: A brief guide for the activity.
- capitalize [true|false]: Whether to capitalise the generated words. Defaults to false if omitted.
- models [a list of key-value structures]: A list of the models which users can select within the plaything.
  - The structures take the form: {"code": "", "label": ""}. The __code__ is used internally and for logging and should not be changed once the plaything specification is in use. The __label__ is presented to users and may be changed without affecting the analysis of logged data (as it uses the code). If only one model is given then the user gets no choice and so the label is never shown.

### "asset_map"
The "about" entry is optional but if present should name a Markdown file for use on the "about" page. The markdown file should contain entries for all of the __issue_categories__ given above. 

There must be one entry for each of the __code__ values __models__; each should map to a "pickle" file created by the "Word Generator" Jupyter Notebook.

## Possible Development Ideas
Add a text entry box (optional) to solicit user comment (e.g. explain what they think the bias is) for logging.