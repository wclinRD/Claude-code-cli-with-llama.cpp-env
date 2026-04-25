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
    
    更嚴謹的包含處理邏輯：
    - 上升筆：後一根 K 線的低點 >= 前一根 K 線的低點
    - 下降筆：後一根 K 線的高點 <= 前一根 K 線的高點
    """
    if df is None or len(df) < min_bars:
        return []
    
    pens = []
    i = 0
    
    while i < len(df) - min_bars:
        found_pen = False
        
        for j in range(i + min_bars - 1, len(df)):
            direction = None
            
            prev_high = df.iloc[i]['High']
            prev_low = df.iloc[i]['Low']
            valid = True
            
            for k in range(i, j + 1):
                curr_high = df.iloc[k]['High']
                curr_low = df.iloc[k]['Low']
                
                if direction is None:
                    if curr_high > prev_high and curr_low >= prev_low:
                        direction = 'up'
                    elif curr_low < prev_low and curr_high <= prev_high:
                        direction = 'down'
                    else:
                        valid = False
                        break
                else:
                    if direction == 'up':
                        if curr_low < prev_low:
                            valid = False
                            break
                        prev_high = curr_high
                        prev_low = curr_low
                    else:
                        if curr_high > prev_high:
                            valid = False
                            break
                        prev_high = curr_high
                        prev_low = curr_low
            
            if valid and direction:
                pen_data = {
                    'start': str(df.iloc[i]['Date']),
                    'end': str(df.iloc[j]['Date']),
                    'type': direction,
                }
                if direction == 'up':
                    pen_data['high'] = float(df.iloc[j]['High'])
                else:
                    pen_data['low'] = float(df.iloc[j]['Low'])
                
                pens.append(pen_data)
                i = j + 1
                found_pen = True
                break
        
        if not found_pen:
            i += 1
    
    return pens[-10:]


def detect_笔破壞(pens: List[Dict], df: pd.DataFrame) -> List[Dict]:
    """
    檢測筆破壞
    筆破壞：原本的筆被後續筆突破
    
    上升筆破壞：上升筆的最高點被後續下降筆突破
    下降筆破壞：下降筆的最低點被後續上升筆突破
    """
    if not pens or len(pens) < 2:
        return []
    
    destructions = []
    
    for i in range(len(pens) - 1):
        current_pen = pens[i]
        next_pen = pens[i + 1]
        
        if current_pen['type'] == 'up':
            current_high = current_pen['high']
            if next_pen['type'] == 'down':
                destroyed_high = next_pen.get('low', 0)
                if destroyed_high < current_high:
                    destructions.append({
                        'pen_index': i,
                        'destroyed_pen': current_pen,
                        'destroying_pen': next_pen,
                        'type': 'up_broken',
                        'break_high': float(current_high),
                        'break_low': float(destroyed_high)
                    })
        else:
            current_low = current_pen['low']
            if next_pen['type'] == 'up':
                destroyed_low = next_pen.get('high', float('inf'))
                if destroyed_low > current_low:
                    destructions.append({
                        'pen_index': i,
                        'destroyed_pen': current_pen,
                        'destroying_pen': next_pen,
                        'type': 'down_broken',
                        'break_low': float(current_low),
                        'break_high': float(destroyed_low)
                    })
    
    return destructions


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
    pen_destructions = detect_笔破壞(pens, df)
    
    return {
        'pens': pens,
        'segments': segments,
        'zhongshus': zhongshus,
        'trend': trend,
        'pen_destructions': pen_destructions
    }


def identify_head_shoulders(df: pd.DataFrame, min_bars: int = 20) -> List[Dict]:
    """
    識別頭肩頂/底
    頭肩頂：中間高點高於兩側高點
    頭肩底：中間低點低於兩側低點
    """
    if df is None or len(df) < min_bars:
        return []
    
    patterns = []
    
    for window in range(30, min(60, len(df) // 2), 5):
        for i in range(len(df) - window):
            segment = df.iloc[i:i + window]
            highs = segment['High'].values
            lows = segment['Low'].values
            
            left_high_idx = np.argmax(highs[:len(highs)//3])
            center_high_idx = np.argmax(highs[len(highs)//3:2*len(highs)//3]) + len(highs)//3
            right_high_idx = np.argmax(highs[2*len(highs)//3:]) + 2*len(highs)//3
            
            left_low_idx = np.argmin(lows[:len(lows)//3])
            center_low_idx = np.argmin(lows[len(lows)//3:2*len(lows)//3]) + len(lows)//3
            right_low_idx = np.argmin(lows[2*len(lows)//3:]) + 2*len(lows)//3
            
            center_high = highs[center_high_idx]
            if (highs[left_high_idx] < center_high and 
                highs[right_high_idx] < center_high and
                center_high > np.mean(highs)):
                patterns.append({
                    'type': 'head_and_shoulders_top',
                    'left_shoulder': float(highs[left_high_idx]),
                    'head': float(center_high),
                    'right_shoulder': float(highs[right_high_idx]),
                    'start': str(segment.iloc[0]['Date']),
                    'end': str(segment.iloc[-1]['Date'])
                })
            
            center_low = lows[center_low_idx]
            if (lows[left_low_idx] > center_low and 
                lows[right_low_idx] > center_low and
                center_low < np.mean(lows)):
                patterns.append({
                    'type': 'head_and_shoulders_bottom',
                    'left_shoulder': float(lows[left_low_idx]),
                    'head': float(center_low),
                    'right_shoulder': float(lows[right_low_idx]),
                    'start': str(segment.iloc[0]['Date']),
                    'end': str(segment.iloc[-1]['Date'])
                })
    
    if patterns:
        return patterns[:3]
    return []


def identify_flag(df: pd.DataFrame, min_bars: int = 10) -> List[Dict]:
    """
    識別旗型/旗竿
    旗竿：急劇的價格變動
    旗形：整理區間，通常與趨勢相反
    """
    if df is None or len(df) < min_bars:
        return []
    
    flags = []
    
    for i in range(min_bars, len(df) - min_bars):
        pole_start = df.iloc[:i]
        flag_start = df.iloc[i:]
        
        pole_change = (pole_start.iloc[-1]['Close'] - pole_start.iloc[0]['Close']) / pole_start.iloc[0]['Close']
        
        if abs(pole_change) > 0.03:
            flag_range = flag_start['High'].max() - flag_start['Low'].min()
            flag_pct = flag_range / pole_start.iloc[0]['Close']
            
            if flag_pct < 0.02:
                flags.append({
                    'type': 'bull_flag' if pole_change > 0 else 'bear_flag',
                    'pole_change_pct': float(pole_change * 100),
                    'flag_range_pct': float(flag_pct * 100),
                    'start': str(pole_start.iloc[0]['Date']),
                    'pole_end': str(pole_start.iloc[-1]['Date']),
                    'flag_start': str(flag_start.iloc[0]['Date']),
                    'flag_end': str(flag_start.iloc[-1]['Date'])
                })
    
    if flags:
        return flags[:3]
    return []


def identify_wedge(df: pd.DataFrame, min_bars: int = 15) -> List[Dict]:
    """
    識別楔形整理
    楔形：價格在收斂的區間內整理
    上升楔形：通常預示反轉下跌
    下降楔形：通常預示反轉上漲
    """
    if df is None or len(df) < min_bars:
        return []
    
    wedges = []
    
    for window in range(min_bars, min(40, len(df) // 2), 5):
        for i in range(len(df) - window):
            segment = df.iloc[i:i + window]
            
            highs = segment['High'].values
            lows = segment['Low'].values
            
            high_slope = (highs[-1] - highs[0]) / len(highs)
            low_slope = (lows[-1] - lows[0]) / len(lows)
            
            if high_slope < 0 and low_slope > 0:
                if abs(high_slope - low_slope) < 0.001:
                    wedges.append({
                        'type': 'neutral_wedge',
                        'high_slope': float(high_slope),
                        'low_slope': float(low_slope),
                        'start': str(segment.iloc[0]['Date']),
                        'end': str(segment.iloc[-1]['Date'])
                    })
                elif high_slope > low_slope:
                    wedges.append({
                        'type': 'rising_wedge',
                        'high_slope': float(high_slope),
                        'low_slope': float(low_slope),
                        'start': str(segment.iloc[0]['Date']),
                        'end': str(segment.iloc[-1]['Date'])
                    })
                else:
                    wedges.append({
                        'type': 'falling_wedge',
                        'high_slope': float(high_slope),
                        'low_slope': float(low_slope),
                        'start': str(segment.iloc[0]['Date']),
                        'end': str(segment.iloc[-1]['Date'])
                    })
    
    if wedges:
        return wedges[:3]
    return []