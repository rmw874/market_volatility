from utils import save_df
from statsmodels.tsa.stattools import grangercausalitytests, ccf
from stock_history import create_stock_df
from crypto_history import create_crypto_df
import seaborn as sns
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

def create_dfs(symbol, ticker, start_date, end_date):
    crypto_df = create_crypto_df(symbol=symbol, start_date=start_date, end_date=end_date)
    stock_df = create_stock_df(ticker=ticker, start_date=start_date, end_date=end_date)
    return crypto_df, stock_df

def match_dates(fst_series, snd_series):
    fst_col = 'adjClose' if 'adjClose' in fst_series.columns else 'close'
    snd_col = 'adjClose' if 'adjClose' in snd_series.columns else 'close'
    
    fst_series = fst_series.set_index('date')
    snd_series = snd_series.set_index('date')
    
    common_dates = fst_series.index.intersection(snd_series.index).sort_values()
    fst_aligned = fst_series.loc[common_dates, fst_col].values
    snd_aligned = snd_series.loc[common_dates, snd_col].values
    
    return fst_aligned, snd_aligned

def rolling_volatility(fst_eod, snd_eod):
    fst_eod = pd.to_numeric(fst_eod)
    snd_eod = pd.to_numeric(snd_eod)
    
    if len(fst_eod) < 21:
        window = max(5, n//3)
    else:
        window = 21

    fst_ror = (fst_eod[1:] - fst_eod[:-1]) / fst_eod[:-1]
    snd_ror = (snd_eod[1:] - snd_eod[:-1]) / snd_eod[:-1]

    vol_fst = pd.Series(fst_ror).rolling(window=window).std().iloc[window-1:].values
    vol_snd = pd.Series(snd_ror).rolling(window=window).std().iloc[window-1:].values
    
    return vol_fst, vol_snd

def compute_lead_lag(vol1, vol2, max_lags=5):
    cross_corr = ccf(vol1, vol2, adjusted=False)[:max_lags+1]
    lags = np.arange(len(cross_corr))
    max_corr_idx = np.argmax(np.abs(cross_corr))

    return {
        'lead_lag_days': max_corr_idx,
        'max_correlation': cross_corr[max_corr_idx],
        'correlation_by_lag': dict(zip(lags, cross_corr))
    }

def compute_spillover(vol1, vol2, max_lags=5):
    df = pd.DataFrame({
        'vol1': vol1,
        'vol2': vol2,
    })
    granger_1_to_2 = grangercausalitytests(df[['vol2', 'vol1']], maxlag=max_lags)
    granger_2_to_1 = grangercausalitytests(df[['vol1', 'vol2']], maxlag=max_lags)
    results = {
        'vol1_to_vol2': {lag: test[0]['ssr_chi2test'][1] for lag, test in granger_1_to_2.items()},
        'vol2_to_vol1': {lag: test[0]['ssr_chi2test'][1] for lag, test in granger_2_to_1.items()}
    }
    return results

def plot_volatility_analysis(vol1, vol2, lead_lag_results, spillover_results, t1, t2, max_lags=10):
    fig = plt.figure(figsize=(15, 12))
    
    # Cross-correlation plot
    ax1 = plt.subplot(221)
    lags = np.arange(max_lags + 1)
    correlations = [lead_lag_results['correlation_by_lag'][lag] for lag in lags]
    ax1.plot(lags, correlations, 'b-', marker='o')
    ax1.axhline(y=0, color='r', linestyle='--', alpha=0.3)
    ax1.set_title('Cross-correlation Function')
    ax1.set_xlabel('Lag (days)')
    ax1.set_ylabel('Correlation')
    
    # Spillover heatmap - using available lags only
    ax2 = plt.subplot(222)
    available_lags = list(spillover_results['vol1_to_vol2'].keys())
    spillover_data = np.array([
        [spillover_results['vol1_to_vol2'][i] for i in available_lags],
        [spillover_results['vol2_to_vol1'][i] for i in available_lags]
    ])
    sns.heatmap(spillover_data, 
                annot=True, 
                fmt='.3f', 
                cmap='YlOrRd_r',
                yticklabels=[f'{t2}→{t1}', f'{t1}→{t2}'],
                xticklabels=available_lags,
                ax=ax2)
    ax2.set_title('Granger Causality p-values')
    ax2.set_xlabel('Lag (days)')
    
    # Joint distribution scatter plot
    ax3 = plt.subplot(223)
    sns.scatterplot(x=vol1, y=vol2, alpha=0.5, ax=ax3)
    sns.kdeplot(x=vol1, y=vol2, levels=5, color='red', alpha=0.5, ax=ax3)
    ax3.set_title('Joint Volatility Distribution')
    ax3.set_xlabel(f'{t1} Volatility')
    ax3.set_ylabel(f'{t2} Volatility')
    
    # Rolling correlation
    ax4 = plt.subplot(224)
    rolling_corr = pd.Series(vol1).rolling(window=60).corr(pd.Series(vol2))
    ax4.plot(range(len(rolling_corr)), rolling_corr)
    ax4.set_title('60-day Rolling Correlation')
    ax4.set_xlabel('Time')
    ax4.set_ylabel('Correlation')
    ax4.axhline(y=0, color='r', linestyle='--', alpha=0.3)
    
    plt.tight_layout()
    return fig

def main():
    # t1 = 'BTCUSDT'
    # t2 = 'SMCI'
    # df1, df2 = create_dfs(t1, t2, "2024-06-01", "2025-01-24")
    # save_df('results/', df1)
    # save_df('results/', df2)
    # mstr = pd.read_csv('results/MSTR_20241101-20250123.csv')
    # btc = pd.read_csv('results/BTCUSDT_20241101-20250122.csv')

    t1 = 'SPY'
    t2 = 'NVDA'
    sd = '2024-06-01'
    ed = '2025-01-24'
    df1 = create_stock_df(t1, sd, ed)
    df2 = create_stock_df(t2, sd, ed)

    eod1, eod2 = match_dates(df1, df2)
    vol1, vol2 = rolling_volatility(eod1, eod2)

    lead_lag_results = compute_lead_lag(vol1, vol2, 10)
    spillover_results = compute_spillover(vol1, vol2)
    
    print(f"Lead/Lag Days: {lead_lag_results['lead_lag_days']}")
    print(f"Maximum Correlation: {lead_lag_results['max_correlation']:.4f}")

    fig = plot_volatility_analysis(vol1, vol2, lead_lag_results, spillover_results, t1=t1, t2=t2)
    plt.savefig(
        f"results/{t1}-{t2}_variance_correlation.png",
        dpi=300,
    )
    plt.close()

if __name__ == "__main__":
    main()