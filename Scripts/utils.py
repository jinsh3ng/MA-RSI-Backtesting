import yfinance as yf
import pandas as pd
import numpy as np


def load_price_data(ticker: str, start_date: str, end_date: str) -> pd.DataFrame:
    """Download price data and flatten MultiIndex columns from yfinance."""
    data = yf.download(ticker, start=start_date, end=end_date)

    # yfinance returns MultiIndex columns for single tickers — flatten them
    if isinstance(data.columns, pd.MultiIndex):
        data.columns = data.columns.get_level_values(0)

    data.reset_index(inplace=True)
    return data


def detect_trades(df: pd.DataFrame):
    """Identify buy and sell trade entries from a strategy DataFrame."""
    buy_mask = (
        ((df["Trade"] == 2) & (df["Trade"].shift(1) == 0))
        | ((df["Trade"] == 1) & (df["Trade"].shift(1) == 0))
    )
    sell_mask = (
        ((df["Trade"] == -2) & (df["Trade"].shift(1) == 0))
        | ((df["Trade"] == -1) & (df["Trade"].shift(1) == 0))
    )
    return df[buy_mask], df[sell_mask]


def evaluate_strategy_performance(df: pd.DataFrame):
    """Calculate performance metrics for a completed strategy backtest."""
    df_results = df.copy()
    strategy_returns = df["StrategyReturns"].pct_change().dropna()

    # Total Return
    total_return = (df_results["StrategyReturns"].iloc[-1] / df_results["StrategyReturns"].iloc[0]) - 1

    # Sharpe Ratio
    sharpe_ratio = (strategy_returns.mean() / strategy_returns.std()) * np.sqrt(252) if strategy_returns.std() != 0 else 0.0

    # Annualized Volatility
    annualized_vol = strategy_returns.std() * np.sqrt(252)

    # Max Drawdown (fixed: divide by peak, not current value)
    df_results["StrategyReturnsMax"] = df_results["StrategyReturns"].cummax()
    df_results["Drawdown"] = (
        (df_results["StrategyReturns"] - df_results["StrategyReturnsMax"]) / df_results["StrategyReturnsMax"]
    )
    max_drawdown = df_results["Drawdown"].min()

    # Information Ratio (fixed: align lengths properly)
    benchmark_returns = df_results["Returns"].iloc[1:]
    active_returns = strategy_returns.values - benchmark_returns.values
    tracking_error = np.std(active_returns)
    information_ratio = np.mean(active_returns) / tracking_error if tracking_error != 0 else 0.0

    # Number of Trades
    buy_signals, sell_signals = detect_trades(df_results)
    num_trades = len(buy_signals) + len(sell_signals)

    return float(total_return), float(sharpe_ratio), float(annualized_vol), float(max_drawdown), float(information_ratio), int(num_trades)