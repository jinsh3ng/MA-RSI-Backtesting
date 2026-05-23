# 📈 MA-RSI Backtesting Strategy

<table>
  <tr>
    <td>
      <img src="https://github.com/user-attachments/assets/5e24156b-97ec-47b3-9534-659a069045cc" width="100%" />
    </td>
    <td>
      <img src="https://github.com/user-attachments/assets/e1c69907-bf41-495c-8c25-3fc6d473f39a" width="100%" /><br />
      <img src="https://github.com/user-attachments/assets/8fbb47c1-2dee-4a5d-b192-2cba258505c1" width="100%" />
    </td>
  </tr>
</table>

## 💡 Why I Built This

I used to backtest trading strategies manually — scrolling through charts, eyeballing crossovers, jotting down entry and exit points on a spreadsheet, and calculating returns by hand. It was tedious, error-prone, and painfully slow. Every time I wanted to tweak a parameter (what if I used a 20-day MA instead of 10?), I had to redo the entire process from scratch.

This project automates all of that. Instead of spending hours on a single backtest, I can now run a strategy in seconds, adjust parameters on the fly, and instantly see performance metrics and visualizations. What used to take an afternoon of squinting at candlestick charts now takes a single button click.

## 📖 What It Does

A Streamlit-based backtesting application that lets you test two classic trading strategies against historical stock data, with configurable parameters and real-time performance evaluation.

### 📈 Moving Average Crossover Strategy

Uses two moving averages — a short-term and a long-term — to generate trading signals:

- **Buy** when the short MA crosses above the long MA (bullish crossover)
- **Sell** when the short MA crosses below the long MA (bearish crossover)
- Includes a **grid search optimizer** that tests all combinations of short/long MA windows to find the best parameters for a chosen metric (Sharpe Ratio, Total Return, Information Ratio, or Drawdown)

### 💡 RSI Strategy (Relative Strength Index)

Identifies overbought and oversold conditions to time entries and exits:

- **Buy** when RSI drops below the lower threshold (e.g., 30), signaling an oversold asset
- **Sell** when RSI rises above the upper threshold (e.g., 70), signaling an overbought asset
- Configurable **exit buffer** to close positions at more moderate RSI levels rather than waiting for a full reversal

### 📊 Performance Metrics

Both strategies are evaluated with:

- **Total Return** — overall strategy profit/loss
- **Sharpe Ratio** — risk-adjusted return
- **Annualized Volatility** — how much the strategy's returns fluctuate
- **Max Drawdown** — largest peak-to-trough decline
- **Information Ratio** — excess return relative to the benchmark per unit of tracking error
- **Number of Trades** — total buy and sell signals generated

## ⚙️ Setup Instructions

1. Clone the repo and navigate to the project directory:

   ```bash
   git clone https://github.com/jinsh3ng/MA-RSI-Backtesting.git
   cd MA-RSI-Backtesting
   ```

2. Create and activate a Python virtual environment:

   ```bash
   python -m venv .venv

   # Windows
   .venv\Scripts\activate

   # macOS / Linux
   source .venv/bin/activate
   ```

3. Install the required packages:

   ```bash
   pip install -r requirements.txt
   ```

4. Run the application:

   ```bash
   streamlit run Scripts/app.py
   ```

## 🛠️ Tech Stack

- **Python** — core language
- **Streamlit** — web UI framework
- **yfinance** — historical stock data
- **pandas / numpy** — data manipulation and calculations
- **matplotlib** — strategy visualizations

## 📁 Project Structure

```
MA-RSI-Backtesting/
├── Scripts/
│   ├── app.py                    # Main Streamlit app with navigation
│   ├── utils.py                  # Shared utilities (data loading, metrics, trade detection)
│   ├── moving_average_app.py     # Moving Average strategy UI
│   ├── moving_RSI.py             # RSI strategy UI
│   ├── trading_moving_average.py # Moving Average strategy logic
│   └── trading_RSI.py            # RSI strategy logic
├── requirements.txt              # Python dependencies
└── README.md
```

## 🚧 Roadmap

- [ ] Add transaction costs and slippage modeling
- [ ] Interactive Plotly charts (zoom, hover, pan)
- [ ] Strategy comparison view (MA vs RSI side by side)
- [ ] Parameter sensitivity heatmaps
- [ ] Export trade log and results to CSV
- [ ] Bollinger Bands strategy

---

Developed by **jinsh3ng**