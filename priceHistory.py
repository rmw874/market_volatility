import configparser
import requests
import json
import os
import pandas as pd

config = configparser.ConfigParser()
config.read("config.ini")


def FMPUrl(ticker, start="2025-01-01", end="2025-01-11"):
    key = config.get("FMP", "API_KEY")
    return f"https://financialmodelingprep.com/api/v3/historical-price-full/{ticker}?from={start}&to={end}&apikey={key}"


with open("test.json", "r") as file:
    test = json.load(file)


def createDF(ticker, start, end):
    data = requests.get(FMPUrl(ticker, start, end)).json()
    df = pd.DataFrame.from_dict(data["historical"])
    df.index = pd.Index([data["symbol"]] * len(df))
    df.index.name = "symbol"
    return df


def saveDF(output_path, df) -> None:
    os.makedirs(output_path, exist_ok=True)
    stock = data.index[0]
    max = data["date"].max().replace("-", "")
    min = data["date"].min().replace("-", "")
    csv_path = os.path.join(output_path, f"{stock}_{min}-{max}.csv")
    df.to_csv(csv_path)


data = createDF("AAPL", start="2022-01-01", end="2025-01-15")

saveDF("results/", data)
