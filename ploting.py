import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
import tables


def create_bar_graph(df: pd.DataFrame, group_by_column: str):
    aggregated_data = tables.aggregate_data(data=df, group_by_column=group_by_column)
    sns.barplot(
        x=group_by_column, y="grouped_data", data=aggregated_data, palette="viridis"
    )

    plt.show()
