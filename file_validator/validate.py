import os
import re
import sys
import json
import traceback

from jsonschema import validate as validate_jsonschema


ROOT_PATH = os.path.dirname(os.path.dirname(__file__))
DEFINITION_SCHEMA_PATH = os.path.join(ROOT_PATH, "file_validator", "schema", "definition_schema.json")


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


def validate_file(filepath, metadata, definition_file, handle_deserialized_metadata=False):
    """
    >>> file_path = r"atmospheric-timeseries\wind_time_series_mini.txt"
    >>> definition_file_path = r"atmospheric-timeseries\definition.json"
    >>> metadata = {"location": "Point(12 13.0)", "elevation": 123, "timezone": "UTC", "file_id": str(uuid4())}
    >>> validate_file(file_path, metadata, definition_file_path)
    """
    definition_path = os.path.abspath(definition_file)
    definition_dir = os.path.dirname(definition_path)

    with open(definition_path, "r") as fi:
        definition_data = json.load(fi)

    validate_from_schema_file(definition_data, DEFINITION_SCHEMA_PATH)

    metadata_schema_file = get_absolute_path_from_relative_path(definition_data["document"]["metadataSchema"], definition_dir)
    filename_schema_file = get_absolute_path_from_relative_path(definition_data["document"]["filenameSchema"], definition_dir)
    header_schema_file = get_absolute_path_from_relative_path(definition_data["content"]["headerSchema"], definition_dir)

    validated_metadata = validate_metadata(metadata, metadata_schema_file, handle_deserialized=handle_deserialized_metadata)
    validate_from_schema_file(os.path.basename(filepath), filename_schema_file)
    validate_header(filepath, definition_data["document"].get("encoding", "utf-8"), header_schema_file)

    return filepath, validated_metadata


def validate_metadata(metadata, metadata_schema_file, handle_deserialized=False):
    try:
        validate_from_schema_file(metadata, metadata_schema_file)
    except Exception:
        if not handle_deserialized:
            raise
    else:
        return metadata

    with open(metadata_schema_file, "r") as fi:
        schema = json.load(fi)
    numeric_schema_fields = get_numeric_fields_in_schema(schema)
    numeric_casted_metadata = { key: float(value) if numeric_schema_fields[key] else value for key, value in metadata.items() }
    validate_from_schema_file(numeric_casted_metadata, metadata_schema_file)

    return numeric_casted_metadata



def validate_from_schema_file(data, schema_file):
    with open(schema_file, "r") as fi:
        schema = json.load(fi)
    
    validate_jsonschema(data, schema=schema)


def validate_header(filepath, encoding, header_schema_file):
    with open(header_schema_file, "r") as fi:
        schema = json.load(fi)

    if schema["minItems"] != schema["maxItems"] or "prefixItems" not in schema:
        raise Exception("Header schema should define an array with minItems = maxItems and prefixItems for each line, for now.")
    
    num_header_lines = schema["minItems"]
    headers = []
    with open(filepath, "r", encoding=encoding) as fi:
        for i, line in enumerate(fi):
            if i >= num_header_lines:
                break

            headers.append(line)
    
    results = []
    for header, item_def in zip(headers, schema["prefixItems"]):
        pattern = item_def["pattern"]
        match = re.match(pattern, header)

        results.append(bool(match))

    if not all(results):
        invalid_headers = { headers[i]: schema["prefixItems"][i]["pattern"] for i, result in enumerate(results) if result is False }
        raise Exception(f"Header validation failed. Header validation status: {invalid_headers}")
