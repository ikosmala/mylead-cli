import json
import logging
import httpx
import pytest
from pytest_httpx import HTTPXMock
from mlcli.ml import fetch_single_page, models
from tenacity import retry, stop_after_attempt, wait_none


@pytest.mark.asyncio()
async def test_fetch_single_page_success(httpx_mock: HTTPXMock):
    with open("tests/test_files/test_success.json") as file:
        mock_response = json.load(file)

    httpx_mock.add_response(json=mock_response)

    api_data = models.Api(token="test")

    async with httpx.AsyncClient(http2=True) as client:
        response = await fetch_single_page(client, api_data, 1)

    assert response == mock_response


@pytest.mark.asyncio()
async def test_fetch_single_page_failed_apikey(
    httpx_mock: HTTPXMock,
    caplog: pytest.LogCaptureFixture,
):
    caplog.at_level(logging.ERROR)
    with open("tests/test_files/test_failed_api_key.json") as file:
        mock_response = json.load(file)

    httpx_mock.add_response(json=mock_response, status_code=401)

    api_data = models.Api(token="test")

    async with httpx.AsyncClient(http2=True) as client:
        with pytest.raises(httpx.HTTPStatusError) as excinfo:
            await fetch_single_page(client, api_data, 1)
    assert excinfo.value.response.status_code == 401
    json_data = excinfo.value.response.json()
    assert json_data["status"] == "error"
    assert "The given token is invalid" in caplog.text


@pytest.mark.asyncio()
async def test_fetch_single_page_failed_parameters(
    httpx_mock: HTTPXMock,
    caplog: pytest.LogCaptureFixture,
):
    caplog.at_level(logging.ERROR)
    with open("tests/test_files/test_failed_field.json") as file:
        mock_response = json.load(file)

    httpx_mock.add_response(json=mock_response, status_code=422)

    api_data = models.Api(token="test")

    async with httpx.AsyncClient(http2=True) as client:
        with pytest.raises(httpx.HTTPStatusError) as excinfo:
            await fetch_single_page(client, api_data, 1)
    assert excinfo.value.response.status_code == 422
    json_data = excinfo.value.response.json()
    assert json_data["status"] == "error"
    assert "Wrong parameters of API call" in caplog.text


@pytest.mark.asyncio()
async def test_fetch_single_page_500(
    httpx_mock: HTTPXMock,
    caplog: pytest.LogCaptureFixture,
):
    caplog.at_level(logging.ERROR)

    httpx_mock.add_response(status_code=500)

    api_data = models.Api(token="test")

    async with httpx.AsyncClient(http2=True) as client:
        with pytest.raises(httpx.HTTPStatusError) as excinfo:
            await fetch_single_page(client, api_data, 1)
    assert excinfo.value.response.status_code == 500

    assert "An unexpected HTTP error occurred" in caplog.text


@pytest.mark.asyncio()
async def test_fetch_single_page_too_many_api_calls_failed(
    httpx_mock: HTTPXMock, caplog: pytest.LogCaptureFixture, monkeypatch: pytest.MonkeyPatch
):
    caplog.at_level(logging.ERROR)
    with open("tests/test_files/test_failed_rate_limit.json") as file:
        mock_response = json.load(file)
    httpx_mock.add_response(json=mock_response, status_code=429)

    monkeypatch.setattr(fetch_single_page.retry, "wait", wait_none())

    api_data = models.Api(token="test")

    async with httpx.AsyncClient(http2=True) as client:
        with pytest.raises(httpx.HTTPStatusError) as excinfo:
            await fetch_single_page(client, api_data, 1)
    assert excinfo.value.response.status_code == 429
