import streamlit as st
import yfinance as yf
import pandas as pd
import datetime

st.set_page_config(page_title="TradeFinder Style Breakout Beacon", layout="wide", initial_sidebar_state="expanded")

st.title("🚨 Breakout Beacon & Intraday Boost Screener")
st.caption("Live 5-Min Momentum Spurt, Range Breakout & Bearish/Bullish Signals")

# High Volatility & F&O Stocks (Including Midcaps like PGEL)
STOCKS = [
    "PGEL.NS", "BANDHANBNK.NS", "LODHA.NS", "LUPIN.NS", "VOLTAS.NS", 
    "INOXWIND.NS", "NBCC.NS", "YESBANK.NS", "DLF.NS", "RELIANCE.NS", 
    "TATAMOTORS.NS", "SBIN.NS", "ICICIBANK.NS", "INFY.NS", "TCS.NS"
]

@st.cache_data(ttl=60)  # Auto Refresh every 60 sec
def run_breakout_beacon():
    screener_results = []
    
    for ticker in STOCKS:
        try:
            t_obj = yf.Ticker(ticker)
            # Fetch 5 days 5-min candle data
            df = t_obj.history(period="5d", interval="5m")
            if df.empty or len(df) < 20:
                continue
            
            latest = df.iloc[-1]
            prev_candle = df.iloc[-2]
            
            price = float(latest['Close'])
            prev_close = float(df.iloc[0]['Close'])
            
            # % Change calculation
            chg_pct = ((price - prev_close) / prev_close) * 100
            
            # Signal % (Sgn %) - Last 5 min price velocity
            sgn_pct = ((price - float(prev_candle['Close'])) / float(prev_candle['Close'])) * 100
            
            # Volume & Breakout Logic
            vol = float(latest['Volume'])
            avg_vol = float(df['Volume'].mean())
            rel_vol = vol / avg_vol if avg_vol > 0 else 1.0
            
            # 2-Day High & Low
            two_day_high = float(df['High'].max())
            two_day_low = float(df['Low'].min())
            
            # Signal Detection Logic (TradeFinder Beacon Logic)
            signal_type = "Neutral ⚪"
            badge = "---"
            
            # Bearish Breakout (Red Bear Badge)
            if price <= (two_day_low * 1.002) and rel_vol > 1.2:
                signal_type = "🐻 BEARISH BREAKOUT"
                badge = "🔴 SELL / PUT"
            # Bullish Breakout (Green Bull Badge)
            elif price >= (two_day_high * 0.998) and rel_vol > 1.2:
                signal_type = "🐂 BULLISH BREAKOUT"
                badge = "🟢 BUY / CALL"
            elif sgn_pct < -0.5:
                signal_type = "📉 Sudden Drop"
                badge = "🔻 Weakness"
            elif sgn_pct > 0.5:
                signal_type = "📈 Sudden Surge"
                badge = "🔺 Strength"

            time_str = latest.name.strftime('%H:%M') if hasattr(latest.name, 'strftime') else "09:30"

            screener_results.append({
                "Symbol": ticker.replace(".NS", ""),
                "% chg": round(chg_pct, 2),
                "Sgn %": round(sgn_pct, 2),
                "Time": time_str,
                "Signal": badge,
                "Type": signal_type,
                "Price": round(price, 2),
                "Rel Vol": round(rel_vol, 2)
            })
        except Exception:
            continue
            
    return pd.DataFrame(screener_results)

# Screen Layout
st.subheader("🔥 Market Pulse: Breakout Beacon Signals")
df_results = run_breakout_beacon()

if not df_results.empty:
    # Sort by absolute Sgn % change to show top movers on top
    df_results['Abs_Sgn'] = df_results['Sgn %'].abs()
    df_results = df_results.sort_values(by="Abs_Sgn", ascending=False).drop(columns=['Abs_Sgn'])
    
    # Custom Styling
    st.dataframe(
        df_results,
        use_container_width=True,
        hide_index=True,
        column_config={
            "% chg": st.column_config.NumberColumn("% chg", format="%.2f%%"),
            "Sgn %": st.column_config.NumberColumn("Sgn %", format="%.2f%%"),
            "Rel Vol": st.column_config.NumberColumn("Rel Vol", format="%.2fx"),
        }
    )
else:
    st.info("Market data fetch ho raha hai... Kripya refresh karein.")
