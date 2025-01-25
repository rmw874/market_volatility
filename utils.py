import os


def saveDF(output_path, df) -> None:
    os.makedirs(output_path, exist_ok=True)
    symbol = df.index[0]
    max = df["date"].max().replace("-", "")
    min = df["date"].min().replace("-", "")
    csv_path = os.path.join(output_path, f"{symbol}_{min}-{max}.csv")
    df.to_csv(csv_path)
