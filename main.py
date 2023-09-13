import pandas as pd
from rich import print
import models, ml, utils, tables, ploting
from time import perf_counter
import logging
from dotenv import load_dotenv
import os
import typer
from typing_extensions import Annotated
from datetime import date, timedelta, datetime
import asyncio
from rich.progress import Progress, SpinnerColumn, TextColumn
import pandas as pd
import sys

DATEFORMATS = ["%Y-%m-%d", "%Y/%m/%d", "%d-%m-%Y", "%d/%m/%Y", "%Y.%m.%d", "%d.%m.%Y"]

logging.basicConfig(level=logging.WARNING)

app = typer.Typer()


def process_data(data: list[dict | None]) -> pd.DataFrame:
    if not data:
        print("No leads to process. Exiting program")
        sys.exit()
    df = utils.get_dataframe(data)
    df["hour_of_day"] = df["created_at.date"].dt.hour.astype(int)

    return df


@app.command()
def stats(
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
    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        transient=True,
    ) as progress:
        progress.add_task(description="Fetching data from MyLead API...", total=None)
        if apikey == "test":
            load_dotenv()
        apikey = os.getenv("API_KEY")  # type: ignore
        if not from_file:
            api = models.Api(token=apikey, date_from=date_from, date_to=date_to)
            all_data = asyncio.run(ml.fetch_all_pages_ML(api_data=api))
            if save_file == True:
                utils.data_to_file("myfile.json", all_data)
        else:
            all_data = utils.data_from_file("myfile.json")

        df = process_data(all_data)

    tables.table_from_data(
        df,
        title="Type of device leads were created on.",
        group_by_column="user_agent.device",
        column_name="Device type",
    )
    tables.table_from_data(
        df,
        title="Operating system leads were created on.",
        group_by_column="user_agent.operation_system",
        column_name="Operating system",
    )
    tables.table_from_data(
        df,
        title="Country leads were created from.",
        group_by_column="country",
        column_name="Operating system",
    )

    tables.table_from_data(
        df,
        title="Campaigns statistics",
        group_by_column="campaign_name",
        column_name="Campaigns statistics",
    )

    tables.table_from_data(
        df,
        title="Hour of day statistics",
        group_by_column="hour_of_day",
        column_name="Hour of day",
    )

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
        if save_file == True:
            utils.data_to_file("myfile.json", all_data)
    else:
        all_data = utils.data_from_file("myfile.json")

    df = utils.get_dataframe(all_data)

    ploting.create_bar_graph(df, group_by_column="country")
    ploting.create_bar_graph(df, group_by_column="user_agent.operation_system")


if __name__ == "__main__":
    app()
