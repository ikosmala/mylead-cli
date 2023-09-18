import asyncio
import logging
import sys
from datetime import datetime
from typing import Annotated, Any
from time import perf_counter
import pandas as pd
import typer
from dotenv import load_dotenv
from rich import print
from rich.progress import Progress, SpinnerColumn, TextColumn

from . import ml
from . import models
from . import ploting
from . import utils
from .tables import choose_table

DATEFORMATS = ["%Y-%m-%d", "%Y/%m/%d", "%d-%m-%Y", "%d/%m/%Y", "%Y.%m.%d", "%d.%m.%Y"]

logging.basicConfig(level=logging.ERROR)

app = typer.Typer()
load_dotenv()


def check_api_key(apikey: str):
    if not apikey:
        print(
            "Missing API Key: Ensure you supply an API Key "
            "either via a console argument or an environment variable"
        )
        sys.exit()


def process_data(data: list[dict[str, Any]]) -> pd.DataFrame:
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
    start_time = perf_counter()
    if not from_file:
        progress.add_task(description="Fetching data from MyLead API...", total=None)
        api = models.Api(token=apikey, date_from=date_from, date_to=date_to, limit=500)
        all_data = asyncio.run(ml.fetch_all_pages_ML(api_data=api))
        if save_file:
            utils.data_to_file("myfile.json", all_data)
    else:
        # todo fetch from specified file
        progress.add_task(description="Fetching data from file...", total=None)
        all_data = utils.data_from_file("myfile.json")
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
            formats=DATEFORMATS,
            default_factory=utils.one_year_ago_day,
        ),
    ],
    apikey: Annotated[
        str,
        typer.Argument(
            envvar="API_KEY", help="Your api key from https://mylead.global/panel/api"
        ),
    ] = "",
    date_to: Annotated[
        datetime,
        typer.Option(
            "--date-to",
            "-dt",
            help="End date for gathering data. Default: today",
            formats=DATEFORMATS,
        ),
    ] = datetime.now(),
    save_file: Annotated[bool, typer.Option(help="Save leads to file")] = False,
    from_file: Annotated[bool, typer.Option(help="Load leads from file")] = False,
):
    """
    Shows data statistics from fetched leads from MyLead API.

    You can specify date ranges by --date-from and --date-to.
    API_KEY is REQUIRED. Can be specified in .env file or provided via command.

    If --save-file is used then fetched data is saved to JSON file.
    If --from-file is used then data is fetched from saved file rather than API.
    """
    check_api_key(apikey)
    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        transient=True,
    ) as progress:
        all_data = fetch_data(
            progress, apikey, date_from, date_to, from_file, save_file
        )
        df = process_data(all_data)

    choose_table(df)


@app.command()
def charts(
    date_from: Annotated[
        datetime,
        typer.Option(
            "--date-from",
            "-df",
            help="Start date for gathering data. Default: 365 days ago.",
            formats=DATEFORMATS,
            default_factory=utils.one_year_ago_day,
        ),
    ],
    apikey: Annotated[
        str,
        typer.Argument(
            envvar="API_KEY", help="Your api key from https://mylead.global/panel/api"
        ),
    ] = "",
    date_to: Annotated[
        datetime,
        typer.Option(
            "--date-to",
            "-dt",
            help="End date for gathering data. Default: today",
            formats=DATEFORMATS,
        ),
    ] = datetime.now(),
    save_file: Annotated[bool, typer.Option(help="Save leads to file")] = False,
    from_file: Annotated[bool, typer.Option(help="Load leads from file")] = False,
):
    """
    Shows charts from fetched leads from MyLead API.

    You can specify date ranges by --date-from and --date-to.
    API_KEY is REQUIRED. Can be specified in .env file or provided via command.

    If --save-file is used then fetched data is saved to JSON file.
    If --from-file is used then data is fetched from saved file rather than API.
    """
    check_api_key(apikey)
    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        transient=True,
    ) as progress:
        all_data = fetch_data(
            progress, apikey, date_from, date_to, from_file, save_file
        )
        df = process_data(all_data)

    ploting.choose_graph(df)


if __name__ == "__main__":
    app()
