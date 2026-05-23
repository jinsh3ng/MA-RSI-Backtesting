import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from utils import load_price_data, detect_trades, evaluate_strategy_performance


def generate_MAcrossover_signals(df, long_ma, short_ma):
    df_signal = df.copy()
    df_signal[f"MA{short_ma}"] = df_signal["Close"].rolling(short_ma).mean()
    df_signal[f"MA{long_ma}"] = df_signal["Close"].rolling(long_ma).mean()
    df_signal["Signal"] = np.where(df_signal[f"MA{short_ma}"] > df_signal[f"MA{long_ma}"], 1, -1)
    df_signal.dropna(subset=[f"MA{long_ma}"], inplace=True)
    df_signal.reset_index(inplace=True, drop=True)
    return df_signal


def run_moving_average_strategy(ticker, start_date, end_date, short_ma, long_ma):
    df = load_price_data(ticker, start_date, end_date)
    df_trade = generate_MAcrossover_signals(df, long_ma, short_ma)

    df_trade["Position"] = df_trade["Signal"].shift().fillna(0)
    df_trade["Trade"] = df_trade["Position"].diff().fillna(0)
    df_trade["Returns"] = df_trade["Close"].pct_change().fillna(0)
    df_trade["StrategyReturns"] = ((df_trade["Returns"] * df_trade["Position"]) + 1).cumprod().bfill()
    df_trade["Benchmark"] = df_trade["Close"] / df_trade["Close"].iloc[0]

    return df_trade


def plot_strategy(df, short_ma, long_ma):
    df_plot = df.copy()
    fig, axs = plt.subplots(1, 2, figsize=(15, 6))

    buy_signals, sell_signals = detect_trades(df_plot)

    axs[0].plot(df_plot["Close"], label="Close", color='grey')
    axs[0].plot(buy_signals["Close"], "^", markersize=10, color="green", label='Buy')
    axs[0].plot(sell_signals["Close"], "v", markersize=10, color="red", label='Sell')
    axs[0].plot(df_plot.index, df_plot[f"MA{short_ma}"], color="blue", label=f"MA{short_ma}")
    axs[0].plot(df_plot.index, df_plot[f"MA{long_ma}"], color="purple", label=f"MA{long_ma}")
    axs[0].set_ylabel("Price")
    axs[0].set_title(f"Moving Average Crossover Strategy between MA{short_ma} and MA{long_ma}")
    axs[0].grid()
    axs[0].legend()

    axs[1].plot(df_plot["StrategyReturns"], label="Strategy Performance", color='blue')
    axs[1].plot(df_plot["Benchmark"], label="Buy Hold Performance", color="grey")
    axs[1].set_ylabel("Price")
    axs[1].set_title("Compare Strategy against Long Only")
    axs[1].grid()
    axs[1].legend()

    plt.tight_layout()
    return fig


def grid_search_optimal_ma(ticker, start, end, metric):
    short_ma_options = [3, 5, 7, 10, 15, 20, 25, 30]
    long_ma_options = [30, 40, 50, 60, 70, 80, 90, 100, 120, 150, 200]

    best_metric_value = None
    best_params = None

    metric_index = {
        "Total Return": 0,
        "Sharpe Ratio": 1,
        "Information Ratio": 4,
        "Drawdown": 3,
    }
    idx = metric_index.get(metric)
    if idx is None:
        raise ValueError(f"Unknown metric: {metric}")

    for short_ma in short_ma_options:
        for long_ma in long_ma_options:
            if short_ma >= long_ma:
                continue

            df_result = run_moving_average_strategy(ticker, start, end, short_ma, long_ma)
            perf = evaluate_strategy_performance(df_result)
            current = perf[idx]

            # Higher is better for all (drawdown: less negative = better)
            if best_metric_value is None or current > best_metric_value:
                best_metric_value = current
                best_params = (short_ma, long_ma)

    return best_params, best_metric_value