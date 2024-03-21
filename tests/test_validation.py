import unittest
from uuid import uuid4

from file_validator import validate_file, validate_metadata


class TestValidation(unittest.TestCase):
    def test_atmospheric_timeseries_validation(self):
        file_path = r"tests\data\atmospheric-timeseries\mini.txt"
        definition_file_path = r"tests\data\atmospheric-timeseries\definition.json"
        metadata = {"location": "Point(12 13.0)", "elevation": 123, "timezone": "UTC", "file_id": str(uuid4())}
        
        validate_file(file_path, metadata, definition_file_path)

    def test_validate_deserialized_metadata(self):
        metadata_schema_file_path = r"tests\data\atmospheric-timeseries\metadata.json"
        file_id = str(uuid4())
        metadata = {"location": "Point(12 13.0)", "elevation": "123", "timezone": "UTC", "file_id": file_id}
        
        validated_metadata = validate_metadata(metadata, metadata_schema_file_path, handle_deserialized=True)
        expected_metadata = {'location': 'Point(12 13.0)', 'elevation': 123.0, 'timezone': 'UTC', 'file_id': file_id}
        self.assertDictEqual(expected_metadata, validated_metadata)

    def test_atmospheric_timeseries_validation_deserialized_metadata_unhandled(self):
        file_path = r"tests\data\atmospheric-timeseries\mini.txt"
        definition_file_path = r"tests\data\atmospheric-timeseries\definition.json"
        metadata = {"location": "Point(12 13.0)", "elevation": "123", "timezone": "UTC", "file_id": str(uuid4())}
        
        with self.assertRaisesRegex(Exception, "'123' is not of type 'number'"):
            validate_file(file_path, metadata, definition_file_path)

    def test_atmospheric_timeseries_validation_deserialized_metadata(self):
        file_path = r"tests\data\atmospheric-timeseries\mini.txt"
        definition_file_path = r"tests\data\atmospheric-timeseries\definition.json"
        metadata = {"location": "Point(12 13.0)", "elevation": "123", "timezone": "UTC", "file_id": str(uuid4())}
        
        validate_file(file_path, metadata, definition_file_path, handle_deserialized_metadata=True)

if __name__ == "__main__":
    unittest.run()
