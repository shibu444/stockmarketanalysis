import yfinance as yf
import pandas as pd
import plotly.graph_objects as go
import streamlit as st
from datetime import datetime, timedelta

# Function to get stock data
def get_stock_data(ticker, start_date, end_date):
    stock_data = yf.download(ticker, start=start_date, end=end_date)
    return stock_data

# Function to calculate technical indicators (without using talib)
def add_technical_indicators(df):
    # Calculate Simple Moving Averages
    df['SMA50'] = df['Close'].rolling(window=50).mean()
    df['SMA100'] = df['Close'].rolling(window=100).mean()

    # Calculate Relative Strength Index (RSI)
    delta = df['Close'].diff(1)
    gain = delta.where(delta > 0, 0)
    loss = -delta.where(delta < 0, 0)

    avg_gain = gain.rolling(window=14).mean()
    avg_loss = loss.rolling(window=14).mean()

    rs = avg_gain / avg_loss
    df['RSI'] = 100 - (100 / (1 + rs))

    return df

# Function to calculate returns and standard deviation
def calculate_statistics(df):
    # Calculate daily returns
    df['Daily Return'] = df['Close'].pct_change()

    # Get the last 90 days of data
    df_90 = df[-90:]
    avg_return = df_90['Daily Return'].mean()
    std_dev = df_90['Daily Return'].std()

    return avg_return, std_dev

# Function to plot the candlestick chart with SMA and RSI
def plot_candlestick_chart(df):
    fig = go.Figure(data=[go.Candlestick(x=df.index,
                                        open=df['Open'],
                                        high=df['High'],
                                        low=df['Low'],
                                        close=df['Close'],
                                        name="Candlestick")])

    # Add SMA50 and SMA100
    fig.add_trace(go.Scatter(x=df.index, y=df['SMA50'], mode='lines', name='SMA 50', line=dict(color='blue')))
    fig.add_trace(go.Scatter(x=df.index, y=df['SMA100'], mode='lines', name='SMA 100', line=dict(color='orange')))
    
    fig.update_layout(title="Candlestick Chart with SMA50 and SMA100",
                      xaxis_title="Date",
                      yaxis_title="Price",
                      template="plotly_dark")
    return fig

def plot_rsi(df):
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=df.index, y=df['RSI'], mode='lines', name='RSI', line=dict(color='green')))
    fig.add_hline(y=70, line=dict(color='red', dash='dash'), annotation_text="Overbought", annotation_position="top left")
    fig.add_hline(y=30, line=dict(color='blue', dash='dash'), annotation_text="Oversold", annotation_position="bottom left")

    fig.update_layout(title="RSI Chart", xaxis_title="Date", yaxis_title="RSI", template="plotly_dark")
    return fig

# Streamlit UI
st.title("Stock Price Data with Technical Indicators")

# Input ticker symbol
ticker = st.text_input("Enter Stock Ticker Symbol", "AAPL")

# Date range for data
end_date = datetime.today().strftime('%Y-%m-%d')
start_date = (datetime.today() - timedelta(days=30)).strftime('%Y-%m-%d')

start_date_input = st.date_input("Start Date", datetime.today() - timedelta(days=30))
end_date_input = st.date_input("End Date", datetime.today())

start_date = start_date_input.strftime('%Y-%m-%d')
end_date = end_date_input.strftime('%Y-%m-%d')

# Get stock data
df = get_stock_data(ticker, start_date, end_date)

if not df.empty:
    # Add technical indicators
    df = add_technical_indicators(df)

    # Plot the candlestick chart with SMAs
    st.plotly_chart(plot_candlestick_chart(df))

    # Plot the RSI chart
    st.plotly_chart(plot_rsi(df))

    # Calculate returns and standard deviation for the last 90 days
    avg_return, std_dev = calculate_statistics(df)

    # Display statistics in a table
    st.subheader("90-Day Average Return and Standard Deviation")
    stats_data = {
        "Average Return": [avg_return],
        "Standard Deviation": [std_dev]
    }
    stats_df = pd.DataFrame(stats_data)
    st.write(stats_df)

else:
    st.error("No data found for this ticker symbol.")
