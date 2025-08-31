import streamlit as st
from trading_RSI import *
from datetime import date

def run_rsi_app():

    # Input field for ticker symbol
    ticker = st.text_input("Enter ticker symbol", key="ticker_input")

    # Date input columns for start and end dates
    col1, col2 = st.columns(2)
    with col1:
        start = st.date_input("Start date", value=date(2023, 1, 1), key="start_date")
    with col2:
        end = st.date_input("End date", value=date.today(), key="end_date")

    # Input fields for RSI parameters: period and exit threshold
    col3, col4 = st.columns(2)
    with col3:
        rsi_period = st.selectbox("RSI Period", options=[5, 10, 14, 21], index=2)
    with col4:
        exit = st.slider("Exit Threshold", min_value=1, max_value=30, value=10)

    # Input fields for RSI bounds (oversold and overbought levels)
    col5, col6 = st.columns(2)
    with col5:
        lower_bound = st.slider("RSI Lower Bound (Oversold)", min_value=5, max_value=50, value=30)
    with col6:
        upper_bound = st.slider("RSI Upper Bound (Overbought)", min_value=50, max_value=95, value=70)

    # Basic input validation with warnings for user feedback
    if not ticker:
        st.warning("⚠️ Please enter a ticker symbol.")
    elif start > end:
        st.warning("⚠️ Start date must be before or equal to End date.")
    elif lower_bound >= upper_bound:
        st.warning("⚠️ Lower bound must be less than upper bound.")
    else:
        # Run the RSI strategy when button is clicked and inputs are valid
        if st.button("Run RSI Strategy"):
            # Format dates as strings for data loading
            start_str = start.strftime("%Y-%m-%d")
            end_str = end.strftime("%Y-%m-%d")

            # Show spinner while running the strategy
            with st.spinner("Running strategy..."):
                # Load price data and run RSI strategy with user inputs
                df_result = run_RSI_strategy(
                    df=load_price_data(ticker, start_str, end_str),
                    period=rsi_period,
                    upper_bound=upper_bound,
                    lower_bound=lower_bound,
                    exit=exit
                )

                # Evaluate strategy performance metrics
                total_return, sharpe_ratio, annualized_vol, max_drawdown, information_ratio, num_trades = evaluate_strategy_performance(df_result)

            # Plot the strategy results (price, RSI, signals, returns)
            fig = plot_strategy(df_result, upper_bound, lower_bound, exit)
            st.pyplot(fig)

            # Display performance metrics in a grid layout
            st.markdown("### Strategy Performance Results")
            col1, col2, col3 = st.columns(3)
            col1.metric("Total Return", f"{round(total_return * 100, 2)}%")
            col2.metric("Sharpe Ratio", f"{round(sharpe_ratio, 2)}")
            col3.metric("Max Drawdown", f"{round(max_drawdown * 100, 2)}%")

            col4, col5, col6 = st.columns(3)
            col4.metric("Information Ratio", f"{round(information_ratio, 2)}")
            col5.metric("Annualized Volatility", f"{round(annualized_vol * 100, 2)}%")
            col6.metric("Number of Trades", str(num_trades))
