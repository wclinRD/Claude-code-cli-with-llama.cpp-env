"""
Wave Theory Module - 波浪理論
艾略特波浪、推動浪、修正浪、黄金分割率
"""

import pandas as pd
import numpy as np
from typing import Dict, List, Tuple


def find_wave_peaks(df: pd.DataFrame, lookback: int = 60) -> Dict:
    """尋找波浪的高低點"""
    if df is None or len(df) < 10:
        return {'peaks': [], 'troughs': []}
    
    recent = df.tail(lookback)
    
    peaks = []
    troughs = []
    
    for i in range(2, len(recent) - 2):
        if (recent.iloc[i]['High'] > recent.iloc[i-1]['High'] and
            recent.iloc[i]['High'] > recent.iloc[i-2]['High'] and
            recent.iloc[i]['High'] > recent.iloc[i+1]['High'] and
            recent.iloc[i]['High'] > recent.iloc[i+2]['High']):
            peaks.append({
                'date': str(recent.iloc[i]['Date']),
                'price': float(recent.iloc[i]['High']),
                'index': i
            })
        
        if (recent.iloc[i]['Low'] < recent.iloc[i-1]['Low'] and
            recent.iloc[i]['Low'] < recent.iloc[i-2]['Low'] and
            recent.iloc[i]['Low'] < recent.iloc[i+1]['Low'] and
            recent.iloc[i]['Low'] < recent.iloc[i+2]['Low']):
            troughs.append({
                'date': str(recent.iloc[i]['Date']),
                'price': float(recent.iloc[i]['Low']),
                'index': i
            })
    
    return {'peaks': peaks[-5:], 'troughs': troughs[-5:]}


def calculate_fibonacci_retracements(start: float, end: float) -> Dict:
    """計算斐波那契回調位"""
    diff = abs(end - start)
    levels = [0, 0.236, 0.382, 0.5, 0.618, 0.786, 1]
    
    if start < end:
        base = start
    else:
        base = end
    
    return {f'fib_{int(l*100)}': round(base + diff * l, 2) for l in levels}


def analyze_wave_structure(df: pd.DataFrame) -> Dict:
    """分析波浪結構"""
    if df is None or len(df) < 30:
        return {'error': 'Insufficient data'}
    
    peaks_troughs = find_wave_peaks(df)
    peaks = peaks_troughs['peaks']
    troughs = peaks_troughs['troughs']
    
    if len(peaks) >= 2 and len(troughs) >= 2:
        wave_count = min(len(peaks), len(troughs))
        
        if peaks[0]['price'] > troughs[0]['price'] > peaks[1]['price']:
            wave_type = 'abc_correction'
        elif troughs[0]['price'] < peaks[0]['price'] < troughs[1]['price']:
            wave_type = 'impulse_wave'
        else:
            wave_type = 'unclear'
        
        if len(peaks) >= 2:
            fib = calculate_fibonacci_retracements(peaks[0]['price'], peaks[-1]['price'])
        else:
            fib = {}
        
        current = df.iloc[-1]
        current_price = current['Close']
        
        nearest_supports = []
        for t in troughs:
            if t['price'] < current_price:
                nearest_supports.append(t['price'])
        
        nearest_resistances = []
        for p in peaks:
            if p['price'] > current_price:
                nearest_resistances.append(p['price'])
        
        return {
            'wave_type': wave_type,
            'wave_count': wave_count,
            'fibonacci': fib,
            'nearest_support': nearest_supports[0] if nearest_supports else None,
            'nearest_resistance': nearest_resistances[0] if nearest_resistances else None,
            'peaks': peaks,
            'troughs': troughs
        }
    
    return {
        'wave_type': 'unclear',
        'wave_count': 0,
        'fibonacci': {},
        'nearest_support': None,
        'nearest_resistance': None
    }


def detect_elliott_waves(df: pd.DataFrame) -> Dict:
    """偵測艾略特波浪"""
    if df is None or len(df) < 60:
        return {'pattern': None, 'wave': None}
    
    recent = df.tail(60)
    
    price_start = recent.iloc[0]['Close']
    price_end = recent.iloc[-1]['Close']
    price_high = recent['High'].max()
    price_low = recent['Low'].min()
    
    change_pct = (price_end - price_start) / price_start * 100
    
    if change_pct > 20:
        return {
            'pattern': 'impulse_wave',
            'wave': 'wave_5',
            'description': '可能處於第 5 浪上漲',
            'target': round(price_high * 1.382, 2)
        }
    elif change_pct > 10:
        return {
            'pattern': ' impulse_wave',
            'wave': 'wave_3',
            'description': '可能處於第 3 浪上漲',
            'target': round(price_high * 1.618, 2)
        }
    elif change_pct < -20:
        return {
            'pattern': 'impulse_wave',
            'wave': 'wave_C',
            'description': '可能處於 C 浪下跌',
            'target': round(price_low * 0.618, 2)
        }
    elif change_pct < -10:
        return {
            'pattern': 'corrective_wave',
            'wave': 'wave_B',
            'description': '可能處於 B 浪反彈',
            'target': round(price_high * 0.786, 2)
        }
    else:
        return {
            'pattern': 'consolidation',
            'wave': None,
            'description': '處於盤整期',
            'target': None
        }


def golden_ratio_analysis(df: pd.DataFrame) -> Dict:
    """黃金分割率分析"""
    if df is None or len(df) < 20:
        return {'targets': []}
    
    recent = df.tail(20)
    
    high = recent['High'].max()
    low = recent['Low'].min()
    
    current = df.iloc[-1]['Close']
    
    targets = [
        ('阻力 1', round(low + (high - low) * 0.382, 2)),
        ('阻力 2', round(low + (high - low) * 0.5, 2)),
        ('阻力 3', round(low + (high - low) * 0.618, 2)),
        ('阻力 4', round(low + (high - low) * 0.786, 2)),
        ('阻力 5', round(high, 2)),
    ]
    
    if current > low + (high - low) * 0.618:
        action = '強勢，建議續抱'
    elif current > low + (high - low) * 0.382:
        action = '中性，建議觀望'
    else:
        action = '弱勢，建議觀望'
    
    return {
        'current': round(current, 2),
        'high': round(high, 2),
        'low': round(low, 2),
        'targets': targets,
        'recommendation': action
    }