from datetime import datetime, timedelta
from unittest.mock import patch
from pydantic import ValidationError
from mlcli import utils
import pytest


def test_one_year_ago_day():
    with patch("mlcli.utils.datetime") as mock_date:
        mock_date.now.return_value = datetime(2023, 9, 17)
        mock_date.timedelta = timedelta

        result = utils.one_year_ago_day()

        assert result == "2022-09-17"


def test_validate_data(data_for_validation):
    validated_data = utils.validate_data(data_for_validation)
    assert len(validated_data) == len(data_for_validation)


def test_validate_data_failed(invalid_data_for_validation):
    with pytest.raises(ValidationError) as excinfo:
        utils.validate_data(invalid_data_for_validation)
