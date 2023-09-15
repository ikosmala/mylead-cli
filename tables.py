import pandas as pd
from rich import box
from rich.console import Console
from rich.padding import Padding
from rich.panel import Panel
from rich.prompt import Prompt
from rich.table import Table

# ml_subs
# daily average, best day,


def aggregate_data(
    data: pd.DataFrame, group_by_column: str, sort_by: str = "total_payout"
) -> pd.DataFrame:
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
    sum_of_all_leads: int,
    sum_payouts: float,
) -> None:
    table = Table(title=title, caption=caption, box=box.ROUNDED, header_style="gold1")
    table.add_column(column_name, justify="left", style="cyan", no_wrap=True)
    table.add_column(
        "No. of leads (% of total)", justify="right", style="white", no_wrap=True
    )
    table.add_column(
        "Total payout (% of total)", justify="right", style="green", no_wrap=True
    )
    data[group_by_column] = data[group_by_column].astype(str)

    for _, row in data.iterrows():
        grouped_data_percent = row["grouped_data"] / sum_of_all_leads * 100
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
    start_date = data["created_at.date"].min()
    end_date = data["created_at.date"].max()
    sum_of_all_leads = len(data)
    result = aggregate_data(data, group_by_column=group_by_column, sort_by=sort_by)
    sum_payouts = result["total_payout"].sum()
    caption = f"Data gathered between {start_date} -- {end_date}"

    create_table(
        data=result,
        title=title,
        caption=caption,
        column_name=column_name,
        group_by_column=group_by_column,
        sum_of_all_leads=sum_of_all_leads,
        sum_payouts=sum_payouts,
    )


def choose_table(df: pd.DataFrame) -> None:
    console = Console()
    OPTIONS = OPTIONS = {
        "1": (
            "Type of device on which leads were created.",
            "user_agent.device",
            "Device Type",
        ),
        "2": (
            "Operating system on which leads were created.",
            "user_agent.operation_system",
            "Operating System",
        ),
        "3": ("Country from which leads were created.", "country", "Country"),
        "4": ("Statistics by campaign.", "campaign_name", "Campaign Statistics"),
        "5": ("Statistics by hour of the day.", "hour_of_day", "Hourly Statistics"),
    }

    console.print(
        Panel(
            "\n".join([f"{key}. {value[0]}" for key, value in OPTIONS.items()])
            + "\n\n[bold]0. Exit[/bold]",
            title="Available statistics",
            expand=False,
            box=box.ROUNDED,
            border_style="gold1",
        )
    )
    while True:
        table_choice = Prompt.ask(
            "Pick a statistic to display or exit the program.",
            choices=[*list(OPTIONS.keys()), "0"],
        )

        if table_choice == "0":
            console.print("Exiting program.")
            break

        title, group_by_column, column_name = OPTIONS.get(
            table_choice, (None, None, None)
        )

        if title:
            table_from_data(
                data=df,
                title=title,
                group_by_column=group_by_column,
                column_name=column_name,
            )
        else:
            console.print("Wrong input")
