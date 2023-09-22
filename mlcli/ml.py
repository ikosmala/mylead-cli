import asyncio
import logging
from math import ceil
from typing import Any

import httpx
from tenacity import retry, retry_if_exception, stop_after_attempt, wait_fixed

from mlcli import models


class StatusError(Exception):
    """Raised when status from MyLead API is different than "success"."""


BASE_URL = "https://mylead.global/api/external/v1/statistic/conversions"
RATE_LIMIT = 19  # rate limit is 20 per one minute for this API endpoint
SLEEP_TIME = 61  # seconds
RETRY_ATTEMPTS = 7


# Define a function to check if the status code is 429 (Too Many Requests).
def retry_if_status_code_is_429(exception: BaseException) -> bool:
    """
    Check if the exception is an HTTP status error with status code 429.

    Args:
        exception (BaseException): The exception to check.

    Returns:
        bool: True if the exception is an HTTP status error with status code 429, False otherwise.
    """

    return isinstance(exception, httpx.HTTPStatusError) and exception.response.status_code == 429


# Define a function to handle HTTP status errors and log messages.
def handle_http_status_error(e: httpx.HTTPStatusError, page: int) -> None:
    """
    Handle HTTP status errors.

    Args:
        e (httpx.HTTPStatusError): The HTTP status error.
        page (int): The page number where the error occurred.

    Returns:
        None

    Raises:
        httpx.HTTPStatusError: Re-raises the original HTTP status error.
    """
    if e.response.status_code in [401, 403]:
        info = e.response.json()
        logging.error(f"Reason: {info['errors']['authorization'][0]}")
    elif e.response.status_code == 422:
        info = e.response.json()
        logging.error(f"Wrong parameters of API call.  {info['errors']}")
    elif e.response.status_code == 429:
        info = e.response.json()
        logging.error(
            "Too many API calls in a short amount of time. "
            f"Will try to retry page n.{page} for {RETRY_ATTEMPTS} times in total.",
        )
    else:
        logging.error(f"An unexpected HTTP error occurred: {e}")
    raise


# Define a function to fetch a single page of data from the API.
@retry(
    retry=retry_if_exception(retry_if_status_code_is_429),
    stop=stop_after_attempt(RETRY_ATTEMPTS),
    wait=wait_fixed(SLEEP_TIME),
)
async def fetch_single_page(
    client: httpx.AsyncClient,
    api_data: models.Api,
    page: int,
) -> dict[str, Any]:
    """
    Fetches a single page of data from the API.

    Args:
        client (httpx.AsyncClient): The HTTP async client used for making requests.
        api_data (models.Api): The API request data.
        page (int): The page number to fetch.

    Returns:
        dict[str, Any]: The JSON response data.

    Raises:
        httpx.HTTPStatusError: Raised when an HTTP status error occurs.
        StatusError: Raised when the response status is not "success".
    """

    params = api_data.model_dump(exclude_none=True)
    params["page"] = page
    try:
        response = await client.get(
            BASE_URL,
            headers={"Accept": "application/json"},
            params=params,
        )
        response.raise_for_status()
    except httpx.HTTPStatusError as e:
        handle_http_status_error(e, page)
        raise
    json_data = response.json()
    if json_data["status"] != "success":
        msg = f"Response: {json_data}"
        raise StatusError(msg)
    return json_data


async def fetch_all_pages_ml(api_data: models.Api) -> list[dict[str, Any]]:
    """
    Fetches all pages of data from the ML API.

    Args:
        api_data (models.Api): The API request data.

    Returns:
        list[dict[str, Any]]: The list of all data retrieved from the API."""
    all_data = []

    async with httpx.AsyncClient(http2=True) as client:
        # Fetch the first page to get total_pages
        initial_data = await fetch_single_page(client, api_data, 1)
        total_count = initial_data["pagination"]["total_count"]
        all_data.extend(initial_data["data"][0]["conversions"])
        total_pages = ceil(total_count / api_data.limit)

        tasks = [fetch_single_page(client, api_data, page) for page in range(2, total_pages + 1)]
        # rate limited batches
        for i in range(0, len(tasks), RATE_LIMIT):
            batch = tasks[i : i + RATE_LIMIT]
            responses = await asyncio.gather(*batch)

            for response in filter(None, responses):
                all_data.extend(response["data"][0]["conversions"])

            # Sleep only if there are more batches to process
            if (i + RATE_LIMIT) < len(tasks):
                await asyncio.sleep(SLEEP_TIME)

    return all_data
