import pytest
import json
from mlcli import utils
import pandas as pd


@pytest.fixture()
def success_response_json() -> dict:
    """
    Fixture for returning a dictionary with correct API response.

    Returns:
        dict: A dictionary containing a valid API response.
    """
    with open("tests/test_files/test_success.json") as file:
        return json.load(file)


@pytest.fixture()
def data_for_validation() -> utils.DataList:
    """
    Fixture for returning a list of dictionaries for validation by pydantic.

    Returns:
        list[dict[str, Any]]: A list of dictionaries representing data for validation.
    """
    with open("tests/test_files/test_success.json") as file:
        response = json.load(file)
        return response["data"][0]["conversions"]


@pytest.fixture()
def invalid_data_for_validation() -> utils.DataList:
    """
    Fixture for providing invalid data for validation testing.

    This fixture loads data from a JSON file, manipulates it to create
    invalid data by removing the 'id' field from a conversion record,
    and returns a list of dictionaries representing the invalid data.

    Returns:
        List[Dict[str, Any]]: A list of dictionaries containing invalid data.
    """
    with open("tests/test_files/test_success.json") as file:
        response = json.load(file)
        response["data"][0]["conversions"][0].pop("id")
        return response["data"][0]["conversions"]


@pytest.fixture()
def validated_data(data_for_validation: utils.DataList) -> utils.DataList:
    return utils.validate_data(data_for_validation)


@pytest.fixture()
def dataframe_data(data_for_validation: utils.DataList) -> pd.DataFrame:
    return utils.get_dataframe(data_for_validation)
