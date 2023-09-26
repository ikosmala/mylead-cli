import json
import logging
import httpx
import pytest
from pytest_httpx import HTTPXMock
from myleadcli.ml import (
    fetch_single_page,
    models,
    StatusError,
    fetch_all_pages_ml,
)
from tenacity import wait_none
import tenacity


@pytest.fixture(scope="module")
def api_data():
    """
    Fixture providing test data for the API.
    """
    return models.Api(token="test", limit=10)


@pytest.mark.asyncio()
async def test_fetch_single_page_success(httpx_mock: HTTPXMock, success_response_json, api_data):
    """
    Test for successful retrieval of a single page from the API.
    """
    httpx_mock.add_response(json=success_response_json)

    async with httpx.AsyncClient(http2=True) as client:
        response = await fetch_single_page(client, api_data, 1)

    assert response == success_response_json


@pytest.mark.asyncio()
async def test_fetch_single_page_failed_apikey(
    httpx_mock: HTTPXMock, caplog: pytest.LogCaptureFixture, api_data
):
    """
    Test for handling failed API key in a single page retrieval.
    """
    caplog.at_level(logging.ERROR)
    with open("tests/test_files/test_failed_api_key.json") as file:
        mock_response = json.load(file)

    httpx_mock.add_response(json=mock_response, status_code=401)

    async with httpx.AsyncClient(http2=True) as client:
        with pytest.raises(httpx.HTTPStatusError) as excinfo:
            await fetch_single_page(client, api_data, 1)
    assert excinfo.value.response.status_code == 401
    json_data = excinfo.value.response.json()
    assert json_data["status"] == "error"
    assert "The given token is invalid" in caplog.text


@pytest.mark.asyncio()
async def test_fetch_single_page_failed_parameters(
    httpx_mock: HTTPXMock, caplog: pytest.LogCaptureFixture, api_data
):
    """
    Test for handling failed parameters of API call in a single page retrieval.
    """
    caplog.at_level(logging.ERROR)
    with open("tests/test_files/test_failed_field.json") as file:
        mock_response = json.load(file)

    httpx_mock.add_response(json=mock_response, status_code=422)

    async with httpx.AsyncClient(http2=True) as client:
        with pytest.raises(httpx.HTTPStatusError) as excinfo:
            await fetch_single_page(client, api_data, 1)
    assert excinfo.value.response.status_code == 422
    json_data = excinfo.value.response.json()
    assert json_data["status"] == "error"
    assert "Wrong parameters of API call" in caplog.text


@pytest.mark.asyncio()
async def test_fetch_single_page_500(
    httpx_mock: HTTPXMock, caplog: pytest.LogCaptureFixture, api_data
):
    """
    Test for handling 500 server error in a single page retrieval.
    """
    caplog.at_level(logging.ERROR)

    httpx_mock.add_response(status_code=500)

    async with httpx.AsyncClient(http2=True) as client:
        with pytest.raises(httpx.HTTPStatusError) as excinfo:
            await fetch_single_page(client, api_data, 1)
    assert excinfo.value.response.status_code == 500

    assert "An unexpected HTTP error occurred" in caplog.text


@pytest.mark.asyncio()
async def test_fetch_single_page_too_many_api_calls_failed(
    httpx_mock: HTTPXMock,
    caplog: pytest.LogCaptureFixture,
    monkeypatch: pytest.MonkeyPatch,
    api_data,
):
    """
    Test for handling too many API calls in a short amount of time.

    This test simulates a scenario where the API rate limit is exceeded,
    resulting in a 429 status code. It ensures that the retry mechanism is
    correctly triggered and that the appropriate error messages are logged.
    """
    caplog.at_level(logging.ERROR)
    with open("tests/test_files/test_failed_rate_limit.json") as file:
        mock_response = json.load(file)
    httpx_mock.add_response(json=mock_response, status_code=429)

    monkeypatch.setattr(fetch_single_page.retry, "wait", wait_none())

    async with httpx.AsyncClient(http2=True) as client:
        with pytest.raises(tenacity.RetryError) as excinfo:
            await fetch_single_page(client, api_data, 1)

    assert "raised HTTPStatusError" in str(excinfo.value)
    assert "Too many API calls in a short amount of time" in caplog.text


@pytest.mark.asyncio()
async def test_fetch_single_page_failed_status_error(
    httpx_mock: HTTPXMock, caplog: pytest.LogCaptureFixture, api_data
):
    """
    Test for handling a failed API response with a 'status' field indicating an error.

    This test simulates a scenario where the API responds with a status code of 200,
    but the 'status' field in the JSON response indicates an error. It ensures that
    a `StatusError` is raised, and the error message is correctly logged.
    """
    caplog.at_level(logging.ERROR)
    with open("tests/test_files/test_failed_status_error.json") as file:
        mock_response = json.load(file)

    httpx_mock.add_response(json=mock_response, status_code=200)

    async with httpx.AsyncClient(http2=True) as client:
        with pytest.raises(StatusError) as excinfo:
            await fetch_single_page(client, api_data, 1)
    assert isinstance(excinfo.value, StatusError)
    assert "Response" in str(excinfo.value)


@pytest.mark.asyncio()
async def test_fetch_all_pages_ml_success(httpx_mock: HTTPXMock, success_response_json, api_data):
    """
    Test for successful retrieval of list of leads from API. Single page.
    """
    httpx_mock.add_response(json=success_response_json)

    async with httpx.AsyncClient(http2=True):
        all_data = await fetch_all_pages_ml(api_data)

    assert isinstance(all_data, list)
    assert len(all_data) == len(success_response_json["data"][0]["conversions"])
