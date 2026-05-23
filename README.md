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

## Overview

Before I entered university, I used to backtest trading strategies manually on TradingView — scrolling through charts, eyeballing price movements, recording entries and exits in a spreadsheet. It was tedious, error-prone, and painfully slow. Every time I wanted to tweak a part of my strategy, I had to redo the entire process from scratch.
 
This project demonstrates how that manual workflow can be fully automated. I tested it on simple algorithms like Moving Average Crossover and RSI. What used to take an afternoon of squinting at candlestick charts now takes a single button click — run a strategy in seconds, adjust parameters on the fly, and instantly see performance metrics and visualizations.
 
> [!NOTE]
> This project is my initiative to automate something driven by curiosity. It’s nothing groundbreaking, but more of a practical idea I wanted to explore and build out. The analytics and visualizations are displayed through a Streamlit frontend, making it easy to interact with the strategies and review performance quickly.

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

---

Developed by **jinsh3ng**
