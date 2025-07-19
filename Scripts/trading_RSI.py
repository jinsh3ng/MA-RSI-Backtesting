import yfinance as yf
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

def load_price_data(ticker, start_date, end_date):
    data = yf.download(ticker, start=start_date, end=end_date)
    data.reset_index(inplace=True)
    return data

def run_RSI_strategy(df, period, upper_bound, lower_bound, exit):
    short_exit_bounds = upper_bound - exit
    long_exit_bounds = lower_bound + exit
    df_signals = df.copy()
    df_signals["Returns"] = df_signals["Close"].pct_change().fillna(0)
    gains = df_signals["Returns"] * (df_signals["Returns"]>0)
    losses = np.abs(df_signals["Returns"] * (df_signals["Returns"]<0))
    RS = (
        gains.rolling(window=period).mean()
        /losses.rolling(window=period).mean()
    )
    
    df_signals["RSI"] = 100-(100/(1+RS))
    df_signals.dropna(subset=[("RSI","")], inplace=True)
    df_signals.reset_index(inplace=True, drop=True)
    df_signals["Signal"] = 0
    current_position = 0  # 1 = Long, -1 = Short, 0 = Neutral

    for i in range(len(df_signals)):
        rsi = df_signals.loc[i, ("RSI","")]
        if current_position == 0:
            if rsi < lower_bound:
                current_position = 1  #enter long
            elif rsi > upper_bound:
                current_position = -1  #enter short

        elif current_position == 1:  # if currently long
            if rsi > long_exit_bounds:
                current_position = 0  # exit long

        elif current_position == -1:  # if currently short
            if rsi < short_exit_bounds:
                current_position = 0  # exit short
        df_signals.loc[i, "Signal"] = current_position
        df_signals["Position"] = df_signals["Signal"].shift().bfill()
        df_signals["Trade"] = df_signals["Position"].diff().fillna(0)
        df_signals["StrategyReturns"] = (1+(df_signals["Position"] * df_signals["Returns"])).cumprod()
        df_signals.loc[0, "StrategyReturns"] = 1
    df_signals["Benchmark"] = df_signals["Close"] / df_signals["Close"].iloc[0]


    return df_signals

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

def plot_strategy(df, upper_bound, lower_bound, exit):
    df_plot = df.copy()
    fig, axs = plt.subplots(2, 2, figsize=(15, 10))  

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
    axs[1, 0].axhline(upper_bound - exit, color='grey', linestyle='--', label='Short Exit Bound')
    axs[1, 0].axhline(lower_bound + exit, color='grey', linestyle='--', label='Long Exit Bound')
    axs[1, 0].set_ylabel("RSI")
    axs[1, 0].set_title("RSI Indicator")
    axs[1, 0].grid()
    axs[1, 0].legend()

    axs[1, 1].plot(df_plot["Position"], label='Position', color='blue')
    axs[1, 1].set_title('Position')
    axs[1, 1].legend()
    axs[1, 1].grid()

    plt.tight_layout()
    plt.show()
    return fig

