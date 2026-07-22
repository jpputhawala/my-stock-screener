import streamlit as st
import yfinance as yf
import pandas as pd

st.set_page_config(page_title="Intraday Stock Option Screener", layout="wide")

st.title("⚡ Intraday Stock Option Screener (CE/PE)")
st.subheader("Automated Entry, Exit, Target & SL Finder")

# Liquid FNO Stocks List
FNO_STOCKS = [
    "RELIANCE.NS", "TATAMOTORS.NS", "SBIN.NS", "ICICIBANK.NS", 
    "INFY.NS", "TCS.NS", "AXISBANK.NS", "BHARTIARTL.NS", "TATASTEEL.NS",
    "HDFCBANK.NS", "LT.NS", "MARUTI.NS", "M&M.NS", "KOTAKBANK.NS",
    "BAJFINANCE.NS"
]

def analyze_stock(ticker):
    try:
        df = yf.Ticker(ticker).history(period="5d", interval="5m")
        if df.empty or len(df) < 10:
            return None
        
        # VWAP Calculation
        df['VWAP'] = (df['Volume'] * (df['High'] + df['Low'] + df['Close']) / 3).cumsum() / df['Volume'].cumsum()
        
        latest = df.iloc[-1]
        close = float(latest['Close'])
        vwap = float(latest['VWAP'])
        
        if pd.isna(close) or pd.isna(vwap):
            return None
        
        status = "🟢 BULLISH (Buy CE)" if close > vwap else "🔴 BEARISH (Buy PE)"
            
        return {
            "Stock": ticker.replace(".NS", ""),
            "LTP": round(close, 2),
            "VWAP": round(vwap, 2),
            "Signal": status,
            "Entry Point": round(close, 2),
            "Target (T1)": round(close * 1.01, 2) if "BULLISH" in status else round(close * 0.99, 2),
            "Target (T2)": round(close * 1.02, 2) if "BULLISH" in status else round(close * 0.98, 2),
            "Stop Loss (SL)": round(vwap, 2)
        }
    except Exception:
        return None

if st.button("🔍 Run Screener Now"):
    results = []
    progress_bar = st.progress(0)
    
    with st.spinner("Fetching Market Data... Please wait 10-15 seconds"):
        total = len(FNO_STOCKS)
        for idx, stock in enumerate(FNO_STOCKS):
            res = analyze_stock(stock)
            if res:
                results.append(res)
            progress_bar.progress((idx + 1) / total)
            
    if len(results) > 0:
        df_res = pd.DataFrame(results)
        st.dataframe(df_res, use_container_width=True)
    else:
        st.warning("⚠️ Live market data load hone me issue aaya. Market hours (9:15 AM - 3:30 PM) me try karein.")
