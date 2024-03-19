import unittest
from uuid import uuid4

from file_validator.validate import validate_file


class TestValidation(unittest.TestCase):
    def test_atmospheric_timeseries_validation(self):
        file_path = r"tests\data\atmospheric-timeseries\mini.txt"
        definition_file_path = r"tests\data\atmospheric-timeseries\definition.json"
        metadata = {"location": "Point(12 13.0)", "elevation": 123, "timezone": "UTC", "file_id": str(uuid4())}
        
        validate_file(file_path, metadata, definition_file_path)


if __name__ == "__main__":
    unittest.run()
