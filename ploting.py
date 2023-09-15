import pandas as pd
import plotly.express as px

import tables


def create_bar_graph(
    df: pd.DataFrame, group_by_column: str, title: str, x_label: str, y_label: str
) -> None:
    aggregated_data = tables.aggregate_data(data=df, group_by_column=group_by_column)
    fig = px.bar(
        aggregated_data,
        x=group_by_column,
        y="total_payout",
        text="total_payout",
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

    fig.show()
