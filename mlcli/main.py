import asyncio
import logging
import sys
from datetime import datetime
from time import perf_counter
from typing import Annotated, Any

import pandas as pd
import typer
from dotenv import load_dotenv
from rich import print
from rich.progress import Progress, SpinnerColumn, TextColumn

from mlcli import ml, models, utils
from mlcli.plotting import choose_graph
from mlcli.tables import choose_table

DATE_FORMATS = ["%Y-%m-%d", "%Y/%m/%d", "%d-%m-%Y", "%d/%m/%Y", "%Y.%m.%d", "%d.%m.%Y"]

logging.basicConfig(
    level=logging.ERROR,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)

app = typer.Typer()
load_dotenv()


def check_api_key(apikey: str) -> None:
    """
    Check if the API key is provided.

    Args:
        apikey (str): The API key to be checked.

    Returns:
        None

    Raises:
        SystemExit: Raised when the API key is missing.
    """
    if not apikey:
        print(
            "Missing API Key: Ensure you supply an API Key "
            "either via a console argument or an environment variable",
        )
        sys.exit()


@utils.benchmark
def process_data(data: list[dict[str, Any]]) -> pd.DataFrame:
    """
    Process the fetched data into a DataFrame.

    Args:
        data (list[dict[str, Any]]): The fetched data to be processed.

    Returns:
        pd.DataFrame: The processed DataFrame.

    Raises:
        SystemExit: Raised when there is no data to process.

    """
    if not data:
        print("No leads to process. Exiting program")
        sys.exit()
    df = utils.get_dataframe(data)
    df["hour_of_day"] = df["created_at.date"].dt.hour.astype(int)
    df["day_of_week"] = df["created_at.date"].dt.day_name()
    return df


def fetch_data(
    progress: Progress,
    apikey: str,
    date_from: datetime,
    date_to: datetime,
    from_file: bool,
    save_file: bool,
) -> list[dict[str, Any]]:
    """
    Fetch data from MyLead API or a file.

    Args:
        progress (Progress): The progress object for displaying progress information.
        apikey (str): The API key for accessing the MyLead API.
        date_from (datetime): The start date for fetching data.
        date_to (datetime): The end date for fetching data.
        from_file (bool): Flag indicating whether to fetch data from a file.
        save_file (bool): Flag indicating whether to save fetched data to a file.

    Returns:
        list[dict[str, Any]]: The fetched data as a list of dictionaries.

    Examples:
        ```python
        progress = Progress()
        apikey = "API_KEY"
        date_from = datetime(2022, 1, 1)
        date_to = datetime(2022, 1, 31)
        from_file = False
        save_file = False

        result = fetch_data(progress, apikey, date_from, date_to, from_file, save_file)
        print(result)
        ```"""
    start_time = perf_counter()
    if not from_file:
        progress.add_task(description="Fetching data from MyLead API...", total=None)
        api = models.Api(token=apikey, date_from=date_from, date_to=date_to, limit=500)
        all_data = asyncio.run(ml.fetch_all_pages_ml(api_data=api))
        if save_file:
            utils.data_to_file("mlcli_leads_data.json", all_data)
    else:
        # TODO: fetch from specified file
        progress.add_task(description="Fetching data from file...", total=None)
        all_data = utils.data_from_file("mlcli_leads_data.json")
    end_time = perf_counter()
    print(f"Fetched {len(all_data)} leads in {end_time-start_time:.2f} seconds.")
    return all_data


@app.command()
def stats(
    date_from: Annotated[
        datetime,
        typer.Option(
            "--date-from",
            "-df",
            help="Start date for gathering data. Default: 365 days ago.",
            formats=DATE_FORMATS,
            default_factory=utils.one_year_ago_day,
        ),
    ],
    apikey: Annotated[
        str,
        typer.Argument(
            envvar="API_KEY",
            help="Your api key from https://mylead.global/panel/api",
        ),
    ] = "",
    date_to: Annotated[
        datetime,
        typer.Option(
            "--date-to",
            "-dt",
            help="End date for gathering data. Default: today",
            formats=DATE_FORMATS,
        ),
    ] = datetime.now(),
    save_file: Annotated[bool, typer.Option(help="Save leads to file")] = False,
    from_file: Annotated[bool, typer.Option(help="Load leads from file")] = False,
    charts: Annotated[bool, typer.Option(help="Show charts instead of tables")] = False,
) -> None:
    """
    Shows statistics for data retrieved from the MyLead API.

    You can specify date ranges using the --date-from and --date-to options.
    An API key (API_KEY) is REQUIRED and can be provided via an environment variable or command.

    When the --chart option is used, data is visualized through charts instead of tables.

    If the --save-file option is used, fetched data is saved as a JSON file.
    Alternatively, you can use --from-file to load data from a previously saved file.

    Due to API rate limiting the maximum fetching speed is 10,000 leads per 60 seconds.

    Args:
        date_from (datetime): Start date for gathering data. Default: 365 days ago.
        date_to (datetime): End date for gathering data. Default: today.
        apikey (str): Your API key from https://mylead.global/panel/api.
        save_file (bool): Save leads to file.
        from_file (bool): Load leads from file.
        charts (bool): Show charts instead of tables.

    Returns:
        None
    """
    check_api_key(apikey)
    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        transient=True,
    ) as progress:
        all_data = fetch_data(
            progress,
            apikey,
            date_from,
            date_to,
            from_file,
            save_file,
        )
        df = process_data(all_data)
    if charts:
        choose_graph(df)
    else:
        choose_table(df)


if __name__ == "__main__":
    app()
