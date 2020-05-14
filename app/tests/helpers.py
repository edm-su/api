import json
from os.path import join, dirname

from jsonschema import validate

from app.auth import create_access_token


def assert_valid_schema(data, schema_file):
    """ Checks whether the given data matches the schema """

    schema = _load_json_schema(schema_file)
    return validate(data, schema)


def _load_json_schema(filename):
    """ Loads the given schema file """

    relative_path = join('schemas', filename)
    absolute_path = join(dirname(__file__), relative_path)

    with open(absolute_path) as schema_file:
        return json.loads(schema_file.read())


def create_auth_header(username):
    token = create_access_token(data={'sub': username}).decode('utf-8')
    return {'Authorization': f'Bearer {token}'}
