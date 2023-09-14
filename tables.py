from rich.table import Table
from rich.console import Console
from rich.padding import Padding
from rich import box
import pandas as pd
from rich.prompt import Prompt

# device type  user_agent.device
# country
# operation system user_agent.operation_system
# ml_subs
# hour_of_leads
# daily average, best day,


def aggregate_data(
    data: pd.DataFrame, group_by_column: str, sort_by: str = "total_payout"
) -> pd.DataFrame:
    selected_columns = [group_by_column, "payout"]
    df = data[selected_columns]
    result = (
        df.groupby(group_by_column)
        .agg(
            grouped_data=pd.NamedAgg(column=group_by_column, aggfunc="size"),
            total_payout=pd.NamedAgg(column="payout", aggfunc="sum"),
        )
        .reset_index()
        .sort_values(sort_by, ascending=False)
    )
    return result


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

    for index, row in data.iterrows():
        table.add_row(
            row[group_by_column],
            f"{row['grouped_data']} ({(row['grouped_data']/ sum_of_all_leads* 100):.2f}%)",
            f"{row['total_payout']:.2f} ({(row['total_payout']/ sum_payouts* 100):.2f}%)",
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
    console.print("Choose one option")
    name = Prompt.ask("Enter your name", choices=["1", "2", "3", "4", "5"])
    print(name)
    print(type(name))
