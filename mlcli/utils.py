import logging
import time
from collections.abc import Callable
from datetime import datetime, timedelta
from typing import Any

import orjson
import pandas as pd
from pydantic import ValidationError

from . import models


def validate_data(data: list[dict[str, Any]]) -> list[dict[str, Any]]:
    valid_data = []
    for item in data:
        try:
            valid_item = models.Lead(**item)
            valid_data.append(valid_item.model_dump())
        except ValidationError as e:
            print(f"Error: {e.errors()}")
            print(e)

    return valid_data


def data_to_file(file_name: str, data: list[dict[str, Any]]) -> None:
    valid_data = validate_data(data)
    with open(file_name, "wb") as f:
        json_str = orjson.dumps(valid_data, option=orjson.OPT_INDENT_2)
        f.write(json_str)
        logging.info(f"Data saved to file {file_name}")


def data_from_file(file_name: str) -> list[dict[str, Any]]:
    with open(file_name, "rb") as f:
        json_bytes = f.read()
        logging.info(f"Data read from file {file_name}")
    # Deserialize using orjson
    data_from_json = orjson.loads(json_bytes)
    return validate_data(data_from_json)


def get_dataframe(data: list[dict[str, Any]]) -> pd.DataFrame:
    validated_data = validate_data(data)
    return pd.json_normalize(validated_data)


def one_year_ago_day() -> str:
    return str((datetime.now() - timedelta(days=365)).date())


def generate_caption(df: pd.DataFrame) -> str:
    start_date = df["created_at.date"].min().date()
    end_date = df["created_at.date"].max().date()
    num_of_leads = len(df)
    return f"Data gathered between {start_date} and {end_date} from {num_of_leads} leads"


def benchmark(func: Callable[..., Any]) -> Callable[..., Any]:
    def wrapper(*args: Any, **kwargs: Any) -> Any:
        start_time = time.perf_counter()
        value = func(*args, **kwargs)
        end_time = time.perf_counter()
        print(
            f"The execution of {func.__name__} took {end_time - start_time:.5f} seconds",
        )
        return value

    return wrapper
