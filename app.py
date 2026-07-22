import streamlit as st
import yfinance as yf
import pandas as pd
import datetime

st.set_page_config(page_title="Breakout Beacon - Smart Trend Option Screener", layout="wide")

st.title("🚨 Breakout Beacon (Smart VWAP & Trend Filtered Option Signals)")
st.caption("TradeFinder Style: Accurate Call/Put Action Signals based on Multi-Level Confirmation")

# Broad Volatile F&O / Midcap Stocks
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
            df = t_obj.history(period="5d", interval="5m")
            if df.empty or len(df) < 20:
                continue
            
            # Intraday VWAP Calculation
            df['VWAP'] = (df['Volume'] * (df['High'] + df['Low'] + df['Close']) / 3).cumsum() / df['Volume'].cumsum()
            
            latest = df.iloc[-1]
            prev_candle = df.iloc[-2]
            
            price = float(latest['Close'])
            vwap = float(latest['VWAP'])
            prev_close = float(df.iloc[0]['Close'])
            
            chg_pct = ((price - prev_close) / prev_close) * 100
            sgn_pct = ((price - float(prev_candle['Close'])) / float(prev_candle['Close'])) * 100
            
            vol = float(latest['Volume'])
            avg_vol = float(df['Volume'].mean())
            rel_vol = vol / avg_vol if avg_vol > 0 else 1.0
            
            day_high = float(df['High'].max())
            day_low = float(df['Low'].min())
            
            # --- ACCURATE TREND CONFIRMATION LOGIC ---
            # Rule: Bearish stock below VWAP CANNOT give BUY CALL signal!
            
            if price < vwap and (chg_pct <= -1.0 or price <= day_low * 1.003):
                action = "🔴 BUY PUT (PE)"
                trend = "📉 Strong Bearish Breakdown (Below VWAP)"
            elif price > vwap and (chg_pct >= 1.0 or price >= day_high * 0.997):
                action = "🟢 BUY CALL (CE)"
                trend = "🚀 Strong Bullish Breakout (Above VWAP)"
            elif price < vwap and chg_pct < 0:
                action = "👀 WATCH PE (Bearish)"
                trend = "Bearish Control (Below VWAP)"
            elif price > vwap and chg_pct > 0:
                action = "👀 WATCH CE (Bullish)"
                trend = "Bullish Control (Above VWAP)"
            else:
                action = "⚪ NO TRADE (Sideways)"
                trend = "No Clear Trend Confirmation"

            time_str = latest.name.strftime('%H:%M') if hasattr(latest.name, 'strftime') else "15:30"

            screener_results.append({
                "Symbol": ticker.replace(".NS", ""),
                "Action Signal": action,
                "Trend Status": trend,
                "Price (LTP)": round(price, 2),
                "VWAP": round(vwap, 2),
                "% chg": round(chg_pct, 2),
                "5-Min Velocity": round(sgn_pct, 2),
                "Time": time_str
            })
        except Exception:
            continue
            
    return pd.DataFrame(screener_results)

# Render Table
st.subheader("🔥 Market Pulse: Trend-Filtered Signals Table")
df_results = run_breakout_beacon()

if not df_results.empty:
    # Sort by absolute % chg to keep active movers on top
    df_results['Abs_Chg'] = df_results['% chg'].abs()
    df_results = df_results.sort_values(by="Abs_Chg", ascending=False).drop(columns=['Abs_Chg'])
    
    st.dataframe(
        df_results,
        use_container_width=True,
        hide_index=True
    )
else:
    st.info("Market data fetch ho raha hai... Kripya refresh karein.")
