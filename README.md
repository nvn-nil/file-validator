# File Validator

Use a file definition file to validate a file completely.

Data coming into a system and out of a system can be trivially validated using jsonschema. However, we do not have a way to check and validate the files that are going in and out of the system. This library aims aims to bridge that gap by implementing a way to validate a file completely (including metadata attached to the file in cloud storages).

This helps:
    - establish robust contracts between cloud services.
    - validate the file before sinking it into a data processing pipeline.
