import pytest
import pathlib
import httpx
from pytest_httpx import HTTPXMock
from mlcli.ml import fetch_single_page, models, StatusError
import json


@pytest.mark.asyncio
async def test_fetch_single_page_success(httpx_mock: HTTPXMock):
    with open("tests/test_files/test_success.json", "r") as file:
        mock_response = json.load(file)

    httpx_mock.add_response(json=mock_response)

    api_data = models.Api(token="test")

    async with httpx.AsyncClient(http2=True) as client:
        response = await fetch_single_page(client, api_data, 1)

    assert response == mock_response


@pytest.mark.asyncio
async def test_fetch_single_page_wrong_apikey(httpx_mock: HTTPXMock):
    with open("tests/test_files/test_wrong_api_key.json") as file:
        mock_response = json.load(file)

    httpx_mock.add_response(json=mock_response, status_code=401)

    api_data = models.Api(token="test")

    async with httpx.AsyncClient(http2=True) as client:
        with pytest.raises(httpx.HTTPStatusError) as excinfo:
            response = await fetch_single_page(client, api_data, 1)
    assert excinfo.value.response.status_code == 401
    assert excinfo.value.response.json()
