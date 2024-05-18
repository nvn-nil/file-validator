import unittest
from uuid import uuid4

from file_validator import validate_file, validate_metadata
from file_validator.utilities import get_json


class TestValidation(unittest.TestCase):
    def test_atmospheric_timeseries_validation(self):
        file_path = r"tests\data\atmospheric-timeseries\mini.txt"
        definition_file_path = r"tests\data\atmospheric-timeseries\definition.json"
        metadata = {
            "location": "Point(12 13.0)",
            "elevation": 123,
            "timezone": "UTC",
            "file_id": str(uuid4()),
        }

        validate_file(file_path, metadata, definition_file_path)

        metadata = {
            "location": "POINT(12 13.0)",
            "elevation": 123,
            "timezone": "UTC",
            "file_id": str(uuid4()),
        }
        validate_file(file_path, metadata, definition_file_path)

    def test_validate_deserialized_metadata(self):
        metadata_schema_file_path = r"tests\data\atmospheric-timeseries\metadata.json"
        file_id = str(uuid4())
        metadata = {
            "location": "Point(12 13.0)",
            "elevation": "123",
            "timezone": "UTC",
            "file_id": file_id,
        }

        validated_metadata = validate_metadata(metadata, metadata_schema_file_path, handle_deserialized=True)
        expected_metadata = {
            "location": "Point(12 13.0)",
            "elevation": 123.0,
            "timezone": "UTC",
            "file_id": file_id,
        }
        self.assertDictEqual(expected_metadata, validated_metadata)

    def test_atmospheric_timeseries_validation_deserialized_metadata_unhandled(self):
        file_path = r"tests\data\atmospheric-timeseries\mini.txt"
        definition_file_path = r"tests\data\atmospheric-timeseries\definition.json"
        metadata = {
            "location": "Point(12 13.0)",
            "elevation": "123",
            "timezone": "UTC",
            "file_id": str(uuid4()),
        }

        with self.assertRaisesRegex(Exception, "'123' is not of type 'number'"):
            validate_file(file_path, metadata, definition_file_path)

    def test_atmospheric_timeseries_validation_deserialized_metadata(self):
        file_path = r"tests\data\atmospheric-timeseries\mini.txt"
        definition_file_path = r"tests\data\atmospheric-timeseries\definition.json"
        metadata = {
            "location": "Point(12 13)",
            "elevation": "123",
            "timezone": "UTC",
            "file_id": str(uuid4()),
        }

        validate_file(file_path, metadata, definition_file_path, handle_deserialized_metadata=True)

    def test_validate_file_from_schema_data(self):
        file_path = r"tests\data\atmospheric-timeseries\mini.txt"
        file_id = str(uuid4())
        metadata = {
            "location": "Point(12 13)",
            "elevation": 123.0,
            "timezone": "UTC",
            "file_id": file_id,
        }

        definition = get_json(r"tests\data\atmospheric-timeseries\definition.json")
        metadata_schema = get_json(r"tests\data\atmospheric-timeseries\metadata.json")
        filename_schema = get_json(r"tests\data\atmospheric-timeseries\filename.json")
        header_schema = get_json(r"tests\data\atmospheric-timeseries\header.json")
        validated_path, validated_metadata = validate_file(
            file_path,
            metadata,
            definition=definition,
            metadata_schema=metadata_schema,
            header_schema=header_schema,
            filename_schema=filename_schema,
            handle_deserialized_metadata=True,
        )

        self.assertDictEqual(validated_metadata, metadata)
        self.assertEqual(file_path, validated_path)

        metadata_with_str_numbers = {
            "location": "Point(12 13)",
            "elevation": "123",
            "timezone": "UTC",
            "file_id": file_id,
        }
        validated_path, validated_metadata = validate_file(
            file_path,
            metadata_with_str_numbers,
            definition=definition,
            metadata_schema=metadata_schema,
            header_schema=header_schema,
            filename_schema=filename_schema,
            handle_deserialized_metadata=True,
        )
        self.assertDictEqual(validated_metadata, metadata)
        self.assertEqual(file_path, validated_path)

    def test_additional_field(self):
        metadata = {
            "location": "Point(1 2)",
            "elevation": "2",
            "timezone": "UTC",
            "file_id": "some",
            "notification_endpoint": "asdkjhaskdlj",
        }
        schema = r"tests\data\atmospheric-timeseries\metadata.json"
        validated = validate_metadata(metadata, schema, handle_deserialized=True)

        self.assertEqual(validated["notification_endpoint"], metadata["notification_endpoint"])


if __name__ == "__main__":
    unittest.run()
