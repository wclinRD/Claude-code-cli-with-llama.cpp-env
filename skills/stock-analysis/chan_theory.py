"""
Chan Theory Module - 纏論分析
筆、線段、中樞、走勢類型
"""

import pandas as pd
import numpy as np
from typing import Dict, List, Tuple


def identify笔(df: pd.DataFrame, min_bars: int = 4) -> List[Dict]:
    """
    識別纏論筆
    筆：至少 4 根 K 線構成的市場基本運動單位
    """
    if df is None or len(df) < min_bars:
        return []
    
    pens = []
    
    i = 0
    while i < len(df) - min_bars:
        start_idx = i
        
        found = False
        for j in range(i + min_bars, len(df)):
            high = df.iloc[j]['High']
            low = df.iloc[j]['Low']
            
            up = True
            for k in range(i, j):
                if df.iloc[k]['Close'] < df.iloc[k]['High'] * 0.99:
                    continue
                if df.iloc[k]['Close'] > df.iloc[k]['Low'] * 1.01:
                    continue
                up = False
                break
            
            if up:
                pens.append({
                    'start': str(df.iloc[i]['Date']),
                    'end': str(df.iloc[j]['Date']),
                    'type': 'up',
                    'high': float(high)
                })
                i = j
                found = True
                break
            
            down = True
            for k in range(i, j):
                if df.iloc[k]['Close'] > df.iloc[k]['Low'] * 1.01:
                    continue
                if df.iloc[k]['Close'] < df.iloc[k]['High'] * 0.99:
                    continue
                down = False
                break
            
            if down:
                pens.append({
                    'start': str(df.iloc[i]['Date']),
                    'end': str(df.iloc[j]['Date']),
                    'type': 'down',
                    'low': float(low)
                })
                i = j
                found = True
                break
        
        if not found:
            i += 1
    
    return pens[-10:]


def identify线段(df: pd.DataFrame) -> List[Dict]:
    """
    識別纏論線段
    線段：由筆構成的同級別趨勢
    """
    if df is None or len(df) < 10:
        return []
    
    pens = identify笔(df)
    
    if len(pens) < 3:
        return []
    
    segments = []
    current_type = pens[0]['type']
    start = pens[0]['start']
    
    for i in range(1, len(pens)):
        if pens[i]['type'] != current_type:
            segments.append({
                'start': start,
                'end': pens[i-1]['end'],
                'type': current_type
            })
            current_type = pens[i]['type']
            start = pens[i]['start']
    
    if pens:
        segments.append({
            'start': start,
            'end': pens[-1]['end'],
            'type': current_type
        })
    
    return segments[-5:]


def identify中枢(df: pd.DataFrame, lookback: int = 30) -> List[Dict]:
    """
    識別纏論中樞
    中樞：重叠的區間
    """
    if df is None or len(df) < lookback:
        return []
    
    recent = df.tail(lookback)
    
    ranges = []
    for i in range(len(recent)):
        ranges.append({
            'high': recent.iloc[i]['High'],
            'low': recent.iloc[i]['Low']
        })
    
    overlaps = []
    for i in range(len(ranges) - 1):
        for j in range(i + 1, len(ranges)):
            high = min(ranges[i]['high'], ranges[j]['high'])
            low = max(ranges[i]['low'], ranges[j]['low'])
            
            if high > low:
                overlaps.append({
                    'start': str(recent.iloc[i]['Date']),
                    'end': str(recent.iloc[j]['Date']),
                    'zone_high': float(high),
                    'zone_low': float(low)
                })
                break
    
    if overlaps:
        return overlaps[-3:]
    
    return []


def classify趋势(df: pd.DataFrame) -> Dict:
    """
    走勢類型分類
    """
    if df is None or len(df) < 20:
        return {'trend': 'unknown'}
    
    recent = df.tail(20)
    
    price_start = recent.iloc[0]['Close']
    price_end = recent.iloc[-1]['Close']
    price_change = (price_end - price_start) / price_start * 100
    
    highs = recent['High'].values
    lows = recent['Low'].values
    
    higher_highs = sum(1 for i in range(1, len(highs)) if highs[i] > highs[i-1])
    higher_lows = sum(1 for i in range(1, len(lows)) if lows[i] > lows[i-1])
    
    if price_change > 10 and higher_highs > len(highs) * 0.6:
        return {'trend': '上升趨勢', 'strength': 'strong'}
    elif price_change > 5:
        return {'trend': '上升趨勢', 'strength': 'weak'}
    elif price_change < -10 and higher_lows < len(lows) * 0.4:
        return {'trend': '下降趨勢', 'strength': 'strong'}
    elif price_change < -5:
        return {'trend': '下降趨勢', 'strength': 'weak'}
    else:
        return {'trend': '盤整', 'strength': 'neutral'}


def analyze_chan(df: pd.DataFrame) -> Dict:
    """綜合纏論分析"""
    if df is None or df.empty:
        return {'error': 'No data'}
    
    pens = identify笔(df)
    segments = identify线段(df)
    zhongshus = identify中枢(df)
    trend = classify趋势(df)
    
    return {
        'pens': pens,
        'segments': segments,
        'zhongshus': zhongshus,
        'trend': trend
    }