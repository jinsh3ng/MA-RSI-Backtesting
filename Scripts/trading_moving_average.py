import yfinance as yf
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import numpy as np

def load_price_data(ticker, start_date, end_date):
    data = yf.download(ticker, start=start_date, end=end_date)
    data.reset_index(inplace=True)
    return data

def generate_MAcrossover_signals(df, long_ma, short_ma):
    df_signal = df.copy()
    df_signal[f"MA{short_ma}"] = df_signal["Close"].rolling(short_ma).mean()
    df_signal[f"MA{long_ma}"] = df_signal["Close"].rolling(long_ma).mean()
    df_signal["Signal"] = np.where(df_signal[f"MA{short_ma}"] > df_signal[f"MA{long_ma}"], 1, -1)
    df_signal.dropna(subset=[(f"MA{long_ma}","")], inplace=True)
    df_signal.reset_index(inplace=True, drop=True)
    return df_signal

def run_moving_average_strategy(ticker, start_date, end_date, short_ma, long_ma):
    df = load_price_data(ticker, start_date, end_date)
    df_trade = generate_MAcrossover_signals(df, long_ma, short_ma)

    df_trade["Position"] = df_trade["Signal"].shift().fillna(0)

    df_trade["Trade"] = df_trade["Position"].diff().fillna(0)

    df_trade["Returns"] = df_trade["Close"].pct_change().fillna(0)

    df_trade["StrategyReturns"] = ((df_trade["Returns"] * df_trade["Position"])+1).cumprod().bfill()

    df_trade["Benchmark"] = df_trade["Close"] / df_trade["Close"].iloc[0]

    return df_trade

def evaluate_strategy_performance(df):
    df_results = df.copy()
    strategy_returns = df['StrategyReturns'].pct_change().dropna()

    #Total Return
    total_return = (df_results["StrategyReturns"].iloc[-1]/df_results["StrategyReturns"].iloc[0])-1

    #Sharpe Ratio
    sharpe_ratio = ((strategy_returns.mean()) / (strategy_returns.std()))*np.sqrt(252)
    
    #Annualized Vol
    annualized_vol = strategy_returns.std() * np.sqrt(252)

    #Max Drawdown
    df_results["StrategyReturnsMax"] = df_results["StrategyReturns"].cummax()
    df_results["Drawdown"] = (df_results["StrategyReturns"] - df_results["StrategyReturnsMax"]) / df_results["StrategyReturns"]
    max_drawdown = df_results["Drawdown"].min()
    
    #Information Ratio
    mean_active_returns = (strategy_returns - df_results["Returns"]).mean()
    tracking_error = (strategy_returns - df_results["Returns"]).std()
    information_ratio = mean_active_returns/tracking_error

    #Number of Trades
    buy_signals = df_results[
        (
            ((df_results["Trade"] == 2) & (df_results["Trade"].shift(1) == 0))
            |
            ((df_results["Trade"] == 1) & (df_results["Trade"].shift(1) == 0))
        )    
    ]
    sell_signals = df_results[
        (
            ((df_results["Trade"] == -2) & (df_results["Trade"].shift(1) == 0))
            | 
            ((df_results["Trade"] == -1) & (df_results["Trade"].shift(1) == 0))
        )
    ]
    num_trades = len(buy_signals)+len(sell_signals)
    
    return total_return, sharpe_ratio, annualized_vol, max_drawdown, information_ratio,num_trades

def plot_strategy(df, short_ma, long_ma):
    df_plot = df.copy()
    fig, axs = plt.subplots(1, 2, figsize=(15, 6))  # 1 row, 2 columns
    
    buy_signals = df_plot[
        (
            ((df_plot["Trade"] == 2) & (df_plot["Trade"].shift(1) == 0))
            | 
            ((df_plot["Trade"] == 1) & (df_plot["Trade"].shift(1) == 0))
        )
    ]
    sell_signals = df_plot[
        (
            ((df_plot["Trade"] == -2) & (df_plot["Trade"].shift(1) == 0))
            | 
            ((df_plot["Trade"] == -1) & (df_plot["Trade"].shift(1) == 0))
        )
    ]

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
    plt.show()
    return fig

def grid_search_optimal_ma(ticker, start, end, metric):
    short_ma_options = [3, 5, 7, 10, 15, 20, 25, 30]
    long_ma_options = [30, 40, 50, 60, 70, 80, 90, 100, 120, 150, 200]

    best_metric_value = None
    best_params = None
    best_df_result = None

    for short_ma in short_ma_options:
        for long_ma in long_ma_options:
            if short_ma >= long_ma:
                continue

            df_result = run_moving_average_strategy(ticker, start, end, short_ma, long_ma)

            total_return, sharpe_ratio, annualized_vol, max_drawdown, information_ratio, num_trades = evaluate_strategy_performance(df_result)

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
                current_metric = max_drawdown
                # For drawdown, smaller (more negative) is worse
                better = (best_metric_value is None) or (current_metric > best_metric_value)  
            else:
                raise ValueError(f"Unknown metric: {metric}")

            if better:
                best_metric_value = current_metric
                best_params = (short_ma, long_ma)

    return best_params, best_metric_value

