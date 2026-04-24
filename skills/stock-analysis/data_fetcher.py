"""
Data Fetcher Module - 數據獲取模組
支援 yfinance (美股) 和 TWSE API (台股)
"""

import re
from typing import Optional
import pandas as pd

try:
    import yfinance
    YFINANCE_AVAILABLE = True
except ImportError:
    YFINANCE_AVAILABLE = False


TWSE_BASE_URL = "https://www.twse.com.tw/rwd/zh/afterTrading/STOCK_DAY"


def detect_market(ticker: str) -> str:
    """自動偵測市場類型"""
    ticker = ticker.upper().strip()
    
    if ticker.endswith('.TW'):
        return 'TWSE'
    elif re.match(r'^\d{4,6}$', ticker):
        return 'TWSE'
    elif re.match(r'^[A-Z]{1,5}$', ticker):
        return 'US'
    else:
        return 'US'


def fetch_yfinance(ticker: str, period: str = "6mo") -> Optional[pd.DataFrame]:
    """從 Yahoo Finance 獲取數據"""
    if not YFINANCE_AVAILABLE:
        raise ImportError("yfinance not installed. Run: pip install yfinance")
    
    try:
        ticker_obj = yfinance.Ticker(ticker)
        df = ticker_obj.history(period=period)
        
        if df.empty:
            return None
            
        df = df.reset_index()
        df['Date'] = pd.to_datetime(df['Date']).dt.tz_localize(None)
        
        return df[['Date', 'Open', 'High', 'Low', 'Close', 'Volume']]
    
    except Exception as e:
        print(f"yfinance fetch error: {e}")
        return None


def fetch_twse(stock_code: str, year: Optional[int] = None, month: Optional[int] = None) -> Optional[pd.DataFrame]:
    """從台灣證券交易所獲取數據"""
    import requests
    from datetime import datetime
    
    if year is None:
        year = datetime.now().year
    if month is None:
        month = datetime.now().month
    
    params = {
        "date": f"{year}{month:02d}01",
        "stockNo": stock_code,
        "response": "json",
        "language": "zh-TW"
    }
    
    try:
        resp = requests.get(TWSE_BASE_URL, params=params, timeout=10)
        data = resp.json()
        
        if 'data' not in data or not data['data']:
            return None
        
        records = []
        for row in data['data']:
            if len(row) >= 6:
                try:
                    records.append({
                        'Date': pd.to_datetime(row[0]),
                        'Open': int(row[3]) if row[3] != '-' else 0,
                        'High': int(row[4]) if row[4] != '-' else 0,
                        'Low': int(row[5]) if row[5] != '-' else 0,
                        'Close': int(row[6]) if row[6] != '-' else 0,
                        'Volume': int(row[2]) if row[2] != '-' else 0
                    })
                except:
                    continue
        
        if records:
            df = pd.DataFrame(records)
            return df
        
        return None
    
    except Exception as e:
        print(f"TWSE fetch error: {e}")
        return None


def fetch_twse_range(stock_code: str, months: int = 6) -> Optional[pd.DataFrame]:
    """從台灣證券交易所獲取多個月數據"""
    from datetime import datetime
    import calendar
    
    all_records = []
    current_date = datetime.now()
    
    for i in range(months):
        year = current_date.year
        month = current_date.month - i
        if month <= 0:
            month += 12
            year -= 1
        
        df = fetch_twse(stock_code, year, month)
        if df is not None and not df.empty:
            all_records.append(df)
    
    if all_records:
        combined = pd.concat(all_records, ignore_index=True)
        combined = combined.drop_duplicates(subset=['Date']).sort_values('Date').reset_index(drop=True)
        return combined
    
    return None


def fetch_data(ticker: str, period: str = "6mo", source: str = "auto") -> Optional[pd.DataFrame]:
    """
    統一的數據獲取接口
    
    Args:
        ticker: 股票代碼 (如 AAPL, 2330.TW, 2330)
        period: 數據期間 (1mo, 3mo, 6mo, 1y, 2y, 5y)
        source: 數據來源 (auto, yfinance, twse)
    
    Returns:
        DataFrame with Date, Open, High, Low, Close, Volume columns
    """
    if source == "auto":
        market = detect_market(ticker)
    else:
        market = source
    
    if market == "TWSE":
        twse_code = ticker.replace('.TW', '')
        if re.match(r'^\d{4,6}$', twse_code):
            full_ticker = f"{twse_code}.TW"
            df = fetch_yfinance(full_ticker, period)
            if df is None or df.empty:
                month_map = {'1mo': 1, '3mo': 3, '6mo': 6, '1y': 12, '2y': 24, '5y': 60}
                months = month_map.get(period, 6)
                df = fetch_twse_range(twse_code, months)
        else:
            df = fetch_yfinance(ticker, period)
    else:
        df = fetch_yfinance(ticker, period)
    
    if df is not None and not df.empty:
        df = df.sort_values('Date').reset_index(drop=True)
    
    return df


def get_recent_closes(ticker: str, days: int = 60) -> list:
    """取得最近收盤價列表"""
    df = fetch_data(ticker)
    if df is None or df.empty:
        return []
    
    return df['Close'].tail(days).tolist()


def get_latest_price(ticker: str) -> Optional[dict]:
    """取得最新價格"""
    df = fetch_data(ticker)
    if df is None or df.empty:
        return None
    
    latest = df.iloc[-1]
    
    prev = None
    if len(df) > 1:
        prev = df.iloc[-2]
    
    change = 0
    change_pct = 0
    if prev is not None:
        change = float(latest['Close']) - float(prev['Close'])
        change_pct = (change / float(prev['Close'])) * 100
    
    return {
        'date': latest['Date'].strftime('%Y-%m-%d'),
        'open': float(latest['Open']),
        'high': float(latest['High']),
        'low': float(latest['Low']),
        'close': float(latest['Close']),
        'volume': int(latest['Volume']),
        'change': change,
        'change_pct': change_pct
    }