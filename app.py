import streamlit as st
import yfinance as yf
import pandas as pd
import streamlit.components.v1 as components

# Layout width wide rakhein taaki TradingView jaisa dashboard bane
st.set_page_config(page_title="Custom Momentum Screener", layout="wide")

# 1. Top Title & Filter Pills Section
st.title("📊 MOMENTUM SCREENER GISM")

# Custom UI Badges / Filters Bar (TradingView Dark Style)
filter_col1, filter_col2, filter_col3, filter_col4 = st.columns(4)

with filter_col1:
    min_rel_vol = st.number_input("Rel Vol >", value=0.1, step=0.1)
with filter_col2:
    min_mkt_cap = st.selectbox("Market Cap", ["200B INR+", "All Caps"])
with filter_col3:
    beta_filter = st.checkbox("Beta > 0 (High Volatility)", value=True)
with filter_col4:
    show_news = st.checkbox("Fresh News Stocks Only 📰", value=False)

# 2. Main Data Table with Green/Red Price Change Column
# Pandas DataFrame ko Streamlit `st.dataframe` me TradingView format me render karna
