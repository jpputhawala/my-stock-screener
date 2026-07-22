import streamlit as st
import yfinance as yf
import pandas as pd
import datetime

st.set_page_config(page_title="Breakout Beacon - Live Option Signals", layout="wide")

st.title("🚨 Breakout Beacon (Live Option Call/Put Finder)")
st.caption("TradeFinder Style Screener: Direct CE / PE Action Signals & Momentum Analysis")

# High Volatility F&O & Midcap Stocks
STOCKS = [
    "PGEL.NS", "BANDHANBNK.NS", "LODHA.NS", "LUPIN.NS", "VOLTAS.NS", 
    "INOXWIND.NS", "NBCC.NS", "YESBANK.NS", "DLF.NS", "RELIANCE.NS", 
    "TATAMOTORS.NS", "SBIN.NS", "ICICIBANK.NS", "INFY.NS", "TCS.NS"
]

@st.cache_data(ttl=60)
def run_breakout_beacon():
    screener_results = []
    
    for ticker in STOCKS:
        try:
            t_obj = yf.Ticker(ticker)
            # Fetch 5-min candles
            df = t_obj.history(period="5d", interval="5m")
            if df.empty or len(df) < 20:
                continue
            
            latest = df.iloc[-1]
            prev_candle = df.iloc[-2]
            
            price = float(latest['Close'])
            prev_close = float(df.iloc[0]['Close'])
            
            # Overall % Change
            chg_pct = ((price - prev_close) / prev_close) * 100
            
            # 5-Min Price Velocity (Sgn %)
            sgn_pct = ((price - float(prev_candle['Close'])) / float(prev_candle['Close'])) * 100
            
            # Adaptive Threshold (Strict for live market, smart for after-hours)
            # Signal Action Logic
            if chg_pct >= 1.5 or sgn_pct >= 0.3:
                action = "🟢 BUY CALL (CE)"
                trend = "🚀 Strong Bullish Momentum"
            elif chg_pct <= -1.5 or sgn_pct <= -0.3:
                action = "🔴 BUY PUT (PE)"
                trend = "💥 Strong Bearish Breakdown"
            elif chg_pct > 0.5:
                action = "👀 WATCH CE (Bullish)"
                trend = "Uptrend Momentum"
            elif chg_pct < -0.5:
                action = "👀 WATCH PE (Bearish)"
                trend = "Downtrend Momentum"
            else:
                action = "⚪ NO TRADE (Consolidating)"
                trend = "Sideways / Neutral Range"

            time_str = latest.name.strftime('%H:%M') if hasattr(latest.name, 'strftime') else "15:30"

            screener_results.append({
                "Symbol": ticker.replace(".NS", ""),
                "Action Signal": action,
                "Trend Type": trend,
                "Price (LTP)": round(price, 2),
                "% chg": round(chg_pct, 2),
                "5-Min Velocity (Sgn %)": round(sgn_pct, 2),
                "Time": time_str
            })
        except Exception:
            continue
            
    return pd.DataFrame(screener_results)

# Render Table
st.subheader("🔥 Market Pulse: Call / Put Signals Table")
df_results = run_breakout_beacon()

if not df_results.empty:
    # Sort by absolute % chg to keep top moving stocks on top
    df_results['Abs_Chg'] = df_results['% chg'].abs()
    df_results = df_results.sort_values(by="Abs_Chg", ascending=False).drop(columns=['Abs_Chg'])
    
    st.dataframe(
        df_results,
        use_container_width=True,
        hide_index=True
    )
else:
    st.info("Market data fetch ho raha hai... Kripya refresh karein.")
