"""
Moving Average & Granville's Eight Rules Module - 均線與葛蘭威爾八大法則
"""

import pandas as pd
import numpy as np
from typing import Dict, List


def calculate_mas(df: pd.DataFrame) -> pd.DataFrame:
    """計算均線"""
    if df is None or len(df) < 240:
        return df
    
    df = df.copy()
    
    df['MA5'] = df['Close'].rolling(window=5).mean()
    df['MA10'] = df['Close'].rolling(window=10).mean()
    df['MA20'] = df['Close'].rolling(window=20).mean()
    df['MA60'] = df['Close'].rolling(window=60).mean()
    df['MA120'] = df['Close'].rolling(window=120).mean()
    df['MA240'] = df['Close'].rolling(window=240).mean()
    
    return df


def detect_ma_alignment(df: pd.DataFrame) -> Dict:
    """偵測均線排列"""
    if df is None or len(df) < 60:
        return {'alignment': 'unknown', 'signal': 'neutral'}
    
    mas = ['MA5', 'MA10', 'MA20', 'MA60', 'MA120']
    
    if all(col in df.columns for col in mas):
        latest = df.iloc[-1]
        
        bullish = all(latest[col] > latest[mas[i+1]] 
                     for i, col in enumerate(mas[:-1]) 
                     if pd.notna(latest[col]) and pd.notna(latest[mas[i+1]]))
        
        bearish = all(latest[col] < latest[mas[i+1]] 
                    for i, col in enumerate(mas[:-1]) 
                    if pd.notna(latest[col]) and pd.notna(latest[mas[i+1]]))
        
        if bullish:
            return {'alignment': 'bullish', 'signal': 'strong_buy'}
        elif bearish:
            return {'alignment': 'bearish', 'signal': 'strong_sell'}
        
        return {'alignment': 'mixed', 'signal': 'neutral'}
    
    return {'alignment': 'unknown', 'signal': 'neutral'}


def granville_rules(df: pd.DataFrame) -> List[Dict]:
    """
    葛蘭威爾八大法則
    1. MA4 從下降轉為走平或上升，股價從 MA4 上方穿破 MA4
    2. 股價向上穿越 MA4 後，又回測 MA4 但不跌破
    3. 股價在 MA4 上方行走，突然跌破 MA4 但很快站回
    6.  股價快速下跌遠離 MA4，出現反彈
    7. 股價站上 MA4 之後往上升，離 MA4 越來越遠，應該獲利了結
    8. MA4 從上升轉為走平或下跌，股價從 MA4 下方跌破 MA4
    """
    if df is None or len(df) < 20:
        return []
    
    df = calculate_mas(df)
    
    if 'MA4' not in df.columns and 'MA5' in df.columns:
        df['MA4'] = df['Close'].rolling(window=4).mean()
    
    signals = []
    
    for i in range(5, len(df)):
        curr = df.iloc[i]
        prev = df.iloc[i-1]
        
        price = curr['Close']
        ma4 = curr.get('MA4', curr.get('MA5'))
        ma4_prev = prev.get('MA4', prev.get('MA5'))
        
        if pd.isna(ma4) or pd.isna(ma4_prev):
            continue
        
        if i >= 1:
            ma4_2prev = df.iloc[i-2].get('MA4', df.iloc[i-2].get('MA5'))
            
            if pd.notna(ma4_2prev) and ma4_2prev < ma4_prev < ma4:
                if price > ma4:
                    signals.append({
                        'rule': 1,
                        'name': '買入訊號1',
                        'description': 'MA4 從下降轉為上升，股價突破 MA4',
                        'date': str(curr['Date']),
                        'action': 'buy'
                    })
        
        if (i >= 2 and 
            prev['Close'] > ma4 and 
            curr['Close'] < ma4 and
            df.iloc[i-2]['Close'] > df.iloc[i-2].get('MA4', df.iloc[i-2].get('MA5'))):
            signals.append({
                'rule': 2,
                'name': '買入訊號2',
                'description': '股價突破 MA4 後回測不跌破',
                'date': str(curr['Date']),
                'action': 'buy'
            })
        
        if (price > ma4 and 
            ma4 > ma4_prev and
            ma4_prev < df.iloc[i-2].get('MA4', df.iloc[i-2].get('MA5'))):
            signals.append({
                'rule': 3,
                'name': '買入訊號3',
                'description': '股價在 MA4 上方，突然跌破 MA4 又站回',
                'date': str(curr['Date']),
                'action': 'buy'
            })
        
        if i >= 5:
            ma4_avg_5 = df.iloc[i-5:i]['MA4'].mean()
            if price < ma4 and ma4 < ma4_avg_5 * 0.95:
                signals.append({
                    'rule': 6,
                    'name': '買入訊號6',
                    'description': '股價快速下跌遠離 MA4，出現反彈',
                    'date': str(curr['Date']),
                    'action': 'buy'
                })
        
        if i >= 10:
            ma4_10d_ago = df.iloc[i-10].get('MA4', df.iloc[i-10].get('MA5'))
            if (price > ma4 and ma4 > ma4_10d_ago * 1.1):
                signals.append({
                    'rule': 7,
                    'name': '賣出訊號7',
                    'description': '股價離 MA4 越來越遠，應獲利了結',
                    'date': str(curr['Date']),
                    'action': 'sell'
                })
        
        if (ma4_prev > ma4 and 
            df.iloc[i-2].get('MA4', df.iloc[i-2].get('MA5')) > ma4_prev):
            if price < ma4:
                signals.append({
                    'rule': 8,
                    'name': '賣出訊號8',
                    'description': 'MA4 從上升轉為下跌，股價跌破 MA4',
                    'date': str(curr['Date']),
                    'action': 'sell'
                })
    
    return signals[-10:]


def analyze_moving_avg(df: pd.DataFrame) -> Dict:
    """綜合均線分析"""
    if df is None or df.empty:
        return {'error': 'No data'}
    
    df_with_ma = calculate_mas(df.copy())
    alignment = detect_ma_alignment(df_with_ma)
    signals = granville_rules(df_with_ma)
    
    latest = df_with_ma.iloc[-1]
    
    mas_values = {}
    for ma in ['MA5', 'MA10', 'MA20', 'MA60', 'MA120', 'MA240']:
        if ma in df_with_ma.columns:
            mas_values[ma] = round(float(latest[ma]), 2) if pd.notna(latest.get(ma)) else None
    
    return {
        'mas': mas_values,
        'alignment': alignment,
        'signals': signals,
        'current_price': round(float(latest['Close']), 2)
    }