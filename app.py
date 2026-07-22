import streamlit as st
import yfinance as yf
import pandas as pd
import datetime
import streamlit.components.v1 as components

st.set_page_config(page_title="Pro F&O Screener: News & Breakout Finder", layout="wide")

st.title("⚡ Pro Intraday Screener: Extremely Bullish & Fresh News Stocks")
st.subheader("Automated Momentum, Fresh News Badges, Targets, SL & Live Charts")

# Top FNO Stocks List
FNO_STOCKS = [
    "RELIANCE.NS", "TATAMOTORS.NS", "SBIN.NS", "ICICIBANK.NS", "INFY.NS",
    "TCS.NS", "AXISBANK.NS", "BHARTIARTL.NS", "TATASTEEL.NS", "HDFCBANK.NS",
    "LT.NS", "MARUTI.NS", "M&M.NS", "KOTAKBANK.NS", "BAJFINANCE.NS",
    "HCLTECH.NS", "SUNPHARMA.NS", "NTPC.NS", "ONGC.NS", "POWERGRID.NS",
    "COALINDIA.NS", "TITAN.NS", "ULTRACEMCO.NS", "ADANIENT.NS", "ADANIPORTS.NS",
    "HEROMOTOCO.NS", "EICHERMOT.NS", "BPCL.NS", "TATACHEM.NS", "HAL.NS"
]

def analyze_stock_with_strict_news(ticker):
    try:
        t_obj = yf.Ticker(ticker)
        df = t_obj.history(period="5d", interval="5m")
        if df.empty or len(df) < 10:
            return None, None
        
        # VWAP Calculation
        df['VWAP'] = (df['Volume'] * (df['High'] + df['Low'] + df['Close']) / 3).cumsum() / df['Volume'].cumsum()
        
        latest = df.iloc[-1]
        close = float(latest['Close'])
        vwap = float(latest['VWAP'])
        vol = float(latest['Volume'])
        avg_vol = float(df['Volume'].mean())
        day_high = float(df['High'].max())
        
        if pd.isna(close) or pd.isna(vwap):
            return None, None
        
        # Extremely Bullish Condition
        is_high_volume = vol > (avg_vol * 1.3)
        near_day_high = close >= (day_high * 0.997)
        
        if close > vwap and is_high_volume and near_day_high:
            status = "🚀 EXTREMELY BULLISH"
        elif close > vwap:
            status = "🟢 BULLISH (Buy CE)"
        else:
            status = "🔴 BEARISH (Buy PE)"
            
        volume_status = "🔥 High Volume Spurt" if is_high_volume else "Normal"

        # STRICT FRESH NEWS CHECK (Last 48 Hours)
        news_items = t_obj.news
        fresh_news_list = []
        has_fresh_news = "---"

        if news_items and len(news_items) > 0:
            now = datetime.datetime.now()
            for item in news_items:
                pub_time = item.get('providerPublishTime', None)
                if pub_time:
                    pub_date = datetime.datetime.fromtimestamp(pub_time)
                    # Checking if news was published within last 48 hours
                    if (now - pub_date).total_seconds() <= 172800:
                        fresh_news_list.append(item)

            if len(fresh_news_list) > 0:
                has_fresh_news = "📰 Fresh News Stock"

        row_data = {
            "Stock": ticker.replace(".NS", ""),
            "LTP": round(close, 2),
            "VWAP": round(vwap, 2),
            "Signal": status,
            "News Tag": has_fresh_news,
            "Volume Momentum": volume_status,
            "Target (T1)": round(close * 1.01, 2) if "BULLISH" in status else round(close * 0.99, 2),
            "Target (T2)": round(close * 1.02, 2) if "BULLISH" in status else round(close * 0.98, 2),
            "Stop Loss (SL)": round(vwap, 2)
        }
        
        return row_data, fresh_news_list
    except Exception:
        return None, None

# Action Button
if st.button("🔍 Run Screener (Find Fresh News & Breakout Stocks)"):
    results = []
    news_dict = {}
    progress_bar = st.progress(0)
    
    with st.spinner("Filtering Real Fresh News & Extremely Bullish Stocks..."):
        total = len(FNO_STOCKS)
        for idx, stock in enumerate(FNO_STOCKS):
            res, news = analyze_stock_with_strict_news(stock)
            if res:
                results.append(res)
                if news and len(news) > 0:
                    news_dict[stock.replace(".NS", "")] = news
            progress_bar.progress((idx + 1) / total)
            
    if len(results) > 0:
        st.session_state['screener_data'] = pd.DataFrame(results)
        st.session_state['news_data'] = news_dict
    else:
        st.warning("⚠️ Data load hone me dikkat hui. Kripya market hours me refresh karein.")

# Display Table
if 'screener_data' in st.session_state:
    st.dataframe(st.session_state['screener_data'], use_container_width=True)

st.divider()

# Stock Specific News & Live Chart Section
st.header("📊 Interactive Chart & Fresh News Section")
clean_symbols = [s.replace(".NS", "") for s in FNO_STOCKS]
selected_stock = st.selectbox("Stock Select Karein (Chart & News Dekhne Ke Liye):", clean_symbols, index=0)

if selected_stock:
    col1, col2 = st.columns([2, 1])
    
    with col1:
        st.subheader(f"📈 {selected_stock} Live Candlestick Chart")
        tv_symbol = f"NSE:{selected_stock}"
        tv_widget_code = f"""
        <div class="tradingview-widget-container" style="height:500px;width:100%;">
          <div id="tradingview_chart" style="height:calc(100% - 32px);width:100%;"></div>
          <script type="text/javascript" src="https://s3.tradingview.com/tv.js"></script>
          <script type="text/javascript">
          new TradingView.widget({{
            "autosize": true,
            "symbol": "{tv_symbol}",
            "interval": "5",
            "timezone": "Asia/Kolkata",
            "theme": "dark",
            "style": "1",
            "locale": "in",
            "toolbar_bg": "#f1f3f6",
            "enable_publishing": false,
            "hide_side_toolbar": false,
            "allow_symbol_change": true,
            "container_id": "tradingview_chart"
          }});
          </script>
        </div>
        """
        components.html(tv_widget_code, height=520)

    with col2:
        st.subheader(f"📰 {selected_stock} Latest Fresh News Headlines")
        if 'news_data' in st.session_state and selected_stock in st.session_state['news_data']:
            stock_news = st.session_state['news_data'][selected_stock]
            if stock_news and len(stock_news) > 0:
                for item in stock_news[:4]:
                    title = item.get('title', 'No Title')
                    publisher = item.get('publisher', 'Market News')
                    link = item.get('link', '#')
                    st.markdown(f"👉 **[{title}]({link})**")
                    st.caption(f"Source: {publisher}")
                    st.write("---")
            else:
                st.info("Is stock ke liye pichle 28-48 ghante me koi fresh news nahi mili.")
        else:
            st.info("Pehle 'Run Screener' button par click karein news check karne ke liye.")
