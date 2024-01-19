from datetime import datetime, timedelta
from unittest.mock import patch
from pydantic import ValidationError
from myleadcli import utils
import pytest
from pytest_mock import MockerFixture
import pandas as pd
from pandas.api.types import CategoricalDtype
import logging

logging.basicConfig(level=logging.INFO)


@pytest.fixture(autouse=True)
def setup_logging(caplog):
    caplog.set_level(logging.INFO)


@pytest.fixture()
def tmp_file_with_data(tmp_path, data_for_validation):
    file_path = tmp_path / "test_file.json"
    utils.data_to_file(file_path, data_for_validation)
    return file_path


def test_one_year_ago_day():
    with patch("myleadcli.utils.datetime") as mock_date:
        mock_date.now.return_value = datetime(2023, 9, 17)
        mock_date.timedelta = timedelta

        result = utils.one_year_ago_day()

        assert result == "2022-09-17"


def test_validate_data(data_for_validation):
    validated_data = utils.validate_data(data_for_validation)
    assert len(validated_data) == len(data_for_validation)


def test_validate_data_failed(invalid_data_for_validation):
    with pytest.raises(ValidationError):
        utils.validate_data(invalid_data_for_validation)


def test_data_to_file(data_for_validation, mocker: MockerFixture):
    filename = "test_file"
    mock_file = mocker.mock_open()
    mocker.patch("builtins.open", mock_file)

    utils.data_to_file(filename, data_for_validation)

    mock_file.assert_called_once_with(filename, "wb")


def test_data_from_file(tmp_file_with_data, data_for_validation):
    data = utils.data_from_file(tmp_file_with_data)
    assert len(data) == len(data_for_validation)


def test_get_dataframe(data_for_validation):
    df = utils.get_dataframe(data_for_validation)
    assert isinstance(df, pd.DataFrame)
    assert df["campaign_id"].dtype == "int64"
    assert df["payout"].dtype == "float64"


def test_get_dataframe_failed(invalid_data_for_validation):
    with pytest.raises(ValidationError):
        utils.get_dataframe(invalid_data_for_validation)


def test_generate_caption(dataframe_data):
    caption = utils.generate_caption(dataframe_data)
    num_of_leads = len(dataframe_data)
    assert f"{num_of_leads} leads" in caption


def test_convert_to_categorical(dataframe_data):
    columns_to_categorical = ["campaign_id", "campaign_name", "currency"]
    categorical = utils.convert_to_categorical(columns_to_categorical, dataframe_data)
    assert isinstance(categorical, pd.DataFrame)

    for column in columns_to_categorical:
        assert isinstance(categorical[column].dtype, CategoricalDtype)


def test_benchmark_decorator(caplog):
    @utils.benchmark
    def sample_function():
        x = 1

    sample_function()
    log_records = caplog.records
    assert len(log_records) == 1
    assert "The execution of sample_function took" in log_records[0].message
