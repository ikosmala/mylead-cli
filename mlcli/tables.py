"""
Module for generating and displaying rich tables with aggregated data.
This module provides functions for aggregating data, creating rich tables,
and allowing users to choose which statistics to display.
"""
import pandas as pd
from rich import box
from rich.console import Console
from rich.padding import Padding
from rich.panel import Panel
from rich.prompt import Prompt
from rich.table import Table
from datetime import date, timedelta
from mlcli.utils import generate_caption


def aggregate_data(
    data: pd.DataFrame,
    group_by_column: str,
    sort_by: str = "total_payout",
) -> pd.DataFrame:
    """
    Aggregate data by a specified column and calculate total payout for each group.

    Args:
        data (pd.DataFrame): The input DataFrame.
        group_by_column (str): The column by which to group the data.
        sort_by (str, optional): The column to sort the result by. Defaults to "total_payout".

    Returns:
        pd.DataFrame: The aggregated DataFrame.
    """
    selected_columns = [group_by_column, "payout"]
    df = data[selected_columns]
    return (
        df.groupby(group_by_column)
        .agg(
            grouped_data=pd.NamedAgg(column=group_by_column, aggfunc="size"),
            total_payout=pd.NamedAgg(column="payout", aggfunc="sum"),
        )
        .reset_index()
        .sort_values(sort_by, ascending=False)
    )


def create_table(
    data: pd.DataFrame,
    title: str,
    caption: str,
    column_name: str,
    group_by_column: str,
    num_of_leads: int,
    sum_payouts: float,
) -> None:
    """
    Create a rich table to display aggregated data.

    Args:
        data (pd.DataFrame): The aggregated data.
        title (str): The title of the table.
        caption (str): The caption for the table.
        column_name (str): The name of the column to display.
        group_by_column (str): The column used for grouping.
        num_of_leads (int): The total number of leads.
        sum_payouts (float): The total sum of payouts.
    """
    table = Table(title=title, caption=caption, box=box.ROUNDED, header_style="gold1")
    table.add_column(column_name, justify="left", style="cyan", no_wrap=True)
    table.add_column(
        "No. of leads (% of total)",
        justify="right",
        style="white",
        no_wrap=True,
    )
    table.add_column(
        "Total payout (% of total)",
        justify="right",
        style="green",
        no_wrap=True,
    )
    data[group_by_column] = data[group_by_column].astype(str)

    for _, row in data.iterrows():
        grouped_data_percent = row["grouped_data"] / num_of_leads * 100
        total_payout_percent = row["total_payout"] / sum_payouts * 100
        table.add_row(
            row[group_by_column],
            f"{row['grouped_data']} ({grouped_data_percent:.2f}%)",
            f"{row['total_payout']:.2f} ({total_payout_percent:.2f}%)",
        )

    console = Console()
    console.rule(style="gold1")
    console.print(Padding(table, 1))


def table_from_data(
    data: pd.DataFrame,
    title: str,
    group_by_column: str,
    column_name: str,
    sort_by: str = "total_payout",
) -> None:
    """
    Create a rich table from input data.

    Args:
        data (pd.DataFrame): The input data.
        title (str): The title of the table.
        group_by_column (str): The column to group by.
        column_name (str): The name of the column to display.
        sort_by (str, optional): The column to sort the result by. Defaults to "total_payout".
    """
    caption = generate_caption(data)
    num_of_leads = data.shape[0]
    result = aggregate_data(data, group_by_column=group_by_column, sort_by=sort_by)
    sum_payouts = result["total_payout"].sum()

    create_table(
        data=result,
        title=title,
        caption=caption,
        column_name=column_name,
        group_by_column=group_by_column,
        num_of_leads=num_of_leads,
        sum_payouts=sum_payouts,
    )


def print_console(console: Console, options: dict[str, dict]) -> None:
    """
    Print a menu of available statistics options.

    Args:
        console (Console): The Rich Console object for output.
        options (dict[str, dict]): A dictionary of statistic options.
    """
    console.print(
        Panel(
            "\n".join([f"{key}. {value['title']}" for key, value in options.items()])
            + "\n\n[bold]0. Exit[/bold]",
            title="Available statistics",
            expand=False,
            box=box.ROUNDED,
            border_style="gold1",
        ),
    )


def choose_table(df: pd.DataFrame) -> None:
    """
    Display a menu of statistics options and allow the user to choose which one to display.

    Args:
        df (pd.DataFrame): The input DataFrame.
    """
    console = Console()
    OPTIONS = {
        "1": {
            "title": "Statistics based on the device of lead origin.",
            "group_by_column": "user_agent.device",
            "column_name": "Device Type",
        },
        "2": {
            "title": "Statistics based on the operating system of lead origin.",
            "group_by_column": "user_agent.operation_system",
            "column_name": "Operating System",
        },
        "3": {
            "title": "Statistics based on the country of lead origin.",
            "group_by_column": "country",
            "column_name": "Country",
        },
        "4": {
            "title": "Statistics by campaign.",
            "group_by_column": "campaign_name",
            "column_name": "Campaign name",
        },
        "5": {
            "title": "Statistics by hour of the day.",
            "group_by_column": "hour_of_day",
            "column_name": "Hour",
        },
        "6": {
            "title": "Statistics by day of the week.",
            "group_by_column": "day_of_week",
            "column_name": "Day",
        },
    }
    print_console(console, OPTIONS)

    while True:
        choice = Prompt.ask(
            "Pick a statistic to display or exit the program.",
            choices=[*list(OPTIONS.keys()), "0"],
        )

        if choice == "0":
            console.print("Exiting program.")
            break

        if option := OPTIONS.get(choice):
            table_from_data(df, **option)
        else:
            console.print("Wrong input")


def rolling_window(df: pd.DataFrame) -> None:
    print(df.dtypes)
    result = aggregate_data(df, group_by_column="date")
    result.set_index("date", inplace=True)
    result.sort_index(inplace=True)
    rolling = result["total_payout"].rolling(window="7D").sum()
    rolling_sorted = rolling.sort_values(ascending=False)
    best_window_end = rolling.idxmax()
    best_window_start = pd.to_datetime(best_window_end) - pd.DateOffset(days=6)

    print("Start Date of Best Rolling Window:", best_window_start)
    print("End Date of Best Rolling Window:", best_window_end)
    print(rolling_sorted.head(5))
