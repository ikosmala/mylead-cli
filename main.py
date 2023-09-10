import pandas as pd
from rich import print
import models, ml, utils
from time import perf_counter
import logging
from dotenv import load_dotenv
import os
import typer

logging.basicConfig(level=logging.INFO)


async def process(token: str):
    api = models.Api(token=token, limit=500)
    all_data = await ml.fetch_all_pages_ML(api_data=api)
    utils.data_to_file("myfile.json", all_data)
    from_file = utils.data_from_file("myfile.json")

    df = pd.json_normalize(from_file)

    print(df.head())
    print(df.columns)
    print(df["campaign_name"].unique())
    print(df["campaign_name"].describe())

    grouped = df.groupby("campaign_name").sum().sort_values("payout", ascending=False)
    print(grouped[["payout"]].head(10))


def main(apikey: str):
    print(f"Hello {apikey}")
    import asyncio

    start_time = perf_counter()
    if apikey == "test":
        load_dotenv()
        apikey = os.getenv("API_KEY")
    asyncio.run(process(apikey))
    end_time = perf_counter()
    logging.info(f"Finish time: {end_time - start_time} seconds")


if __name__ == "__main__":
    typer.run(main)
