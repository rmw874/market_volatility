import configparser
import requests
import json
import pandas as pd

config = configparser.ConfigParser()
config.read("config.ini")


def FMPUrl(ticker, start_date="2025-01-01", end_date="2025-01-11"):
    key = config.get("FMP", "API_KEY")
    return f"https://financialmodelingprep.com/api/v3/historical-price-full/{ticker}?from={start_date}&to={end_date}&apikey={key}"


with open("test.json", "r") as file:
    test = json.load(file)


def create_stock_DF(ticker, start_date, end_date):
    data = requests.get(FMPUrl(ticker, start_date, end_date)).json()
    df = pd.DataFrame.from_dict(data["historical"])
    df.index = pd.Index([data["symbol"]] * len(df))
    df.index.name = "symbol"
    return df
