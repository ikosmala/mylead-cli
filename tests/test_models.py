from datetime import date, datetime, timedelta

from mlcli.models import Api


def test_strip_date_to():
    test_date = datetime.now() + timedelta(days=1)
    print(test_date)
    api = Api(token="test_token", date_to=test_date)

    assert isinstance(api.date_to, date)


def test_strip_date_from():
    test_date = datetime.now() + timedelta(days=-1)
    print(test_date)
    api = Api(token="test_token", date_from=test_date)

    assert isinstance(api.date_to, date)
