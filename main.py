from stockHistory import create_stock_DF
from cryptoHistory import create_crypto_DF
from utils import saveDF


def createDFs(symbol, ticker, start_date, end_date):
    cryptoDF = create_crypto_DF(symbol=symbol, start_date=start_date, end_date=end_date)
    stockDF = create_stock_DF(ticker=ticker, start_date=start_date, end_date=end_date)
    return cryptoDF, stockDF


cdf, sdf = createDFs("BTCUSDT", "MSTR", "2024-11-01", "2025-01-23")

saveDF("results/", cdf)
saveDF("results/", sdf)
