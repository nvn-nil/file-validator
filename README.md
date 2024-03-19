# File Validator

Use a json file definition to validate a file completely (filename, metadata, headers, [data]).

Data coming into a system and out of a system can be easily validated using jsonschema. However, we do not have a way to check and validate the files that are going in and out of the system. This library aims aims to bridge that gap by implementing a way to validate a file completely (including metadata attached to the file in cloud storages).

> **_NOTE:_**  Metadata validation can be skipped for local files. metadataSchema can be a catch all jsonschema in that case.

This helps:
  - establish robust contracts between cloud services.
  - validate the file before sinking it into a data processing pipeline.

Definition file contains references to schema files for the different elements of a file.

```json
{
    "document": {
        "encoding": "utf-8",
        "metadataSchema": "metadata.json",
        "filenameSchema": "filename.json"
    },
    "content": {
        "headerSchema": "header.json"
    }
}
```
