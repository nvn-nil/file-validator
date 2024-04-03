import os
import json


def get_numeric_fields_in_schema(schema):
    if schema["type"] == "number":
        return True

    fields = {}
    if schema["type"] == "object":
        for field in schema["properties"]:
            fields[field] = get_numeric_fields_in_schema(schema["properties"][field])

        return fields

    return False


def get_absolute_path_from_relative_path(filepath, base_dir):
    if not os.path.isabs(filepath):
        return os.path.join(base_dir, filepath)

    return filepath


def get_json(file_or_dict):
    if isinstance(file_or_dict, str):
        with open(file_or_dict, "r") as fi:
            return json.load(fi)
    if isinstance(file_or_dict, dict):
        return file_or_dict

    raise TypeError("Schema is not of supported type. str(path) and dict(schema data)")
