# 📈 MA-RSI Backtesting Strategy
<table>
  <tr>
    <td></td>
    <td>
      <p align="center">
        <img src="https://github.com/user-attachments/assets/272973ce-8922-4895-91d1-d19c66708a32" width="70%" />
      </p>
      <p align="center">
        <img src="https://github.com/user-attachments/assets/34641feb-c069-4ed7-9aef-1e1c1d7fcf1c" width="70%" />
      </p>
    </td>
  </tr>
</table>

## 📘 Strategy Overview

This app lets you backtest and evaluate two widely used trading strategies — each with its own signal logic and customization options.

### 📊 Moving Average Strategy

- **Buy Signal:** When short-term MA crosses **above** long-term MA (bullish crossover)  
- **Sell Signal:** When short-term MA crosses **below** long-term MA (bearish crossover)  
- Supports **performance optimization**

### 💡 RSI Strategy (Relative Strength Index)

- **Buy Signal:** RSI falls **below lower threshold** (e.g., 30 — oversold)  
- **Sell Signal:** RSI rises **above upper threshold** (e.g., 70 — overbought)  
- Includes an **exit buffer** for earlier exits at moderate RSI levels  

## ⚙️ Setup Instructions

1. In the /MA-RSI-Backtesting directory, create a Python virtual environment and activate it:

   ```bash
   python -m venv .venv
   .venv\Scripts\activate # The .venv activation command might differ depending on your operating system

2. Install the required packages

   ```bash
   pip install -r requirements.txt


3. In the same directory(/MA-RSI-Backtesting), start the application
   
   ```bash
   streamlit run app.py  


