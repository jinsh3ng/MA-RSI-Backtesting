# Import required libraries
import yfinance as yf
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

# Function to load historical price data using Yahoo Finance
def load_price_data(ticker, start_date, end_date):
    data = yf.download(ticker, start=start_date, end=end_date)
    data.reset_index(inplace=True)
    return data

# Function to implement the RSI-based trading strategy
def run_RSI_strategy(df, period, upper_bound, lower_bound, exit):
    # Define dynamic exit levels
    short_exit_bounds = upper_bound - exit
    long_exit_bounds = lower_bound + exit

    df_signals = df.copy()
    df_signals["Returns"] = df_signals["Close"].pct_change().fillna(0)

    # Separate gains and losses
    gains = df_signals["Returns"] * (df_signals["Returns"] > 0)
    losses = np.abs(df_signals["Returns"] * (df_signals["Returns"] < 0))

    # Calculate RSI using the rolling mean of gains and losses
    RS = gains.rolling(window=period).mean() / losses.rolling(window=period).mean()
    df_signals["RSI"] = 100 - (100 / (1 + RS))

    # Remove rows with NaN RSI (due to initial rolling window)
    df_signals.dropna(subset=[("RSI", "")], inplace=True)
    df_signals.reset_index(inplace=True, drop=True)

    # Initialize signal column and current trading position
    df_signals["Signal"] = 0
    current_position = 0  # 1 = long, -1 = short, 0 = neutral

    # Loop through each row to generate trading signals based on RSI
    for i in range(len(df_signals)):
        rsi = df_signals.loc[i, ("RSI", "")]
        
        if current_position == 0:
            if rsi < lower_bound:
                current_position = 1  # Enter long
            elif rsi > upper_bound:
                current_position = -1  # Enter short

        elif current_position == 1:
            if rsi > long_exit_bounds:
                current_position = 0  # Exit long

        elif current_position == -1:
            if rsi < short_exit_bounds:
                current_position = 0  # Exit short

        df_signals.loc[i, "Signal"] = current_position

        # Update position and trade signals
        df_signals["Position"] = df_signals["Signal"].shift().bfill()
        df_signals["Trade"] = df_signals["Position"].diff().fillna(0)

        # Calculate cumulative strategy returns
        df_signals["StrategyReturns"] = (1 + (df_signals["Position"] * df_signals["Returns"])).cumprod()
        df_signals.loc[0, "StrategyReturns"] = 1

    # Calculate benchmark (buy-and-hold) performance
    df_signals["Benchmark"] = df_signals["Close"] / df_signals["Close"].iloc[0]

    return df_signals

# Function to evaluate performance of the strategy
def evaluate_strategy_performance(df):
    df_results = df.copy()
    strategy_returns = df['StrategyReturns'].pct_change().dropna()

    # Total return
    total_return = (df_results["StrategyReturns"].iloc[-1] / df_results["StrategyReturns"].iloc[0]) - 1

    # Sharpe ratio (risk-adjusted return)
    sharpe_ratio = (strategy_returns.mean() / strategy_returns.std()) * np.sqrt(252)

    # Annualized volatility
    annualized_vol = strategy_returns.std() * np.sqrt(252)

    # Max drawdown calculation
    df_results["StrategyReturnsMax"] = df_results["StrategyReturns"].cummax()
    df_results["Drawdown"] = (df_results["StrategyReturns"] - df_results["StrategyReturnsMax"]) / df_results["StrategyReturns"]
    max_drawdown = df_results["Drawdown"].min()

    # Information ratio vs benchmark
    mean_active_returns = (strategy_returns - df_results["Returns"]).mean()
    tracking_error = (strategy_returns - df_results["Returns"]).std()
    information_ratio = mean_active_returns / tracking_error

    # Number of trades (buy + sell signals)
    buy_signals = df_results[
        ((df_results["Trade"] == 2) & (df_results["Trade"].shift(1) == 0))
        | ((df_results["Trade"] == 1) & (df_results["Trade"].shift(1) == 0))
    ]
    sell_signals = df_results[
        ((df_results["Trade"] == -2) & (df_results["Trade"].shift(1) == 0))
        | ((df_results["Trade"] == -1) & (df_results["Trade"].shift(1) == 0))
    ]
    num_trades = len(buy_signals) + len(sell_signals)

    return total_return, sharpe_ratio, annualized_vol, max_drawdown, information_ratio, num_trades

# Function to plot price, RSI, and strategy performance
def plot_strategy(df, upper_bound, lower_bound, exit):
    df_plot = df.copy()
    fig, axs = plt.subplots(2, 2, figsize=(15, 10))  # 2x2 grid of subplots

    # Identify buy/sell points
    buy_signals = df_plot[
        ((df_plot["Trade"] == 2) & (df_plot["Trade"].shift(1) == 0))
        | ((df_plot["Trade"] == 1) & (df_plot["Trade"].shift(1) == 0))
    ]
    sell_signals = df_plot[
        ((df_plot["Trade"] == -2) & (df_plot["Trade"].shift(1) == 0))
        | ((df_plot["Trade"] == -1) & (df_plot["Trade"].shift(1) == 0))
    ]

    # Subplot 1: Price with buy/sell markers
    axs[0, 0].plot(df_plot["Close"], label="Close", color='grey')
    axs[0, 0].plot(buy_signals.index, buy_signals["Close"], "^", color="green", label="Buy", markersize=10)
    axs[0, 0].plot(sell_signals.index, sell_signals["Close"], "v", color="red", label="Sell", markersize=10)
    axs[0, 0].set_ylabel("Price")
    axs[0, 0].set_title(f"{lower_bound} - {upper_bound} RSI Trading Strategy")
    axs[0, 0].grid()
    axs[0, 0].legend()

    # Subplot 2: Strategy vs Benchmark performance
    axs[0, 1].plot(df_plot["StrategyReturns"], label="Strategy", color='blue')
    axs[0, 1].plot(df_plot["Benchmark"], label="Buy & Hold", color='grey')
    axs[0, 1].set_ylabel("Cumulative Returns")
    axs[0, 1].set_title("Strategy vs Benchmark")
    axs[0, 1].grid()
    axs[0, 1].legend()

    # Subplot 3: RSI levels with upper/lower/exit bounds
    axs[1, 0].plot(df_plot["RSI"], label="RSI", color='purple')
    axs[1, 0].axhline(upper_bound, color='red', linestyle='--', label='Upper Bound')
    axs[1, 0].axhline(lower_bound, color='green', linestyle='--', label='Lower Bound')
    axs[1, 0].axhline(upper_bound - exit, color='grey', linestyle='--', label='Short Exit Bound')
    axs[1, 0].axhline(lower_bound + exit, color='grey', linestyle='--', label='Long Exit Bound')
    axs[1, 0].set_ylabel("RSI")
    axs[1, 0].set_title("RSI Indicator")
    axs[1, 0].grid()
    axs[1, 0].legend()

    # Subplot 4: Position over time (1 = long, -1 = short)
    axs[1, 1].plot(df_plot["Position"], label='Position', color='blue')
    axs[1, 1].set_title('Position')
    axs[1, 1].legend()
    axs[1, 1].grid()

    plt.tight_layout()
    plt.show()
    return fig
