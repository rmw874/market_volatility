import requests
from datetime import datetime
import pandas as pd


def get_binance_klines(symbol, start_date, end_date, interval):
    start_ts = int(datetime.strptime(start_date, "%Y-%m-%d").timestamp() * 1000)
    end_ts = int(datetime.strptime(end_date, "%Y-%m-%d").timestamp() * 1000)

    url = "https://api.binance.com/api/v3/klines"
    params = {
        "symbol": symbol,
        "interval": interval,
        "startTime": start_ts,
        "endTime": end_ts,
        "limit": 1000,
    }
    return requests.get(url, params=params).json()


def create_crypto_DF(
    symbol="BTCUSDT", start_date="2025-01-01", end_date="2025-01-11", interval="1d"
):
    data = get_binance_klines(symbol, start_date, end_date, interval)
    df = pd.DataFrame(
        data,
        columns=[
            "open_time",
            "open",
            "high",
            "low",
            "close",
            "volume",
            "close_time",
            "quote_volume",
            "trades_count",
            "taker_buy_base_volume",
            "taker_buy_quote_volume",
            "ignore",
        ],
    )
    df["symbol"] = symbol
    df["open_time"] = list(
        map(
            lambda ts: datetime.fromtimestamp(ts / 1000).strftime("%Y-%m-%d"),
            df["open_time"],
        )
    )
    df = df.rename(columns={"open_time": "date"})
    df = df.drop(["close_time", "ignore"], axis=1)
    df.set_index("symbol", inplace=True)
    return df
