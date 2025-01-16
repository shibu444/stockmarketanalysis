import streamlit as st
import yfinance as yf
import plotly.graph_objs as go
import pandas as pd
import numpy as np
from ta.momentum import RSIIndicator

# Streamlit app title
st.title('Stock Analysis App')

# Input for stock ticker
ticker = st.text_input('Enter Stock Ticker', 'AAPL')

# Date range selection
start_date = st.date_input('Start Date', pd.to_datetime('2024-01-01'))
end_date = st.date_input('End Date', pd.to_datetime('2025-01-01'))

# Fetch stock data from Yahoo Finance
try:
    data = yf.download(ticker, start=start_date, end=end_date)
except Exception as e:
    st.error(f"Error fetching data for ticker {ticker}: {e}")
    data = pd.DataFrame()

# Ensure data is available
if not data.empty:
    # Calculate SMA 50 and SMA 100
    data['SMA50'] = data['Close'].rolling(window=50).mean()
    data['SMA100'] = data['Close'].rolling(window=100).mean()

    # Calculate RSI (14-period)
    try:
        rsi_indicator = RSIIndicator(data['Close'], window=14)
        data['RSI'] = rsi_indicator.rsi()  # Correctly assign RSI to the DataFrame
    except Exception as e:
        st.error(f"Error calculating RSI: {e}")
        data['RSI'] = np.nan

    # Limit data to the last 30 days for the candlestick chart
    last_30_days = data.tail(30)

    # Create the candlestick chart with SMA lines
    fig = go.Figure()

    # Add candlestick trace
    fig.add_trace(go.Candlestick(x=last_30_days.index,
                                 open=last_30_days['Open'],
                                 high=last_30_days['High'],
                                 low=last_30_days['Low'],
                                 close=last_30_days['Close'],
                                 name='Candlesticks'))

    # Add SMA 50 and SMA 100 lines
    fig.add_trace(go.Scatter(x=last_30_days.index, y=last_30_days['SMA50'],
                             mode='lines', name='SMA 50', line=dict(color='blue')))
    fig.add_trace(go.Scatter(x=last_30_days.index, y=last_30_days['SMA100'],
                             mode='lines', name='SMA 100', line=dict(color='orange')))

    # Update chart layout
    fig.update_layout(title=f'{ticker} Candlestick Chart with SMA 50 and SMA 100',
                      xaxis_title='Date',
                      yaxis_title='Price',
                      template='plotly_dark')

    # Display candlestick chart
    st.plotly_chart(fig)

    # Calculate returns for the last 90 days
    data['Returns'] = data['Close'].pct_change()
    last_90_days = data.tail(90)

    # Calculate average return and standard deviation
    avg_return = last_90_days['Returns'].mean()
    std_return = last_90_days['Returns'].std()

    # Display average return and standard deviation
    st.subheader('Return Statistics (Last 90 Days)')
    st.write(f"**Average Return**: {avg_return:.4%}")
    st.write(f"**Standard Deviation of Returns**: {std_return:.4%}")

    # Create RSI chart
    rsi_fig = go.Figure()

    # Add RSI line
    rsi_fig.add_trace(go.Scatter(x=data.index, y=data['RSI'], mode='lines',
                                 name='RSI', line=dict(color='green')))

    # Add horizontal lines for RSI thresholds
    rsi_fig.add_hline(y=70, line=dict(color='red', dash='dot'), name='Overbought')
    rsi_fig.add_hline(y=30, line=dict(color='blue', dash='dot'), name='Oversold')

    # Update RSI chart layout
    rsi_fig.update_layout(title=f'{ticker} RSI (14-Period)',
                          xaxis_title='Date',
                          yaxis_title='RSI',
                          template='plotly_dark')

    # Display RSI chart
    st.plotly_chart(rsi_fig)
else:
    st.warning("No data available for the selected ticker and date range.")
