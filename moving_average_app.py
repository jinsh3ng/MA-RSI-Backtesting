import streamlit as st
from trading_moving_average import *
from datetime import date

def run_ma_app():

    ticker = st.text_input("Enter ticker symbol", key="ticker_input")

    col1, col2 = st.columns(2)
    with col1:
        start = st.date_input("Start date", value=date(2023, 1, 1), key="start_date")
    with col2:
        end = st.date_input("End date", value=date.today(), key="end_date")

    short_ma_options = [3, 5, 7, 10, 15, 20, 25, 30]
    long_ma_options = [30, 40, 50, 60, 70, 80, 90, 100, 120, 150, 200]

    col3, col4 = st.columns(2)
    with col3:
        short_ma = st.selectbox("Short MA window", options=short_ma_options, index=3, key="short_ma")
    with col4:
        long_ma = st.selectbox("Long MA window", options=long_ma_options, index=2, key="long_ma")

    # Initialize session state variables
    if 'start_str' not in st.session_state:
        st.session_state.start_str = None
    if 'end_str' not in st.session_state:
        st.session_state.end_str = None
    if 'df_result' not in st.session_state:
        st.session_state.df_result = None
    if 'metrics' not in st.session_state:
        st.session_state.metrics = None
    if 'optimize_submitted' not in st.session_state:
        st.session_state.optimize_submitted = False
    if 'best_params' not in st.session_state:
        st.session_state.best_params = None
    if 'best_metric_value' not in st.session_state:
        st.session_state.best_metric_value = None

    if not ticker:
        st.warning("⚠️ Please enter a ticker symbol.")
    elif start > end:
        st.warning("⚠️ Start date must be before or equal to End date.")
    elif short_ma >= long_ma:
        st.warning("⚠️ Short MA must be less than Long MA.")
    else:
        if st.button("Run Analysis"):
            st.session_state.start_str = start.strftime("%Y-%m-%d")
            st.session_state.end_str = end.strftime("%Y-%m-%d")

            df_result = run_moving_average_strategy(ticker, st.session_state.start_str, st.session_state.end_str, short_ma, long_ma)
            total_return, sharpe_ratio, annualized_vol, max_drawdown, information_ratio, num_trades = evaluate_strategy_performance(df_result)

            st.session_state.df_result = df_result
            st.session_state.metrics = {
                "total_return": total_return,
                "sharpe_ratio": sharpe_ratio,
                "annualized_vol": annualized_vol,
                "max_drawdown": max_drawdown,
                "information_ratio": information_ratio,
                "num_trades": num_trades
            }
            st.session_state.optimize_submitted = False 

        if st.session_state.df_result is not None:
            fig = plot_strategy(st.session_state.df_result, short_ma, long_ma)
            st.pyplot(fig)

            st.markdown("### Strategy Performance Results")
            col1, col2, col3 = st.columns(3)
            col1.metric("Total Return", f"{round((st.session_state.metrics['total_return']) * 100, 2)}%")
            col2.metric("Sharpe Ratio", f"{round(st.session_state.metrics['sharpe_ratio'], 2)}")
            col3.metric("Max Drawdown", f"{round(st.session_state.metrics['max_drawdown'] * 100, 2)}%")

            col4, col5, col6 = st.columns(3)
            col4.metric("Information Ratio", f"{round(st.session_state.metrics['information_ratio'], 2)}")
            col5.metric("Annualized Volatility", f"{round(st.session_state.metrics['annualized_vol'] * 100, 2)}%")
            col6.metric("Number of Trades", str(st.session_state.metrics['num_trades']))

            st.write("---")

            optimize_metric = st.selectbox(
                "Select metric to optimize",
                options=["Total Return", "Sharpe Ratio", "Information Ratio", "Drawdown"],
                key="optimize_metric"
            )

            with st.form("optimize_form"):
                submitted = st.form_submit_button("Run Optimization")

            if submitted:
                if st.session_state.start_str is None or st.session_state.end_str is None:
                    st.error("Please run analysis first by clicking 'Run Analysis'.")
                else:
                    with st.spinner("Running optimization, please wait..."):
                        best_params, best_metric_value = grid_search_optimal_ma(
                            ticker,
                            st.session_state.start_str,
                            st.session_state.end_str,
                            optimize_metric
                        )
                    st.session_state.best_params = best_params
                    st.session_state.best_metric_value = best_metric_value
                    st.session_state.optimize_submitted = True

            if st.session_state.optimize_submitted:
                st.success(f"Best MA params: Short MA = {st.session_state.best_params[0]}, Long MA = {st.session_state.best_params[1]}")
                st.info(f"Best {optimize_metric}: {round(st.session_state.best_metric_value, 4)}")
