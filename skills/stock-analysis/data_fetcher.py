"""
Data Fetcher Module - 數據獲取模組
支援 yfinance (美股) 和 TWSE API (台股)
櫃買中心、產業基本面、籌碼分析
"""

import re
from typing import Optional, Dict, List
import pandas as pd

try:
    import yfinance
    YFINANCE_AVAILABLE = True
except ImportError:
    YFINANCE_AVAILABLE = False


TWSE_BASE_URL = "https://www.twse.com.tw/rwd/zh/afterTrading/STOCK_DAY"
TWSE_API_BASE = "https://www.twse.com.tw/rwd/zh"
GRETAI_URL = "https://www.gretai.org.tw/web/stock/aftertrading"


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


def detect_otc_market(ticker: str) -> bool:
    """偵測是否為上櫃股票 (6開頭)"""
    return bool(re.match(r'^\d{4,6}$', ticker)) and ticker.startswith(('6', '7', '8'))


def fetch_gretai(stock_code: str, year: int = None, month: int = None) -> Optional[pd.DataFrame]:
    """從櫃買中心獲取上櫃股票數據"""
    import requests
    from datetime import datetime
    
    if year is None:
        year = datetime.now().year
    if month is None:
        month = datetime.now().month
    
    params = {
        "d": f"{year}/{month:02d}",
        "stkno": stock_code,
        "response": "json"
    }
    
    try:
        resp = requests.get(f"{GRETAI_URL}/BOTRDAYA", params=params, timeout=10)
        data = resp.json()
        
        if 'aaData' not in data or not data['aaData']:
            return None
        
        records = []
        for row in data['aaData']:
            if len(row) >= 6:
                try:
                    records.append({
                        'Date': pd.to_datetime(row[0]),
                        'Open': int(row[3].replace(',', '')) if row[3] != '-' else 0,
                        'High': int(row[4].replace(',', '')) if row[4] != '-' else 0,
                        'Low': int(row[5].replace(',', '')) if row[5] != '-' else 0,
                        'Close': int(row[6].replace(',', '')) if row[6] != '-' else 0,
                        'Volume': int(row[2].replace(',', '')) if row[2] != '-' else 0
                    })
                except:
                    continue
        
        if records:
            df = pd.DataFrame(records)
            return df
        
        return None
    
    except Exception as e:
        print(f"Gretai fetch error: {e}")
        return None


def fetch_gretai_range(stock_code: str, months: int = 6) -> Optional[pd.DataFrame]:
    """從櫃買中心獲取多個月數據"""
    from datetime import datetime
    
    all_records = []
    current_date = datetime.now()
    
    for i in range(months):
        year = current_date.year
        month = current_date.month - i
        if month <= 0:
            month += 12
            year -= 1
        
        df = fetch_gretai(stock_code, year, month)
        if df is not None and not df.empty:
            all_records.append(df)
    
    if all_records:
        combined = pd.concat(all_records, ignore_index=True)
        combined = combined.drop_duplicates(subset=['Date']).sort_values('Date').reset_index(drop=True)
        return combined
    
    return None


def fetch_institutional_holdings(stock_code: str) -> Optional[Dict]:
    """取得法人持股資料 (外資/投信/自營商)"""
    import requests
    from datetime import datetime
    
    today = datetime.now()
    date_str = f"{today.year}{today.month:02d}{today.day:02d}"
    
    params = {
        "date": date_str,
        "stockNo": stock_code,
        "response": "json",
        "language": "zh-TW"
    }
    
    try:
        resp = requests.get(f"{TWSE_API_BASE}/fund/BWIBBU_d", params=params, timeout=10)
        data = resp.json()
        
        if 'data' not in data or not data['data']:
            return None
        
        for row in data['data']:
            if len(row) >= 6:
                return {
                    'foreign_investor': row[1],
                    'foreign_dealer': row[2],
                    'securities': row[3],
                    'total': row[4],
                    'date': row[0]
                }
        
        return None
    
    except Exception as e:
        print(f"Institutional holdings fetch error: {e}")
        return None


def fetch_margin_short(stock_code: str) -> Optional[Dict]:
    """取得融資融券資料"""
    import requests
    from datetime import datetime
    
    today = datetime.now()
    date_str = f"{today.year}{today.month:02d}{today.day:02d}"
    
    params = {
        "date": date_str,
        "stockNo": stock_code,
        "response": "json",
        "language": "zh-TW"
    }
    
    try:
        resp = requests.get(f"{TWSE_API_BASE}/stock/BWIBBU_d", params=params, timeout=10)
        data = resp.json()
        
        if 'data' not in data or not data['data']:
            return None
        
        for row in data['data']:
            if len(row) >= 8:
                try:
                    margin = int(row[5].replace(',', '')) if row[5] != '-' else 0
                    short = int(row[6].replace(',', '')) if row[6] != '-' else 0
                    
                    return {
                        'margin_balance': margin,
                        'short_balance': short,
                        'margin_change': row[4],
                        'short_change': row[7],
                        'date': row[0]
                    }
                except:
                    pass
        
        return None
    
    except Exception as e:
        print(f"Margin/short fetch error: {e}")
        return None


def fetch_industry_performance(industry_code: str = None) -> Optional[Dict]:
    """取得產業表現資料"""
    import requests
    
    params = {
        "response": "json",
        "language": "zh-TW"
    }
    
    try:
        if industry_code:
            params["indcode"] = industry_code
        
        resp = requests.get(f"{TWSE_API_BASE}/industry/BUANK_A", params=params, timeout=10)
        data = resp.json()
        
        if 'data' not in data:
            return None
        
        results = []
        for row in data['data'][:20]:
            if len(row) >= 4:
                results.append({
                    'industry': row[0],
                    'change_pct': row[1],
                    'stock_count': row[2],
                    'turnover_rate': row[3]
                })
        
        return {'industries': results}
    
    except Exception as e:
        print(f"Industry fetch error: {e}")
        return None


def fetch_stock_info(ticker: str) -> Optional[Dict]:
    """取得股票基本資料"""
    twse_code = ticker.replace('.TW', '')
    
    try:
        if YFINANCE_AVAILABLE:
            yf = yfinance.Ticker(f"{twse_code}.TW")
            info = yf.info
            return {
                'name': info.get('longName') or info.get('shortName'),
                'sector': info.get('sector'),
                'industry': info.get('industry'),
                'market_cap': info.get('marketCap'),
                'pe_ratio': info.get('trailingPE'),
                'dividend_yield': info.get('dividendYield'),
                '52w_high': info.get('fiftyTwoWeekHigh'),
                '52w_low': info.get('fiftyTwoWeekLow'),
            }
    except Exception as e:
        print(f"Stock info fetch error: {e}")
    
    return None


def fetch_daily_summary() -> Optional[Dict]:
    """取得大盤每日摘要"""
    import requests
    from datetime import datetime
    
    today = datetime.now()
    date_str = f"{today.year}{today.month:02d}{today.day:02d}"
    
    params = {
        "date": date_str,
        "response": "json",
        "language": "zh-TW"
    }
    
    try:
        resp = requests.get(f"{TWSE_API_BASE}/afterTrading/FMTQIK", params=params, timeout=10)
        data = resp.json()
        
        if 'data' not in data or not data['data']:
            return None
        
        row = data['data'][0]
        return {
            'date': row[0],
            'index': row[1].replace(',', ''),
            'change': row[2],
            'change_pct': row[3],
            'volume': row[4].replace(',', ''),
            'turnover_rate': row[5]
        }
    
    except Exception as e:
        print(f"Daily summary fetch error: {e}")
        return None


def fetch_usd_twd() -> Optional[Dict]:
    """取得美元兌台幣匯率"""
    import requests
    
    try:
        if YFINANCE_AVAILABLE:
            yf = yfinance.Ticker("USDTWD=X")
            hist = yf.history(period="5d")
            if not hist.empty:
                latest = hist.iloc[-1]
                prev = hist.iloc[-2] if len(hist) > 1 else latest
                change = ((latest['Close'] - prev['Close']) / prev['Close']) * 100
                return {
                    'rate': round(latest['Close'], 2),
                    'change_pct': round(change, 2),
                    'high': round(latest['High'], 2),
                    'low': round(latest['Low'], 2)
                }
    except Exception as e:
        print(f"USD/TWD fetch error: {e}")
    
    return None


def fetch_crude_oil() -> Optional[Dict]:
    """取得原油價格 (WTI)"""
    try:
        if YFINANCE_AVAILABLE:
            yf = yfinance.Ticker("CL=F")
            hist = yf.history(period="5d")
            if not hist.empty:
                latest = hist.iloc[-1]
                prev = hist.iloc[-2] if len(hist) > 1 else latest
                change = ((latest['Close'] - prev['Close']) / prev['Close']) * 100
                return {
                    'price': round(latest['Close'], 2),
                    'change_pct': round(change, 2),
                    'high': round(latest['High'], 2),
                    'low': round(latest['Low'], 2)
                }
    except Exception as e:
        print(f"Crude oil fetch error: {e}")
    
    return None


def fetch_gold() -> Optional[Dict]:
    """取得黃金價格"""
    try:
        if YFINANCE_AVAILABLE:
            yf = yfinance.Ticker("GC=F")
            hist = yf.history(period="5d")
            if not hist.empty:
                latest = hist.iloc[-1]
                prev = hist.iloc[-2] if len(hist) > 1 else latest
                change = ((latest['Close'] - prev['Close']) / prev['Close']) * 100
                return {
                    'price': round(latest['Close'], 2),
                    'change_pct': round(change, 2),
                    'high': round(latest['High'], 2),
                    'low': round(latest['Low'], 2)
                }
    except Exception as e:
        print(f"Gold fetch error: {e}")
    
    return None


def fetch_us_10y_bond() -> Optional[Dict]:
    """取得美國10年期公債殖利率"""
    try:
        if YFINANCE_AVAILABLE:
            yf = yfinance.Ticker("^TNX")
            hist = yf.history(period="5d")
            if not hist.empty:
                latest = hist.iloc[-1]
                return {
                    'rate': round(latest['Close'], 2),
                    'high': round(latest['High'], 2),
                    'low': round(latest['Low'], 2)
                }
    except Exception as e:
        print(f"US 10Y bond fetch error: {e}")
    
    return None


def fetch_sp500() -> Optional[Dict]:
    """取得S&P 500指數"""
    try:
        if YFINANCE_AVAILABLE:
            yf = yfinance.Ticker("^GSPC")
            hist = yf.history(period="5d")
            if not hist.empty:
                latest = hist.iloc[-1]
                prev = hist.iloc[-2] if len(hist) > 1 else latest
                change = ((latest['Close'] - prev['Close']) / prev['Close']) * 100
                return {
                    'index': round(latest['Close'], 2),
                    'change_pct': round(change, 2)
                }
    except Exception as e:
        print(f"S&P500 fetch error: {e}")
    
    return None


def fetch_nasdaq() -> Optional[Dict]:
    """取得Nasdaq指數"""
    try:
        if YFINANCE_AVAILABLE:
            yf = yfinance.Ticker("^IXIC")
            hist = yf.history(period="5d")
            if not hist.empty:
                latest = hist.iloc[-1]
                prev = hist.iloc[-2] if len(hist) > 1 else latest
                change = ((latest['Close'] - prev['Close']) / prev['Close']) * 100
                return {
                    'index': round(latest['Close'], 2),
                    'change_pct': round(change, 2)
                }
    except Exception as e:
        print(f"NASDAQ fetch error: {e}")
    
    return None


def fetch_macro_data() -> Dict:
    """取得總體經濟數據"""
    macro = {}
    
    macro['usd_twd'] = fetch_usd_twd()
    macro['crude_oil'] = fetch_crude_oil()
    macro['gold'] = fetch_gold()
    macro['us_10y_bond'] = fetch_us_10y_bond()
    macro['sp500'] = fetch_sp500()
    macro['nasdaq'] = fetch_nasdaq()
    
    return macro


def fetch_stock_news(ticker: str) -> List[Dict]:
    """取得股票相關新聞"""
    import requests
    
    twse_code = ticker.replace('.TW', '')
    
    if not YFINANCE_AVAILABLE:
        return []
    
    try:
        yf = yfinance.Ticker(f"{twse_code}.TW")
        news = yf.news
        
        if not news:
            return []
        
        results = []
        for item in news[:5]:
            results.append({
                'title': item.get('title', ''),
                'publisher': item.get('publisher', ''),
                'link': item.get('link', ''),
                'time': item.get('providerPublishTime', '')
            })
        
        return results
    
    except Exception as e:
        print(f"Stock news fetch error: {e}")
        return []


def fetch_market_news() -> List[Dict]:
    """取得市場最新新聞"""
    
    if not YFINANCE_AVAILABLE:
        return []
    
    try:
        tickers = ['^TWII', '^GSPC', 'AAPL', 'MSFT']
        all_news = []
        
        for ticker in tickers:
            yf = yfinance.Ticker(ticker)
            news = yf.news
            if news:
                for item in news[:2]:
                    all_news.append({
                        'title': item.get('title', ''),
                        'publisher': item.get('publisher', ''),
                        'source': ticker
                    })
        
        seen = set()
        unique_news = []
        for n in all_news:
            if n['title'] not in seen:
                seen.add(n['title'])
                unique_news.append(n)
        
        return unique_news[:8]
    
    except Exception as e:
        print(f"Market news fetch error: {e}")
        return []


def fetch_twse_announcements(stock_code: str) -> List[Dict]:
    """取得台股重大訊息"""
    import requests
    from datetime import datetime
    
    try:
        today = datetime.now()
        date_str = f"{today.year}{today.month:02d}{today.day:02d}"
        
        params = {
            "dtype": "ALL",
            "date": date_str,
            "stockNo": stock_code,
            "response": "json"
        }
        
        resp = requests.get("https://www.twse.com.tw/rwd/zh/common/disc/BWIBBU_d", 
                          params=params, timeout=10)
        
        if resp.status_code == 200:
            data = resp.json()
            if 'data' in data and data['data']:
                results = []
                for row in data['data'][:5]:
                    results.append({
                        'title': row[2] if len(row) > 2 else '',
                        'date': row[0] if len(row) > 0 else '',
                    })
                return results
        
        return []
    
    except Exception as e:
        print(f"TWSE announcements fetch error: {e}")
        return []


def fetch_taiwan_stock_news() -> List[Dict]:
    """取得台灣財經新聞 (從鉅亨網)"""
    import requests
    
    try:
        resp = requests.get(
            "https://api.cnyes.com/api/v1/news/category?q=stock&limit=10",
            headers={"Content-Type": "application/json"},
            timeout=10
        )
        
        if resp.status_code == 200:
            data = resp.json()
            results = []
            if 'data' in data:
                for item in data['data'][:8]:
                    results.append({
                        'title': item.get('title', ''),
                        'source': 'Yahoo/鉅亨',
                        'url': f"https://news.cnyes.com/news/id/{item.get('id')}"
                    })
            return results
        
        return []
    
    except Exception as e:
        print(f"Taiwan stock news fetch error: {e}")
        return []


def scrape_cnyes_news() -> List[Dict]:
    """從鉅亨網爬蟲取得最新財經新聞"""
    import requests
    from bs4 import BeautifulSoup
    
    try:
        headers = {
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
            'Accept-Language': 'zh-TW,zh;q=0.9,en-US;q=0.8,en;q=0.7'
        }
        
        resp = requests.get(
            "https://news.cnyes.com/",
            headers=headers,
            timeout=15
        )
        
        if resp.status_code != 200:
            return []
        
        soup = BeautifulSoup(resp.text, 'html.parser')
        articles = soup.find_all('a')[:30]
        
        results = []
        for art in articles:
            title = art.get('title', '') or art.get_text(strip=True)
            if title and 15 < len(title) < 80 and 'class' not in str(art.parent):
                results.append({
                    'title': title[:60],
                    'source': '鉅亨網'
                })
        
        return list({v['title']: v for v in results}.values())[:8]
    
    except Exception as e:
        print(f"CNYES scrape error: {e}")
        return []


def scrape_udn_news() -> List[Dict]:
    """從經濟日報取得最新財經新聞"""
    import requests
    from bs4 import BeautifulSoup
    
    try:
        headers = {
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
        }
        
        resp = requests.get(
            "https://money.udn.com/money/cate/5594",
            headers=headers,
            timeout=15
        )
        
        if resp.status_code != 200:
            return []
        
        soup = BeautifulSoup(resp.text, 'html.parser')
        links = soup.find_all('a', href=True)
        
        results = []
        for link in links[:30]:
            title = link.get_text(strip=True)
            href = link.get('href', '')
            if title and 15 < len(title) < 70 and '/money/' in href:
                results.append({
                    'title': title[:60],
                    'source': '經濟日報'
                })
        
        return list({v['title']: v for v in results}.values())[:6]
    
    except Exception as e:
        print(f"UDN scrape error: {e}")
        return []


def scrape_yahoo_news() -> List[Dict]:
    """從Yahoo奇摩股市取得台股新聞"""
    import requests
    from bs4 import BeautifulSoup
    
    try:
        headers = {
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
        }
        
        resp = requests.get(
            "https://tw.stock.yahoo.com/",
            headers=headers,
            timeout=15
        )
        
        if resp.status_code != 200:
            return []
        
        soup = BeautifulSoup(resp.text, 'html.parser')
        links = soup.find_all('a', href=True)
        
        results = []
        for link in links[:40]:
            title = link.get_text(strip=True)
            href = link.get('href', '')
            if title and 12 < len(title) < 60 and 'yahoo.com' in href:
                results.append({
                    'title': title[:60],
                    'source': 'Yahoo奇摩'
                })
        
        return list({v['title']: v for v in results}.values())[:6]
    
    except Exception as e:
        print(f"Yahoo scrape error: {e}")
        return []


def fetch_rss_news() -> List[Dict]:
    """從RSS取得財經新聞"""
    import requests
    import xml.etree.ElementTree as ET
    
    rss_feeds = [
        ('https://news.google.com/rss/topics/CAAqJggKIiBDQkFTRWdvSUwyMHZNRGx1YlY4U0FtVnVHZ0pWVXlnQVAB?hl=zh-TW&gl=TW&ceid=TW%3Azh-Hant', 'Google News'),
    ]
    
    results = []
    
    for url, source in rss_feeds:
        try:
            resp = requests.get(url, timeout=10, headers={'User-Agent': 'Mozilla/5.0'})
            if resp.status_code == 200:
                root = ET.fromstring(resp.content)
                for item in root.findall('.//item')[:10]:
                    title = item.find('title')
                    if title is not None and title.text:
                        results.append({
                            'title': title.text[:60],
                            'source': source
                        })
        except Exception as e:
            continue
    
    return results[:8]


def fetch_google_finance_news() -> List[Dict]:
    """從Google Finance取得新聞"""
    import requests
    
    try:
        url = "https://news.google.com/rss/topics/CAAqJggKIiBDQkFTRWdvSUwyMHZNRGx1YlY4U0FtVnVHZ0pWVXlnQVAB?hl=zh-TW&gl=TW&ceid=TW%3Azh-Hant"
        
        resp = requests.get(url, timeout=15, headers={'User-Agent': 'Mozilla/5.0'})
        
        if resp.status_code == 200:
            import xml.etree.ElementTree as ET
            root = ET.fromstring(resp.content)
            
            results = []
            for item in root.findall('.//item')[:10]:
                title = item.find('title')
                if title is not None and title.text:
                    results.append({
                        'title': title.text[:60],
                        'source': 'Google News'
                    })
            return results
        
    except Exception as e:
        print(f"Google Finance news error: {e}")
    
    return []


def fetch_stock_news_by_keyword(keyword: str = "台股") -> List[Dict]:
    """根據關鍵字取得相關新聞"""
    import requests
    import xml.etree.ElementTree as ET
    from urllib.parse import quote
    
    keywords = [
        f"台股 {keyword}",
        f"台灣股市 {keyword}",
        f"加權指數 {keyword}",
        f"半導體 {keyword}",
        f"AI {keyword}",
        f"電子股 {keyword}",
    ]
    
    results = []
    
    for kw in keywords[:3]:
        try:
            encoded_kw = quote(kw)
            url = f"https://news.google.com/rss/search?q={encoded_kw}&hl=zh-TW&gl=TW&ceid=TW%3Azh-Hant"
            
            resp = requests.get(url, timeout=10, headers={'User-Agent': 'Mozilla/5.0'})
            
            if resp.status_code == 200:
                root = ET.fromstring(resp.content)
                for item in root.findall('.//item')[:3]:
                    title = item.find('title')
                    if title is not None and title.text:
                        results.append({
                            'title': title.text[:55],
                            'source': 'Google'
                        })
        except:
            continue
    
    seen = set()
    unique = []
    for r in results:
        if r['title'] not in seen:
            seen.add(r['title'])
            unique.append(r)
    
    return unique[:8]


def fetch_all_news() -> Dict:
    """取得所有新聞來源"""
    news = {}
    
    news['rss'] = fetch_rss_news()
    news['google'] = fetch_google_finance_news()
    
    return news


def fetch_tech_news() -> List[Dict]:
    """從科技報橘取得科技/商業新聞"""
    import requests
    from bs4 import BeautifulSoup
    
    try:
        headers = {
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36'
        }
        
        urls = [
            ('https://techorange.github.io/', '科技橘報'),
        ]
        
        results = []
        for url, source in urls:
            try:
                resp = requests.get(url, headers=headers, timeout=10)
                if resp.status_code == 200:
                    soup = BeautifulSoup(resp.text, 'html.parser')
                    titles = soup.find_all(['h2', 'h3'])[:8]
                    for t in titles:
                        text = t.get_text(strip=True)
                        if 15 < len(text) < 60:
                            results.append({'title': text[:55], 'source': source})
            except:
                continue
        
        return results[:6]
    
    except Exception as e:
        return []