import streamlit as st
from trading import *
from datetime import date

st.write("## Moving Average Strategy")

ticker = st.text_input("Enter ticker symbol")

col1, col2 = st.columns(2)
with col1:
    start = st.date_input("Start date", value=date.today())
with col2:
    end = st.date_input("End date", value=date.today())

short_ma_options = [3, 5, 7, 10, 15, 20, 25, 30]
long_ma_options = [30, 40, 50, 60, 70, 80, 90, 100, 120, 150, 200]

col3, col4 = st.columns(2)
with col3:
    short_ma = st.selectbox("Short MA window", options=short_ma_options, index=3)  
with col4:
    long_ma = st.selectbox("Long MA window", options=long_ma_options, index=2) 

if not ticker:
    st.warning("⚠️ Please enter a ticker symbol.")
elif start > end:
    st.warning("⚠️ Start date must be before or equal to End date.")
elif short_ma >= long_ma:
    st.warning("⚠️ Short MA must be less than Long MA.")
else:
    if st.button("Run Analysis"):
        start_str = start.strftime("%Y-%m-%d")
        end_str = end.strftime("%Y-%m-%d")
        df_result = run_moving_average_strategy(ticker, start_str, end_str, short_ma, long_ma)
        total_return,sharpe_ratio, annualized_vol, max_drawdown,information_ratio,num_trades = evaluate_strategy_performance(df_result)
        st.write("---")
        fig = plot_strategy(df_result, short_ma, long_ma)
        st.pyplot(fig)
        a, b, c = st.columns(3)
        d, e, f = st.columns(3)
        st.markdown("### Strategy Performance Results")
        col1, col2, col3 = st.columns(3)
        col1.metric("Total Return", f"{round((total_return - 1) * 100, 2)}%", border=True)
        col2.metric("Sharpe Ratio", f"{round(sharpe_ratio, 2)}", border=True)
        col3.metric("Max Drawdown", f"{round(max_drawdown * 100, 2)}%", border=True)

        col4, col5, col6 = st.columns(3)
        col4.metric("Information Ratio", f"{round(information_ratio, 2)}", border=True)
        col5.metric("Annualized Volatility", f"{round(annualized_vol * 100, 2)}%", border=True)
        col6.metric("Number of Trades", str(num_trades), border=True)


