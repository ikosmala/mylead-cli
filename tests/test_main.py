from myleadcli import main
import pytest


def test_check_apikey():
    main.check_api_key("test")


def test_check_apikey_fail():
    with pytest.raises(SystemExit):
        main.check_api_key("")
