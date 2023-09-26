import pandas as pd
import plotly.express as px
from rich import box
from rich.console import Console
from rich.panel import Panel
from rich.prompt import Prompt

from myleadcli import tables
from myleadcli.utils import generate_caption


def create_bar_chart(
    df: pd.DataFrame,
    group_by_column: str,
    title: str,
    x_label: str,
    y_label: str,
    caption: str,
    invert_colors: bool = False,
) -> None:
    """
    Creates a bar chart based on the provided DataFrame.

    Args:
        df (pd.DataFrame): The DataFrame containing the data.
        group_by_column (str): The column to group the data by.
        title (str): The title of the chart.
        x_label (str): The label for the x-axis.
        y_label (str): The label for the y-axis.
        caption (str): The caption for the chart.
        invert_colors (bool, optional): Whether to invert chart. Defaults to False.

    Returns:
        None"""
    fig = px.bar(
        df,
        x=group_by_column,
        y="total_payout",
        text="total_payout",
        color="total_payout" if invert_colors else group_by_column,
        labels={
            group_by_column: x_label,
            "total_payout": y_label,
            "grouped_data": "Number of leads",
        },
        title=title,
        hover_data={"grouped_data": True},
    )

    fig.update_traces(texttemplate="%{text}", textposition="outside")
    fig.update_layout(
        title={
            "text": title,
            "y": 0.95,
            "x": 0.5,
            "xanchor": "center",
            "yanchor": "top",
        },
        xaxis_title=x_label,
        yaxis_title=y_label,
        xaxis_tickangle=-45,
    )

    fig.add_annotation(
        text=caption,
        xref="paper",
        yref="paper",
        x=0.5,
        y=1.05,
        showarrow=False,
    )

    fig.show()


def barchart_from_data(
    df: pd.DataFrame,
    group_by_column: str,
    title: str,
    x_label: str,
    y_label: str,
    sort_by: str = "total_payout",
    invert_colors: bool = False,
) -> None:
    """
    Intermediate function for creating chart from dataframe.

    Args:
        df (pd.DataFrame): The DataFrame containing the data.
        group_by_column (str): The column to group the data by.
        title (str): The title of the chart.
        x_label (str): The label for the x-axis.
        y_label (str): The label for the y-axis.
        sort_by (str, optional): The column to sort the data by. Defaults to "total_payout".
        invert_colors (bool, optional): Whether to invert the chart. Defaults to False.

    Returns:
        None"""
    caption = generate_caption(df)
    aggregated_data = tables.aggregate_data(
        data=df,
        group_by_column=group_by_column,
        sort_by=sort_by,
    )

    create_bar_chart(
        df=aggregated_data,
        group_by_column=group_by_column,
        title=title,
        x_label=x_label,
        y_label=y_label,
        caption=caption,
        invert_colors=invert_colors,
    )


def print_options(console: Console, options: dict[str, dict]) -> None:
    """
    Prints the available chart options to the console.

    Args:
        console (Console): The console object used for printing.
        options (dict[str, dict]): The dictionary of chart options.

    Returns:
        None"""
    console.print(
        Panel(
            "\n".join([f"{key}. {value['title']}" for key, value in options.items()])
            + "\n\n[bold]0. Exit[/bold]",
            title="Available charts",
            expand=False,
            box=box.ROUNDED,
            border_style="gold1",
        ),
    )


def choose_graph(df: pd.DataFrame) -> None:
    """
    Choose a graph to display based on the provided DataFrame.

    Args:
        df (pd.DataFrame): The DataFrame containing the data.

    Returns:
        None
    """
    console = Console()
    OPTIONS = {
        "1": {
            "title": "Device Types",
            "group_by_column": "Device Type",
            "x_label": "Device Type",
            "y_label": "Number of Leads",
            "invert_colors": False,
        },
        "2": {
            "title": "Operating Systems",
            "group_by_column": "Operating System",
            "x_label": "Operating System",
            "y_label": "Number of Leads",
            "invert_colors": False,
        },
        "3": {
            "title": "Country Statistics",
            "group_by_column": "Country Code",
            "x_label": "Country Code",
            "y_label": "Number of Leads",
            "invert_colors": False,
        },
        "4": {
            "title": "Campaigns",
            "group_by_column": "Campaign Name",
            "x_label": "Campaign Name",
            "y_label": "Number of Leads",
            "invert_colors": False,
        },
        "5": {
            "title": "Hourly Lead Approvals",
            "group_by_column": "Hour",
            "x_label": "Hour",
            "y_label": "Number of Leads",
            "invert_colors": True,
        },
        "6": {
            "title": "Day of Week Lead Approvals",
            "group_by_column": "Day of the Week",
            "x_label": "Day of the Week",
            "y_label": "Number of Leads",
            "invert_colors": False,
        },
    }
    print_options(console, OPTIONS)
    while True:
        choice = Prompt.ask(
            "Pick a chart to display or exit the program.",
            choices=[*list(OPTIONS.keys()), "0"],
        )

        if choice == "0":
            console.print("Exiting program.")
            break

        if option := OPTIONS.get(choice):
            barchart_from_data(df, **option)
        else:
            console.print("Wrong input")
