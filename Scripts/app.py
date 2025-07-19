import streamlit as st
from streamlit_option_menu import option_menu
from moving_average_app import run_ma_app
from moving_RSI import run_rsi_app

# Top navbar
selected = option_menu(
    menu_title=None,
    options=["Main", "Moving Average", "RSI"],
    icons=["house", "graph-up", "activity"],
    menu_icon="cast",  
    orientation="horizontal"
)

if selected == "Main":
    st.title("🏠 Main Dashboard")
    st.write("Welcome to my dashboard!")

    st.markdown("""
    This app allows you to run two trading strategies — **Moving Average** and **RSI** — and customize their parameters to analyze performance.

    ---

    ### 📈 Moving Average Strategy  
    This strategy is based on two moving averages: a short-term and a long-term one.  
    - A **buy signal** is triggered when the short-term moving average crosses **above** the long-term moving average (bullish crossover).  
    - A **sell signal** is triggered when the short-term moving average crosses **below** the long-term moving average (bearish crossover).  
    - Toward the end of the app, you can also choose to **optimize performance metrics** of your choice (e.g., Sharpe Ratio or Total Return).

    ---

    ### 💡 RSI Strategy (Relative Strength Index)  
    The RSI strategy identifies **overbought** and **oversold** conditions in the market.  
    - A **buy signal** is generated when the RSI falls **below a lower threshold** (e.g., 30), suggesting the asset is oversold.  
    - A **sell signal** is triggered when the RSI rises **above an upper threshold** (e.g., 70), suggesting the asset is overbought.  
    - This strategy also includes an **exit buffer**, allowing you to exit trades earlier at more moderate RSI levels. 

    ---
    """)
    st.markdown("Developed by **jinsh3ng**")



elif selected == "Moving Average":
    st.title("📉 Moving Average Strategy")
    run_ma_app()

elif selected == "RSI":
    st.title("📊 RSI Trading Strategy")
    run_rsi_app()
