import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from utils import load_price_data, detect_trades


def run_RSI_strategy(df, period, upper_bound, lower_bound, exit_threshold):
    short_exit_bounds = upper_bound - exit_threshold
    long_exit_bounds = lower_bound + exit_threshold

    df_signals = df.copy()
    df_signals["Returns"] = df_signals["Close"].pct_change().fillna(0)

    # RSI calculation
    gains = df_signals["Returns"].clip(lower=0)
    losses = df_signals["Returns"].clip(upper=0).abs()
    avg_gain = gains.rolling(window=period).mean()
    avg_loss = losses.rolling(window=period).mean()
    rs = avg_gain / avg_loss
    df_signals["RSI"] = 100 - (100 / (1 + rs))

    df_signals.dropna(subset=["RSI"], inplace=True)
    df_signals.reset_index(inplace=True, drop=True)

    # Generate signals via state machine
    signals = np.zeros(len(df_signals))
    current_position = 0  # 1 = Long, -1 = Short, 0 = Neutral

    for i in range(len(df_signals)):
        rsi = df_signals.loc[i, "RSI"]
        if current_position == 0:
            if rsi < lower_bound:
                current_position = 1  # enter long
            elif rsi > upper_bound:
                current_position = -1  # enter short
        elif current_position == 1:
            if rsi > long_exit_bounds:
                current_position = 0  # exit long
        elif current_position == -1:
            if rsi < short_exit_bounds:
                current_position = 0  # exit short
        signals[i] = current_position

    df_signals["Signal"] = signals
    df_signals["Position"] = df_signals["Signal"].shift().bfill()
    df_signals["Trade"] = df_signals["Position"].diff().fillna(0)
    df_signals["StrategyReturns"] = (1 + (df_signals["Position"] * df_signals["Returns"])).cumprod()
    df_signals.loc[0, "StrategyReturns"] = 1
    df_signals["Benchmark"] = df_signals["Close"] / df_signals["Close"].iloc[0]

    return df_signals


def plot_strategy(df, upper_bound, lower_bound, exit_threshold):
    df_plot = df.copy()
    fig, axs = plt.subplots(2, 2, figsize=(15, 10))

    buy_signals, sell_signals = detect_trades(df_plot)

    axs[0, 0].plot(df_plot["Close"], label="Close", color='grey')
    axs[0, 0].plot(buy_signals.index, buy_signals["Close"], "^", color="green", label="Buy", markersize=10)
    axs[0, 0].plot(sell_signals.index, sell_signals["Close"], "v", color="red", label="Sell", markersize=10)
    axs[0, 0].set_ylabel("Price")
    axs[0, 0].set_title(f"{lower_bound} - {upper_bound} RSI Trading Strategy")
    axs[0, 0].grid()
    axs[0, 0].legend()

    axs[0, 1].plot(df_plot["StrategyReturns"], label="Strategy", color='blue')
    axs[0, 1].plot(df_plot["Benchmark"], label="Buy & Hold", color='grey')
    axs[0, 1].set_ylabel("Cumulative Returns")
    axs[0, 1].set_title("Strategy vs Benchmark")
    axs[0, 1].grid()
    axs[0, 1].legend()

    axs[1, 0].plot(df_plot["RSI"], label="RSI", color='purple')
    axs[1, 0].axhline(upper_bound, color='red', linestyle='--', label='Upper Bound')
    axs[1, 0].axhline(lower_bound, color='green', linestyle='--', label='Lower Bound')
    axs[1, 0].axhline(upper_bound - exit_threshold, color='grey', linestyle='--', label='Short Exit Bound')
    axs[1, 0].axhline(lower_bound + exit_threshold, color='grey', linestyle='--', label='Long Exit Bound')
    axs[1, 0].set_ylabel("RSI")
    axs[1, 0].set_title("RSI Indicator")
    axs[1, 0].grid()
    axs[1, 0].legend()

    axs[1, 1].plot(df_plot["Position"], label='Position', color='blue')
    axs[1, 1].set_title('Position')
    axs[1, 1].legend()
    axs[1, 1].grid()

    plt.tight_layout()
    return fig