import pandas as pd
import plotly.express as px
from rich import box
from rich.console import Console
from rich.panel import Panel
from rich.prompt import Prompt

from mlcli import tables
from mlcli.utils import generate_caption


def create_bar_chart(
    df: pd.DataFrame,
    group_by_column: str,
    title: str,
    x_label: str,
    y_label: str,
    caption: str,
    invert_colors: bool = False,
) -> None:
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
    console = Console()
    OPTIONS = {
        "1": {
            "title": "Type of device on which leads were created",
            "group_by_column": "user_agent.device",
            "x_label": "Device Type",
            "y_label": "Leads Value",
            "invert_colors": False,
        },
        "2": {
            "title": "Operating system on which leads were created",
            "group_by_column": "user_agent.operation_system",
            "x_label": "Operating System",
            "y_label": "Leads Value",
            "invert_colors": False,
        },
        "3": {
            "title": "Country statistics",
            "group_by_column": "country",
            "x_label": "Country code",
            "y_label": "Leads Value",
            "invert_colors": False,
        },
        "4": {
            "title": "Campaigns chart",
            "group_by_column": "campaign_name",
            "x_label": "Campaign name",
            "y_label": "Leads Value",
            "invert_colors": False,
        },
        "5": {
            "title": "Hour of day lead was approved",
            "group_by_column": "hour_of_day",
            "x_label": "Hour",
            "y_label": "Leads Value",
            "invert_colors": True,
        },
        "6": {
            "title": "Hour of day lead was approved",
            "group_by_column": "day_of_week",
            "x_label": "Day of the week",
            "y_label": "Leads Value",
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
