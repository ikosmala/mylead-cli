import asyncio
import logging
from math import ceil
from typing import Any

import httpx
from tenacity import retry, retry_if_exception, stop_after_attempt, wait_fixed

from . import models


class StatusError(Exception):
    """Raised when status from MyLead API is different than "success" """

    pass


BASE_URL = "https://mylead.global/api/external/v1/statistic/conversions"
RATE_LIMIT = 19  # rate limit is 20 per one minute for this API endpoint
SLEEP_TIME = 61  # seconds
RETRY_ATTEMPTS = 7


def retry_if_status_code_is_429(exception: BaseException) -> bool:
    return (
        isinstance(exception, httpx.HTTPStatusError)
        and exception.response.status_code == 429
    )


@retry(
    retry=retry_if_exception(retry_if_status_code_is_429),
    stop=stop_after_attempt(RETRY_ATTEMPTS),
    wait=wait_fixed(SLEEP_TIME),
)
async def fetch_single_page(
    client: httpx.AsyncClient, api_data: models.Api, page: int
) -> dict[str, Any]:
    params = api_data.model_dump(exclude_none=True)
    params["page"] = page
    try:
        response = await client.get(
            BASE_URL, headers={"Accept": "application/json"}, params=params
        )
        response.raise_for_status()
    except httpx.HTTPStatusError as e:
        if e.response.status_code in [401, 403]:
            info = e.response.json()
            logging.error(f"Reason: {info['errors']['authorization'][0]}")
        elif e.response.status_code == 422:
            info = e.response.json()
            logging.error(f"Wrong parameters of API call.  {info['errors']}")
        elif e.response.status_code == 429:
            info = e.response.json()
            logging.error(
                "Too many API calls in short amount of time. "
                f"Will try to retry page n.{page} for {RETRY_ATTEMPTS} times in total."
            )
        else:
            logging.error(f"An unexpected HTTP error occured: {e}")
        raise
    json_data = response.json()
    if json_data["status"] != "success":
        raise StatusError(f"Response: {json_data}")
    return json_data


async def fetch_all_pages_ML(api_data: models.Api) -> list[dict[str, Any]]:
    all_data = []

    async with httpx.AsyncClient(http2=True) as client:
        # Fetch the first page to get total_pages
        initial_data = await fetch_single_page(client, api_data, 1)
        total_count = initial_data["pagination"]["total_count"]
        all_data.extend(initial_data["data"][0]["conversions"])
        total_pages = ceil(total_count / api_data.limit)

        tasks = [
            fetch_single_page(client, api_data, page)
            for page in range(2, total_pages + 1)
        ]
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