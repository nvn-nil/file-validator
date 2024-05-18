import os
import re
from jsonschema import validate as validate_jsonschema

from file_validator.utilities import get_absolute_path_from_relative_path, get_json, get_numeric_fields_in_schema


ROOT_PATH = os.path.dirname(os.path.dirname(__file__))
DEFINITION_SCHEMA_PATH = os.path.join(ROOT_PATH, "file_validator", "schema", "definition_schema.json")


def validate_file(
    filepath,
    metadata,
    definition,
    metadata_schema=None,
    filename_schema=None,
    header_schema=None,
    handle_deserialized_metadata=False,
):
    r"""
    >>> file_path = r"atmospheric-timeseries\wind_time_series_mini.txt"
    >>> definition_file_path = r"atmospheric-timeseries\definition.json"
    >>> metadata = {"location": "Point(12 13.0)", "elevation": 123, "timezone": "UTC", "file_id": str(uuid4())}
    >>> validate_file(file_path, metadata, definition_file_path)
    """
    definition_data = get_json(definition)
    definition_schema = get_json(DEFINITION_SCHEMA_PATH)
    validate_jsonschema(definition_data, schema=definition_schema)

    if isinstance(definition, str) and os.path.isfile(definition):
        if not (
            os.path.isabs(definition_data["document"]["metadataSchema"])
            and os.path.isabs(definition_data["document"]["filenameSchema"])
            and os.path.isabs(definition_data["document"]["headerSchema"])
        ):
            definition_path = os.path.abspath(definition)
            definition_dir = os.path.dirname(definition_path)

            metadata_schema_path = get_absolute_path_from_relative_path(
                definition_data["document"]["metadataSchema"], definition_dir
            )
            filename_schema_path = get_absolute_path_from_relative_path(
                definition_data["document"]["filenameSchema"], definition_dir
            )
            header_schema_path = get_absolute_path_from_relative_path(
                definition_data["content"]["headerSchema"], definition_dir
            )
        else:
            metadata_schema_path = definition_data["document"]["metadataSchema"]
            filename_schema_path = definition_data["document"]["filenameSchema"]
            header_schema_path = definition_data["content"]["headerSchema"]

        metadata_schema = get_json(metadata_schema_path)
        filename_schema = get_json(filename_schema_path)
        header_schema = get_json(header_schema_path)

    if not (
        isinstance(definition, dict)
        and isinstance(metadata_schema, dict)
        and isinstance(filename_schema, dict)
        and isinstance(header_schema, dict)
    ):
        raise Exception("definition, metadata_schema, filename_schema, header_schema is required")

    validated_metadata = validate_metadata(metadata, metadata_schema, handle_deserialized=handle_deserialized_metadata)
    validate_jsonschema(os.path.basename(filepath), schema=filename_schema)
    validate_header(filepath, definition_data["document"].get("encoding", "utf-8"), header_schema)

    return filepath, validated_metadata


def validate_metadata(metadata, metadata_schema, handle_deserialized=False):
    schema = get_json(metadata_schema)
    try:
        validate_jsonschema(metadata, schema=schema)
    except Exception:
        if not handle_deserialized:
            raise
    else:
        return metadata

    numeric_schema_fields = get_numeric_fields_in_schema(schema)
    numeric_casted_metadata = {
        key: float(value) if key in numeric_schema_fields and numeric_schema_fields[key] else value
        for key, value in metadata.items()
    }
    validate_jsonschema(numeric_casted_metadata, schema=schema)

    return numeric_casted_metadata


def validate_header(filepath, encoding, schema):
    if schema["minItems"] != schema["maxItems"] or "prefixItems" not in schema:
        raise Exception(
            "Header schema should define an array with minItems = maxItems and prefixItems for each line, for now."
        )

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
        invalid_headers = {
            headers[i]: schema["prefixItems"][i]["pattern"] for i, result in enumerate(results) if result is False
        }
        raise Exception(f"Header validation failed. Header validation status: {invalid_headers}")
