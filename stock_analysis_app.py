# stock_analysis_app.py

import yfinance as yf
import streamlit as st
import pandas as pd
from ta.momentum import RSIIndicator
from ta.trend import SMAIndicator
from ta.volatility import BollingerBands

# Set page configuration
st.set_page_config(
    page_title="Stock Analysis Tool",
    layout="wide",
    initial_sidebar_state="expanded",
)

# Title and description
st.title("📈 Stock Analysis Tool")
st.write("""
This tool provides quick insights into stocks based on their ticker symbols.
Enter a ticker symbol to retrieve basic information and analyze historical data.
""")

# Sidebar input
st.sidebar.header("Input Options")
ticker_symbol = st.sidebar.text_input("Enter Ticker Symbol", value="AAPL").upper()

# Fetch data when ticker symbol is provided
if ticker_symbol:
    try:
        # Fetch stock data
        stock = yf.Ticker(ticker_symbol)
        basic_info = stock.info
        historical_data = stock.history(period="1y")

        # Check if historical data is available
        if not historical_data.empty:
            # Display basic stock information
            st.header("🔍 Basic Information")
            col1, col2 = st.columns(2)
            with col1:
                st.write(f"**Company Name:** {basic_info.get('longName', 'N/A')}")
                st.write(f"**Sector:** {basic_info.get('sector', 'N/A')}")
                st.write(f"**Industry:** {basic_info.get('industry', 'N/A')}")
                st.write(f"**Market Cap:** {basic_info.get('marketCap', 'N/A')}")
            with col2:
                st.write(f"**P/E Ratio:** {basic_info.get('trailingPE', 'N/A')}")
                st.write(f"**Dividend Yield:** {basic_info.get('dividendYield', 'N/A')}")
                st.write(f"**52-Week High:** {basic_info.get('fiftyTwoWeekHigh', 'N/A')}")
                st.write(f"**52-Week Low:** {basic_info.get('fiftyTwoWeekLow', 'N/A')}")

            # Tooltips for basic info
            with st.expander("ℹ️ Basic Information Tooltips"):
                st.markdown("""
                - **Market Cap**: Indicates the company's total market value, helping assess its size.
                - **P/E Ratio**: A valuation metric comparing the stock price to its earnings; useful for comparing companies within the same industry.
                - **Dividend Yield**: Shows how much a company pays out in dividends each year relative to its stock price.
                """)

            # Calculate technical indicators
            st.header("📊 Technical Indicators")
            # Moving Averages
            historical_data['SMA50'] = SMAIndicator(historical_data['Close'], window=50).sma_indicator()
            historical_data['SMA200'] = SMAIndicator(historical_data['Close'], window=200).sma_indicator()
            # RSI
            historical_data['RSI'] = RSIIndicator(historical_data['Close'], window=14).rsi()
            # Bollinger Bands
            bb_indicator = BollingerBands(historical_data['Close'])
            historical_data['BB_High'] = bb_indicator.bollinger_hband()
            historical_data['BB_Low'] = bb_indicator.bollinger_lband()
            # Volatility
            historical_data['Volatility'] = historical_data['Close'].rolling(window=20).std()

            # Plotting price and moving averages
            st.subheader("Price Chart with Moving Averages")
            price_chart = st.line_chart(historical_data[['Close', 'SMA50', 'SMA200']])

            # Tooltips for moving averages
            with st.expander("ℹ️ Moving Averages Tooltip"):
                st.write("Moving averages smooth out price data to help identify trends and potential support or resistance levels.")

            # Plotting RSI
            st.subheader("Relative Strength Index (RSI)")
            rsi_chart = st.line_chart(historical_data['RSI'])

            # Tooltips for RSI
            with st.expander("ℹ️ RSI Tooltip"):
                st.write("RSI indicates overbought (>70) or oversold (<30) conditions, potentially signaling price reversals.")

            # Plotting Bollinger Bands
            st.subheader("Bollinger Bands")
            bb_chart = st.line_chart(historical_data[['Close', 'BB_High', 'BB_Low']])

            # Tooltips for Bollinger Bands
            with st.expander("ℹ️ Bollinger Bands Tooltip"):
                st.write("Bollinger Bands help identify volatility and overbought/oversold conditions.")

            # Display key insights
            st.header("💡 Key Insights")

            # Price Trend Analysis
            latest_close = historical_data['Close'][-1]
            sma50 = historical_data['SMA50'][-1]
            sma200 = historical_data['SMA200'][-1]

            if sma50 > sma200:
                trend = "upward"
                st.success(f"The stock is in an **upward trend** as the 50-day SMA is above the 200-day SMA.")
            elif sma50 < sma200:
                trend = "downward"
                st.warning(f"The stock is in a **downward trend** as the 50-day SMA is below the 200-day SMA.")
            else:
                trend = "sideways"
                st.info("The stock is moving **sideways** as the 50-day SMA is equal to the 200-day SMA.")

            # RSI Analysis
            latest_rsi = historical_data['RSI'][-1]
            if latest_rsi > 70:
                st.warning("The RSI indicates that the stock is **overbought** (>70).")
            elif latest_rsi < 30:
                st.success("The RSI indicates that the stock is **oversold** (<30).")
            else:
                st.info("The RSI is in a **neutral** range.")

            # Volatility Analysis
            latest_volatility = historical_data['Volatility'][-1]
            st.write(f"The current volatility (20-day standard deviation) is **{latest_volatility:.2f}**.")

            # Tooltips for volatility
            with st.expander("ℹ️ Volatility Tooltip"):
                st.write("Volatility measures the rate at which the price of a security increases or decreases.")

            # Bollinger Bands Analysis
            latest_close = historical_data['Close'][-1]
            bb_high = historical_data['BB_High'][-1]
            bb_low = historical_data['BB_Low'][-1]

            if latest_close > bb_high:
                st.warning("The price is above the upper Bollinger Band, indicating potential **overbought** conditions.")
            elif latest_close < bb_low:
                st.success("The price is below the lower Bollinger Band, indicating potential **oversold** conditions.")
            else:
                st.info("The price is within the Bollinger Bands.")

            # Disclaimer
            st.markdown("---")
            st.write("""
            **Disclaimer:** This tool is intended for informational purposes only and should not be construed as financial advice.
            Investing in stocks involves risk, and past performance is not indicative of future results.
            """)

        else:
            st.error("No historical data found for this ticker.")

    except Exception as e:
        st.error(f"An error occurred: {e}")
