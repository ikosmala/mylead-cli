import pandas as pd
from rich import print
import models, ml, utils, tables, ploting
import logging
from dotenv import load_dotenv
import os
import typer
from typing import Any
from typing_extensions import Annotated
from datetime import datetime
import asyncio
from rich.progress import Progress, SpinnerColumn, TextColumn
import sys

DATEFORMATS = ["%Y-%m-%d", "%Y/%m/%d", "%d-%m-%Y", "%d/%m/%Y", "%Y.%m.%d", "%d.%m.%Y"]

logging.basicConfig(level=logging.INFO)

app = typer.Typer()


def process_data(data: list[dict[str, Any]]) -> pd.DataFrame:
    if not data:
        print("No leads to process. Exiting program")
        sys.exit()
    df = utils.get_dataframe(data)
    df["hour_of_day"] = df["created_at.date"].dt.hour.astype(int)

    return df


@app.command()
def stats(
    apikey: Annotated[
        str,
        typer.Option(
            help="MyLead API Key",
            prompt="MyLeadAPI key (leave empty if fetching from file)",
            hide_input=True,
        ),
    ],
    date_from: Annotated[
        datetime,
        typer.Option(
            help="Start date for gathering data. Default: 365 days ago.",
            formats=DATEFORMATS,
            default_factory=utils.one_year_ago_day,
        ),
    ],
    date_to: Annotated[
        datetime,
        typer.Option(
            help="End date for gathering data. Default: today", formats=DATEFORMATS
        ),
    ] = datetime.now(),
    save_file: Annotated[bool, typer.Option(help="Save leads to file")] = False,
    from_file: Annotated[bool, typer.Option(help="Load leads from file")] = False,
):
    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        transient=True,
    ) as progress:
        if apikey == "test":
            load_dotenv()
            apikey = os.getenv("API_KEY")
        if not from_file:
            progress.add_task(
                description="Fetching data from MyLead API...", total=None
            )
            api = models.Api(token=apikey, date_from=date_from, date_to=date_to)
            all_data = asyncio.run(ml.fetch_all_pages_ML(api_data=api))
            if save_file is True:
                utils.data_to_file("myfile.json", all_data)
        else:
            # todo fetch from specified file
            progress.add_task(description="Fetching data from file...", total=None)
            all_data = utils.data_from_file("myfile.json")

        df = process_data(all_data)

    tables.choose_table(df)


@app.command()
def plot(
    apikey: Annotated[str, typer.Argument(help="MyLead API Key")],
    date_from: Annotated[
        datetime,
        typer.Option(
            help="Start date for gathering data. Default: 365 days ago.",
            formats=DATEFORMATS,
            default_factory=utils.one_year_ago_day,
        ),
    ],
    date_to: Annotated[
        datetime,
        typer.Option(
            help="End date for gathering data. Default: today", formats=DATEFORMATS
        ),
    ] = datetime.now(),
    save_file: Annotated[bool, typer.Option(help="Save leads to file")] = False,
    from_file: Annotated[bool, typer.Option(help="Load leads from file")] = False,
):
    if apikey == "test":
        load_dotenv()
        apikey = os.getenv("API_KEY")  # type: ignore
    if not from_file:
        api = models.Api(token=apikey, date_from=date_from, date_to=date_to, limit=500)
        all_data = asyncio.run(ml.fetch_all_pages_ML(api_data=api))
        if save_file is True:
            utils.data_to_file("myfile.json", all_data)
    else:
        all_data = utils.data_from_file("myfile.json")

    df = process_data(all_data)

    ploting.create_bar_graph(df, group_by_column="country")
    ploting.create_bar_graph(df, group_by_column="user_agent.operation_system")


if __name__ == "__main__":
    app()
