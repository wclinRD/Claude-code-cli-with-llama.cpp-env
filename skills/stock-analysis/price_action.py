"""
Price Action Module - 價格行為分析
支撐/阻力位、缺口分析、趨勢線、型態辨識
"""

import pandas as pd
import numpy as np
from typing import List, Tuple, Dict, Optional


def find_support_resistance(df: pd.DataFrame, window: int = 20) -> Dict:
    """尋找支撐與阻力位"""
    if df is None or len(df) < window:
        return {'support': [], 'resistance': []}
    
    closes = df['Close'].values
    highs = df['High'].values
    lows = df['Low'].values
    
    support_levels = []
    resistance_levels = []
    
    for i in range(window, len(closes) - window):
        if all(lows[i] <= lows[j] for j in range(max(0, i - window), i)):
            support_levels.append(lows[i])
        
        if all(highs[i] >= highs[j] for j in range(max(0, i - window), i)):
            resistance_levels.append(highs[i])
    
    support_levels = sorted(set(support_levels))[-3:] if support_levels else []
    resistance_levels = sorted(set(resistance_levels))[-3:] if resistance_levels else []
    
    return {
        'support': support_levels,
        'resistance': resistance_levels
    }


def detect_gaps(df: pd.DataFrame) -> List[Dict]:
    """偵測缺口"""
    if df is None or len(df) < 2:
        return []
    
    gaps = []
    
    for i in range(1, len(df)):
        prev_low = df.iloc[i-1]['Low']
        prev_high = df.iloc[i-1]['High']
        curr_low = df.iloc[i]['Low']
        curr_high = df.iloc[i]['High']
        
        if curr_low > prev_high:
            gap_size = ((curr_low - prev_high) / prev_high) * 100
            gaps.append({
                'date': df.iloc[i]['Date'],
                'type': 'up_gap',
                'size': gap_size,
                'filled': False
            })
        elif curr_high < prev_low:
            gap_size = ((prev_low - curr_high) / prev_low) * 100
            gaps.append({
                'date': df.iloc[i]['Date'],
                'type': 'down_gap',
                'size': gap_size,
                'filled': False
            })
    
    return gaps[-5:]


def detect_trendlines(df: pd.DataFrame, lookback: int = 60) -> Dict:
    """偵測趨勢線"""
    if df is None or len(df) < 10:
        return {'uptrend': False, 'downtrend': False, 'trendline_price': None}
    
    recent = df.tail(lookback)
    
    x = np.arange(len(recent))
    y = recent['Close'].values
    
    slope, intercept = np.polyfit(x, y, 1)
    
    is_uptrend = slope > 0
    is_downtrend = slope < 0
    
    current_price = df.iloc[-1]['Close']
    trendline_price = slope * (len(recent) - 1) + intercept
    
    return {
        'uptrend': is_uptrend,
        'downtrend': is_downtrend,
        'slope': slope,
        'trendline_price': trendline_price
    }


def detect_patterns(df: pd.DataFrame) -> Dict:
    """型態辨識"""
    if df is None or len(df) < 30:
        return {'pattern': None, 'confidence': 0}
    
    recent = df.tail(60)
    closes = recent['Close'].values
    highs = recent['High'].values
    lows = recent['Low'].values
    
    price_range = highs.max() - lows.min()
    current_price = closes[-1]
    start_price = closes[0]
    
    if lows.min() == lows[0]:
        if all(closes[i] >= closes[0] * 0.95 for i in range(len(closes) // 2, len(closes))):
            if highs[-1] > highs.max() * 0.95:
                return {'pattern': 'W底', 'confidence': 0.7}
    
    if highs.max() == highs[0]:
        if all(closes[i] <= closes[0] * 1.05 for i in range(len(closes) // 2, len(closes))):
            if lows[-1] < lows.min() * 1.05:
                return {'pattern': 'M��', 'confidence': 0.7}
    
    first_half = closes[:len(closes)//2]
    second_half = closes[len(closes)//2:]
    
    if abs(first_half.mean() - second_half.mean()) < price_range * 0.1:
        return {'pattern': '整理三角', 'confidence': 0.5}
    
    if current_price > start_price * 1.1:
        return {'pattern': '多頭趨勢', 'confidence': 0.6}
    elif current_price < start_price * 0.9:
        return {'pattern': '空頭趨勢', 'confidence': 0.6}
    
    return {'pattern': '盤整', 'confidence': 0.4}


def analyze_price_action(df: pd.DataFrame) -> Dict:
    """綜合價格行為分析"""
    if df is None or df.empty:
        return {'error': 'No data'}
    
    sr = find_support_resistance(df)
    gaps = detect_gaps(df)
    trendline = detect_trendlines(df)
    pattern = detect_patterns(df)
    
    current_price = df.iloc[-1]['Close']
    
    nearest_support = None
    for s in sr['support']:
        if s < current_price:
            nearest_support = s
    
    nearest_resistance = None
    for r in sr['resistance']:
        if r > current_price:
            nearest_resistance = r
    
    return {
        'current_price': float(current_price),
        'support': sr['support'],
        'resistance': sr['resistance'],
        'nearest_support': nearest_support,
        'nearest_resistance': nearest_resistance,
        'gaps': gaps,
        'trendline': trendline,
        'pattern': pattern
    }