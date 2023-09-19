from datetime import datetime, timedelta
from unittest.mock import patch

from mlcli import utils


def test_one_year_ago_day():
    with patch("mlcli.utils.datetime") as mock_date:
        mock_date.now.return_value = datetime(2023, 9, 17)
        mock_date.timedelta = timedelta

        result = utils.one_year_ago_day()

        assert result == "2022-09-17"
