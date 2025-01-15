import streamlit as st
import yfinance as yf
import pandas as pd
import plotly.graph_objects as go
from datetime import datetime, timedelta

# Function to calculate RSI
def calculate_rsi(data, window):
    delta = data['Adj Close'].diff(1)
    gain = (delta.where(delta > 0, 0)).rolling(window=window).mean()
    loss = (-delta.where(delta < 0, 0)).rolling(window=window).mean()
    rs = gain / loss
    rsi = 100 - (100 / (1 + rs))
    return rsi

# Streamlit App
st.title('Stock Analysis App')
st.sidebar.header('User Input')

ticker = st.sidebar.text_input("Enter Stock Ticker:", "AAPL")
start_date = st.sidebar.date_input("Start Date:", datetime.now() - timedelta(days=365))
end_date = st.sidebar.date_input("End Date:", datetime.now())

if start_date > end_date:
    st.sidebar.error("End Date must fall after Start Date.")

if ticker:
    # Download stock data
    stock_data = yf.download(ticker, start=start_date, end=end_date)

    if not stock_data.empty:
        # Add SMA 50 and SMA 100
        stock_data['SMA_50'] = stock_data['Adj Close'].rolling(window=50).mean()
        stock_data['SMA_100'] = stock_data['Adj Close'].rolling(window=100).mean()

        # Calculate RSI
        stock_data['RSI'] = calculate_rsi(stock_data, 14)

        # Filter data for the last 30 days for candlestick chart
        last_30_days = stock_data[-30:]

        # Create candlestick chart
        fig = go.Figure()
        fig.add_trace(go.Candlestick(x=last_30_days.index,
                                      open=last_30_days['Open'],
                                      high=last_30_days['High'],
                                      low=last_30_days['Low'],
                                      close=last_30_days['Adj Close'],
                                      name='Candlesticks'))
        fig.add_trace(go.Scatter(x=last_30_days.index, y=last_30_days['SMA_50'],
                                 mode='lines', name='SMA 50'))
        fig.add_trace(go.Scatter(x=last_30_days.index, y=last_30_days['SMA_100'],
                                 mode='lines', name='SMA 100'))
        fig.update_layout(title=f'{ticker} Candlestick Chart with SMA', xaxis_title='Date', yaxis_title='Price')

        st.plotly_chart(fig)

        # RSI Chart
        st.subheader('RSI (Relative Strength Index)')
        rsi_fig = go.Figure()
        rsi_fig.add_trace(go.Scatter(x=stock_data.index, y=stock_data['RSI'],
                                      mode='lines', name='RSI'))
        rsi_fig.add_hline(y=70, line_dash="dot", line_color="red", annotation_text="Overbought", annotation_position="top left")
        rsi_fig.add_hline(y=30, line_dash="dot", line_color="green", annotation_text="Oversold", annotation_position="bottom left")
        rsi_fig.update_layout(title='RSI Chart', xaxis_title='Date', yaxis_title='RSI')

        st.plotly_chart(rsi_fig)

        # Calculate returns
        stock_data['Daily Return'] = stock_data['Adj Close'].pct_change()
        last_90_days = stock_data[-90:]
        avg_return = last_90_days['Daily Return'].mean()
        std_dev_return = last_90_days['Daily Return'].std()

        # Display average return and standard deviation
        st.subheader('Performance Metrics (Last 90 Days)')
        metrics = pd.DataFrame({
            'Metric': ['Average Return', 'Standard Deviation'],
            'Value': [avg_return, std_dev_return]
        })
        st.table(metrics)

        # Buy/Sell Decision
        st.subheader('Buy/Sell Decision')
        current_rsi = stock_data['RSI'].iloc[-1]
        if current_rsi > 70:
            st.write("**Decision:** Sell (Overbought)")
        elif current_rsi < 30:
            st.write("**Decision:** Buy (Oversold)")
        else:
            st.write("**Decision:** Hold")

    else:
        st.error("No data found for the given ticker symbol.")
else:
    st.info("Please enter a stock ticker symbol.")
