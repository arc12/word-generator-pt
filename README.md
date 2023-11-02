# Word Generator Plaything
_This documents the configuration files which allow the Plaything to be customised and notes how they relate to various useage scenarios._

Plaything name: word-generator

## Plaything Specification
Refer to the README in the pg_shared repository/folder for common elements; this README refers only to the elements which are specific to the Attribute Issues Plaything.
For the Word Generator Plaything, the Specifications folder is Config/word-generator.

Available views:
- "about" - available if there is an entry for "about" in the asset_map.
- "generate"

### "detail"
The structure of the "detail" container comprises:
- instruction [simple text]: A brief guide for the activity.
- capitalize [true|false]: Whether to capitalise the generated words. Defaults to false if omitted.
- models [a list of key-value structures]: A list of the models which users can select within the plaything.
  - The structures take the form: {"code": "", "label": ""}. The __code__ is used internally and for logging and should not be changed once the plaything specification is in use. The __label__ is presented to users and may be changed without affecting the analysis of logged data (as it uses the code). If only one model is given then the user gets no choice and so the label is never shown.

### "asset_map"
The "about" entry is optional but if present should name a Markdown file for use on the "about" page. For this plaything, the "about" information is expected to be an explanation of the algorithm and user interactions. 

There must also be one entry for each of the __code__ values __models__; each should map to a "pickle" file created by the "Word Generator" Jupyter Notebook.

## Possible Development Ideas
Add a text entry box (optional) to solicit user comment (e.g. explain what they think the bias is) for logging.