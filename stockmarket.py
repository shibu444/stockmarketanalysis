import streamlit as st
import yfinance as yf
import plotly.graph_objs as go
import pandas as pd
import numpy as np
import talib

# Set the title of the app
st.title('Stock Analysis with Candlestick Chart and Technical Indicators')

# Text input for ticker
ticker = st.text_input('Enter Stock Ticker', 'AAPL')

# Date range selection
start_date = st.date_input('Start Date', pd.to_datetime('2023-12-01'))
end_date = st.date_input('End Date', pd.to_datetime('2025-01-01'))

# Fetch data from Yahoo Finance
data = yf.download(ticker, start=start_date, end=end_date)

# Calculate SMA 50 and SMA 100
data['SMA50'] = data['Close'].rolling(window=50).mean()
data['SMA100'] = data['Close'].rolling(window=100).mean()

# Calculate RSI (14-period)
rsi = ta.momentum.RSIIndicator(data['Close'], window=14)
data['RSI'] = rsi.rsi()

# Candlestick chart with SMA lines
fig = go.Figure()

# Add Candlestick chart
fig.add_trace(go.Candlestick(x=data.index,
                             open=data['Open'],
                             high=data['High'],
                             low=data['Low'],
                             close=data['Close'],
                             name='Candlesticks'))

# Add SMA 50
fig.add_trace(go.Scatter(x=data.index, y=data['SMA50'], mode='lines', name='SMA 50', line={'color': 'blue'}))

# Add SMA 100
fig.add_trace(go.Scatter(x=data.index, y=data['SMA100'], mode='lines', name='SMA 100', line={'color': 'orange'}))

# Update layout for the candlestick chart
fig.update_layout(title=f'{ticker} Candlestick Chart with SMA 50 and SMA 100',
                  xaxis_title='Date',
                  yaxis_title='Price',
                  template='plotly_dark')

# Display the candlestick chart
st.plotly_chart(fig)

# Calculate returns for last 90 days
data['Returns'] = data['Close'].pct_change()
last_90_days = data[-90:]

# Calculate average return and standard deviation of returns
avg_return = last_90_days['Returns'].mean()
std_return = last_90_days['Returns'].std()

# Display the table with average return and standard deviation
st.write(f"Average Return (Last 90 Days): {avg_return:.4f}")
st.write(f"Standard Deviation of Returns (Last 90 Days): {std_return:.4f}")

# Plot RSI chart
rsi_fig = go.Figure()

# Add RSI line
rsi_fig.add_trace(go.Scatter(x=data.index, y=data['RSI'], mode='lines', name='RSI', line={'color': 'green'}))

# Update layout for RSI chart
rsi_fig.update_layout(title=f'{ticker} RSI (14-period)',
                      xaxis_title='Date',
                      yaxis_title='RSI',
                      template='plotly_dark')

# Display the RSI chart
st.plotly_chart(rsi_fig)
