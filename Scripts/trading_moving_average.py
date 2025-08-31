# Import required libraries
import yfinance as yf
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

# Function to download historical price data for a given ticker
def load_price_data(ticker, start_date, end_date):
    data = yf.download(ticker, start=start_date, end=end_date)
    data.reset_index(inplace=True)
    return data

# Function to generate moving average crossover signals
def generate_MAcrossover_signals(df, long_ma, short_ma):
    df_signal = df.copy()

    # Calculate short-term and long-term moving averages
    df_signal[f"MA{short_ma}"] = df_signal["Close"].rolling(short_ma).mean()
    df_signal[f"MA{long_ma}"] = df_signal["Close"].rolling(long_ma).mean()

    # Signal: 1 if short MA > long MA, else -1
    df_signal["Signal"] = np.where(df_signal[f"MA{short_ma}"] > df_signal[f"MA{long_ma}"], 1, -1)

    # Drop rows where long MA is NaN (due to rolling window)
    df_signal.dropna(subset=[f"MA{long_ma}"], inplace=True)

    df_signal.reset_index(inplace=True, drop=True)
    return df_signal

# Function to apply the moving average strategy
def run_moving_average_strategy(ticker, start_date, end_date, short_ma, long_ma):
    # Load historical data
    df = load_price_data(ticker, start_date, end_date)

    # Generate signals based on MA crossover
    df_trade = generate_MAcrossover_signals(df, long_ma, short_ma)

    # Position: shift signal forward to avoid lookahead bias
    df_trade["Position"] = df_trade["Signal"].shift().fillna(0)

    # Trade entry/exit signals
    df_trade["Trade"] = df_trade["Position"].diff().fillna(0)

    # Daily returns
    df_trade["Returns"] = df_trade["Close"].pct_change().fillna(0)

    # Cumulative strategy returns
    df_trade["StrategyReturns"] = ((df_trade["Returns"] * df_trade["Position"]) + 1).cumprod().bfill()

    # Benchmark: Buy-and-hold returns
    df_trade["Benchmark"] = df_trade["Close"] / df_trade["Close"].iloc[0]

    return df_trade

# Function to evaluate strategy performance with several metrics
def evaluate_strategy_performance(df):
    df_results = df.copy()
    strategy_returns = df['StrategyReturns'].pct_change().dropna()

    # Total return of the strategy
    total_return = (df_results["StrategyReturns"].iloc[-1] / df_results["StrategyReturns"].iloc[0]) - 1

    # Sharpe ratio: risk-adjusted return
    sharpe_ratio = ((strategy_returns.mean()) / (strategy_returns.std())) * np.sqrt(252)
    
    # Annualized volatility
    annualized_vol = strategy_returns.std() * np.sqrt(252)

    # Max drawdown: worst peak-to-trough drop
    df_results["StrategyReturnsMax"] = df_results["StrategyReturns"].cummax()
    df_results["Drawdown"] = (df_results["StrategyReturns"] - df_results["StrategyReturnsMax"]) / df_results["StrategyReturns"]
    max_drawdown = df_results["Drawdown"].min()
    
    # Information ratio: relative performance against benchmark
    mean_active_returns = (strategy_returns - df_results["Returns"]).mean()
    tracking_error = (strategy_returns - df_results["Returns"]).std()
    information_ratio = mean_active_returns / tracking_error

    # Number of trades: count buy and sell signals
    buy_signals = df_results[
        (
            ((df_results["Trade"] == 2) & (df_results["Trade"].shift(1) == 0))
            | ((df_results["Trade"] == 1) & (df_results["Trade"].shift(1) == 0))
        )    
    ]
    sell_signals = df_results[
        (
            ((df_results["Trade"] == -2) & (df_results["Trade"].shift(1) == 0))
            | ((df_results["Trade"] == -1) & (df_results["Trade"].shift(1) == 0))
        )
    ]
    num_trades = len(buy_signals) + len(sell_signals)
    
    return total_return, sharpe_ratio, annualized_vol, max_drawdown, information_ratio, num_trades

# Function to plot price, moving averages, signals, and performance
def plot_strategy(df, short_ma, long_ma):
    df_plot = df.copy()
    fig, axs = plt.subplots(1, 2, figsize=(15, 6))  # 1 row, 2 columns

    # Extract buy and sell signals
    buy_signals = df_plot[
        (
            ((df_plot["Trade"] == 2) & (df_plot["Trade"].shift(1) == 0))
            | ((df_plot["Trade"] == 1) & (df_plot["Trade"].shift(1) == 0))
        )
    ]
    sell_signals = df_plot[
        (
            ((df_plot["Trade"] == -2) & (df_plot["Trade"].shift(1) == 0))
            | ((df_plot["Trade"] == -1) & (df_plot["Trade"].shift(1) == 0))
        )
    ]

    # Plot price and signals
    axs[0].plot(df_plot["Close"], label="Close", color='grey')
    axs[0].plot(buy_signals["Close"], "^", markersize=10, color="green", label='Buy')
    axs[0].plot(sell_signals["Close"], "v", markersize=10, color="red", label='Sell')
    axs[0].plot(df_plot.index, df_plot[f"MA{short_ma}"], color="blue", label=f"MA{short_ma}")
    axs[0].plot(df_plot.index, df_plot[f"MA{long_ma}"], color="purple", label=f"MA{long_ma}")
    axs[0].set_ylabel("Price")
    axs[0].set_title(f"Moving Average Crossover Strategy: MA{short_ma} vs MA{long_ma}")
    axs[0].grid()
    axs[0].legend()

    # Plot strategy vs benchmark performance
    axs[1].plot(df_plot["StrategyReturns"], label="Strategy Performance", color='blue')
    axs[1].plot(df_plot["Benchmark"], label="Buy Hold Performance", color="grey")
    axs[1].set_ylabel("Returns")
    axs[1].set_title("Strategy vs Buy-and-Hold")
    axs[1].grid()
    axs[1].legend()

    plt.tight_layout()
    plt.show()
    return fig

# Function to search for optimal MA parameters based on a performance metric
def grid_search_optimal_ma(ticker, start, end, metric):
    short_ma_options = [3, 5, 7, 10, 15, 20, 25, 30]
    long_ma_options = [30, 40, 50, 60, 70, 80, 90, 100, 120, 150, 200]

    best_metric_value = None
    best_params = None
    best_df_result = None

    # Test all combinations of short and long MA
    for short_ma in short_ma_options:
        for long_ma in long_ma_options:
            if short_ma >= long_ma:
                continue  # skip invalid combinations

            # Run strategy and evaluate
            df_result = run_moving_average_strategy(ticker, start, end, short_ma, long_ma)
            total_return, sharpe_ratio, annualized_vol, max_drawdown, information_ratio, num_trades = evaluate_strategy_performance(df_result)

            # Select the current metric for comparison
            current_metric = None
            if metric == "Total Return":
                current_metric = total_return
                better = (best_metric_value is None) or (current_metric > best_metric_value)
            elif metric == "Sharpe Ratio":
                current_metric = sharpe_ratio
                better = (best_metric_value is None) or (current_metric > best_metric_value)
            elif metric == "Information Ratio":
                current_metric = information_ratio
                better = (best_metric_value is None) or (current_metric > best_metric_value)
            elif metric == "Drawdown":
                current_metric = max_drawdown  # closer to 0 is better
                better = (best_metric_value is None) or (current_metric > best_metric_value)
            else:
                raise ValueError(f"Unknown metric: {metric}")

            # Update best parameters if this one is better
            if better:
                best_metric_value = current_metric
                best_params = (short_ma, long_ma)

    return best_params, best_metric_value
