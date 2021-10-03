import json
from os.path import join
from os import getcwd
from jsonschema import validate
import time

class Validator():

    @staticmethod
    def assert_valid_schema(data, schema_file):
        """ Checks whether the given data matches the schema """
        relative_path = join(getcwd(), "utilities", "json_schemas", schema_file)
        with open(relative_path) as schema_file:
            return validate(data, json.loads(schema_file.read()))

    @staticmethod
    def isDatetimeFormat(string_time_format, microseconds= True):
        try:
            datetime_format = '%Y-%m-%dT%H:%M:%S.%f%z'
            if not microseconds:
                datetime_format = '%Y-%m-%dT%H:%M:%S%z'
            time.strptime(string_time_format, datetime_format)
            return True
        except ValueError:
            print("Got time format to check: {0}".format(string_time_format))
            return False

    @staticmethod
    def isDateFormat(string_date_format):
        try:
            time.strptime(string_date_format, '%Y-%m-%d')
            return True
        except ValueError:
            print("Got date format to check: {0}".format(string_date_format))
            return False