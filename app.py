import streamlit as st
import yfinance as yf
import pandas as pd
import datetime

st.set_page_config(page_title="Breakout Beacon - Call/Put Signal", layout="wide")

st.title("🚨 Breakout Beacon (Live Call/Put Option Finder)")
st.caption("TradeFinder Style: Direct CE / PE Action Signals based on Momentum Spurt")

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
            df = t_obj.history(period="5d", interval="5m")
            if df.empty or len(df) < 20:
                continue
            
            latest = df.iloc[-1]
            prev_candle = df.iloc[-2]
            
            price = float(latest['Close'])
            prev_close = float(df.iloc[0]['Close'])
            
            # % Change Calculation
            chg_pct = ((price - prev_close) / prev_close) * 100
            
            # 5-Min Price Velocity (Sgn %)
            sgn_pct = ((price - float(prev_candle['Close'])) / float(prev_candle['Close'])) * 100
            
            # Volume Check
            vol = float(latest['Volume'])
            avg_vol = float(df['Volume'].mean())
            rel_vol = vol / avg_vol if avg_vol > 0 else 1.0
            
            two_day_high = float(df['High'].max())
            two_day_low = float(df['Low'].min())
            
            # --- EXACT CALL / PUT ACTION LOGIC ---
            if price <= (two_day_low * 1.002) or (sgn_pct < -0.8 and rel_vol > 1.2):
                action = "🔴 BUY PUT (PE)"
                trend = "📉 Downward Breakout"
            elif price >= (two_day_high * 0.998) or (sgn_pct > 0.8 and rel_vol > 1.2):
                action = "🟢 BUY CALL (CE)"
                trend = "📈 Upward Breakout"
            elif sgn_pct > 0.4:
                action = "👀 WATCH CE"
                trend = "Mild Uptrend"
            elif sgn_pct < -0.4:
                action = "👀 WATCH PE"
                trend = "Mild Downtrend"
            else:
                action = "⚪ NO TRADE (WAIT)"
                trend = "Sideways / Neutral"

            time_str = latest.name.strftime('%H:%M') if hasattr(latest.name, 'strftime') else "09:30"

            screener_results.append({
                "Symbol": ticker.replace(".NS", ""),
                "Action Signal": action,
                "Trend Type": trend,
                "Price (LTP)": round(price, 2),
                "% chg": round(chg_pct, 2),
                "5-Min Velocity (Sgn %)": round(sgn_pct, 2),
                "Time": time_str,
                "Volume Boost": f"{round(rel_vol, 1)}x"
            })
        except Exception:
            continue
            
    return pd.DataFrame(screener_results)

# Render Table
st.subheader("🔥 Live Market Pulse Breakout Signals")
df_results = run_breakout_beacon()

if not df_results.empty:
    # Sort by absolute velocity to show active breakout stocks on top
    df_results['Abs_Sgn'] = df_results['5-Min Velocity (Sgn %)'].abs()
    df_results = df_results.sort_values(by="Abs_Sgn", ascending=False).drop(columns=['Abs_Sgn'])
    
    st.dataframe(
        df_results,
        use_container_width=True,
        hide_index=True
    )
else:
    st.info("Market data fetch ho raha hai... Kripya refresh karein.")
