import pytest
import json
import orjson


@pytest.fixture()
def success_response_json():
    with open("tests/test_files/test_success.json") as file:
        return json.load(file)


@pytest.fixture()
def data_for_validation():
    with open("tests/test_files/test_success.json") as file:
        response = json.load(file)
        return response["data"][0]["conversions"]


@pytest.fixture()
def invalid_data_for_validation():
    with open("tests/test_files/test_success.json") as file:
        response = json.load(file)
        response["data"][0]["conversions"][0].pop("id")
        return response["data"][0]["conversions"]
