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


def detect_w底_m頭(df: pd.DataFrame) -> Dict:
    """詳細偵測W底與M頭形態，含頸線計算與階段判斷及後續走勢預測"""
    if df is None or len(df) < 40:
        return {}

    recent = df.tail(60).reset_index(drop=True)
    closes = recent['Close'].values
    highs = recent['High'].values
    lows = recent['Low'].values

    result = {}

    def w底_predict(stage, depth, neckline, current_price, breakout_pct, left_bottom, right_bottom):
        predictions = {
            '形成中': {
                'likely_move': '準備向上突破',
                'probability': '65%',
                '注意': [
                    f'頸線 $%.2f 是關鍵突破點' % neckline,
                    '突破需要放量配合，否則容易失敗',
                    f'突破後上看 $%.2f' % (neckline + depth),
                    '兩底之中較低者 $%.2f 是最後防線' % min(left_bottom, right_bottom)
                ],
                'time_estimate': '1-4週內'
            },
            '回踩中': {
                'likely_move': '回檔找支撐',
                'probability': '70%',
                '注意': [
                    f'頸線 $%.2f 現在變成支撐' % neckline,
                    '股價回測時不要慌，通常是加碼機會',
                    f'守住 $%.2f 就沒問題' % (neckline * 0.98),
                    '如果跌破頸線就要小心了'
                ],
                'time_estimate': '1-3週'
            },
            '突破確認': {
                'likely_move': '漲向目標，可能回調',
                'probability': '75%',
                '注意': [
                    f'第一站 $%.2f (+%.0f%%)' % (neckline + depth * 0.5, depth * 0.5 / neckline * 100),
                    f'終點站 $%.2f (+%.0f%%)' % (neckline + depth, depth / neckline * 100),
                    '漲多後常會回檔整理38-50%',
                    '回檔守住頸線就是買點'
                ],
                'time_estimate': '3-8週'
            },
            '大幅突破': {
                'likely_move': '很強，續漲機率高',
                'probability': '80%',
                '注意': [
                    '動能很強，不要逆勢做空',
                    '可以設移動停損續抱',
                    f'目標 $%.2f (+%.0f%%)' % (neckline + depth, depth / neckline * 100),
                    'RSI > 80 小心短線拉回'
                ],
                'time_estimate': '2-4週'
            }
        }
        pred = predictions.get(stage, predictions['突破確認'])
        pred['current_position'] = '現價 $%.2f，頸線 $%.2f' % (current_price, neckline)
        return pred

    def m頭_predict(stage, depth, neckline, current_price, breakout_pct, left_top, right_top):
        predictions = {
            '形成中': {
                'likely_move': '準備向下突破',
                'probability': '65%',
                '注意': [
                    f'頸線 $%.2f 是關鍵支撐' % neckline,
                    '跌破需要放量，否則可能是假跌破',
                    f'跌破後下看 $%.2f' % (neckline - depth),
                    '兩頭之中較高者 $%.2f 是最後防線' % max(left_top, right_top)
                ],
                'time_estimate': '1-4週內'
            },
            '反彈中': {
                'likely_move': '反彈測試壓力',
                'probability': '70%',
                '注意': [
                    f'頸線 $%.2f 是重要壓力' % neckline,
                    '反彈到這裡常會遇到賣壓',
                    f'無法突破的話，下看 $%.2f' % (neckline - depth * 0.5),
                    '反彈幅度通常只有跌幅的38-62%'
                ],
                'time_estimate': '1-3週'
            },
            '跌破確認': {
                'likely_move': '跌向目標，可能反彈',
                'probability': '75%',
                '注意': [
                    f'第一站 $%.2f' % (neckline - depth * 0.5),
                    f'終點站 $%.2f' % (neckline - depth),
                    '跌深後常會反彈38-50%',
                    '反彈無法站回頸線就要減碼'
                ],
                'time_estimate': '3-8週'
            },
            '大幅跌破': {
                'likely_move': '很弱，續跌機率高',
                'probability': '80%',
                '注意': [
                    '動能很強，不要逆勢接刀',
                    '等反彈再說，不要急著摸底',
                    f'目標 $%.2f' % (neckline - depth),
                    'RSI < 20 才考慮是否超賣'
                ],
                'time_estimate': '2-4週'
            }
        }
        pred = predictions.get(stage, predictions['跌破確認'])
        pred['current_position'] = '現價 $%.2f，頸線 $%.2f' % (current_price, neckline)
        return pred

    # === W底偵測 ===
    swing_lows_idx = []
    for i in range(5, len(lows) - 5):
        if lows[i] == min(lows[max(0, i-5):i+5]) and lows[i] < lows[i-1] and lows[i] < lows[i+1]:
            swing_lows_idx.append(i)

    if len(swing_lows_idx) >= 2:
        for i in range(len(swing_lows_idx) - 1):
            idx1, idx2 = swing_lows_idx[i], swing_lows_idx[i + 1]
            if abs(lows[idx1] - lows[idx2]) / lows[idx1] < 0.05:
                end_idx = min(max(idx1, idx2) + 30, len(closes))
                peak_between = max(closes[max(idx1, idx2):end_idx])
                if peak_between > max(lows[idx1], lows[idx2]) * 1.1:
                    neckline = peak_between
                    left_bottom = lows[idx1]
                    right_bottom = lows[idx2]
                    current_price = closes[-1]
                    
                    # 計算形態參數
                    depth = neckline - min(left_bottom, right_bottom)
                    breakout_pct = (current_price - neckline) / neckline * 100
                    from_neckline_pullback = (current_price - neckline) / neckline * 100 if current_price < neckline else 0
                    
                    # 判斷階段
                    if breakout_pct < 0:
                        if abs(from_neckline_pullback) < 3:
                            stage = "形成中"
                            stage_desc = "兩底完成，正測試頸線"
                        else:
                            stage = "回踩中"
                            stage_desc = f"突破後回測頸線支撐 ({from_neckline_pullback:.1f}%)"
                    elif breakout_pct < 5:
                        stage = "突破確認"
                        stage_desc = f"已突破頸線，幅度 +{breakout_pct:.1f}%"
                    else:
                        stage = "大幅突破"
                        stage_desc = f"強勢突破，幅度 +{breakout_pct:.1f}%"
                    
                    result['w底'] = {
                        'left_bottom': left_bottom,
                        'right_bottom': right_bottom,
                        'neckline': neckline,
                        'depth': depth,
                        'breakout_pct': breakout_pct,
                        'stage': stage,
                        'stage_desc': stage_desc,
                        'target': round(neckline + depth * 1.0, 2),
                        'target_1': round(neckline + depth * 0.5, 2),
                        'target_2': round(neckline + depth * 1.618, 2),
                        'stop_loss': round(min(left_bottom, right_bottom) * 0.98, 2),
                        'confidence': 0.75
                    }
                    result['w底']['prediction'] = w底_predict(stage, depth, neckline, current_price, breakout_pct, left_bottom, right_bottom)
                    break
    
    # === M頭偵測 ===
    swing_highs_idx = []
    for i in range(5, len(highs) - 5):
        if highs[i] == max(highs[max(0, i-5):i+5]) and highs[i] > highs[i-1] and highs[i] > highs[i+1]:
            swing_highs_idx.append(i)
    
    if len(swing_highs_idx) >= 2:
        for i in range(len(swing_highs_idx) - 1):
            idx1, idx2 = swing_highs_idx[i], swing_highs_idx[i + 1]
            if abs(highs[idx1] - highs[idx2]) / highs[idx1] < 0.05:
                end_idx = min(max(idx1, idx2) + 30, len(closes))
                valley_between = min(closes[max(idx1, idx2):end_idx])
                if valley_between < min(highs[idx1], highs[idx2]) * 0.95:
                    neckline = valley_between
                    left_top = highs[idx1]
                    right_top = highs[idx2]
                    current_price = closes[-1]
                    
                    depth = max(left_top, right_top) - neckline
                    breakout_pct = (neckline - current_price) / neckline * 100
                    
                    if breakout_pct < 0:
                        if abs(breakout_pct) < 3:
                            stage = "形成中"
                            stage_desc = "兩頭完成，正測試頸線"
                        else:
                            stage = "反彈中"
                            stage_desc = f"跌破後測試頸線壓力 ({breakout_pct:.1f}%)"
                    elif breakout_pct < 5:
                        stage = "跌破確認"
                        stage_desc = f"已跌破頸線，幅度 -{breakout_pct:.1f}%"
                    else:
                        stage = "大幅跌破"
                        stage_desc = f"強勢跌破，幅度 -{breakout_pct:.1f}%"
                    
                    result['m頭'] = {
                        'left_top': left_top,
                        'right_top': right_top,
                        'neckline': neckline,
                        'depth': depth,
                        'breakout_pct': breakout_pct,
                        'stage': stage,
                        'stage_desc': stage_desc,
                        'target': round(neckline - depth * 1.0, 2),
                        'target_1': round(neckline - depth * 0.5, 2),
                        'target_2': round(neckline - depth * 1.618, 2),
                        'stop_loss': round(max(left_top, right_top) * 1.02, 2),
                        'confidence': 0.75
                    }
                    result['m頭']['prediction'] = m頭_predict(stage, depth, neckline, current_price, breakout_pct, left_top, right_top)
                    break
    
    return result


def detect_patterns(df: pd.DataFrame) -> Dict:
    """型態辨識"""
    if df is None or len(df) < 30:
        return {'pattern': None, 'confidence': 0}
    
    recent = df.tail(60)
    closes = recent['Close'].values
    highs = recent['High'].values
    lows = recent['Low'].values
    
    current_price = closes[-1]
    start_price = closes[0]
    price_range = highs.max() - lows.min()
    
    if price_range < 1:
        return {'pattern': '盤整', 'confidence': 0.4}
    
    patterns_detected = []
    pattern_details = {}
    
    # W底 / M頭 詳細偵測
    wm_details = detect_w底_m頭(df)
    if wm_details.get('w底'):
        patterns_detected.append(('W底', 0.75))
        pattern_details['w底'] = wm_details['w底']
    if wm_details.get('m頭'):
        patterns_detected.append(('M頭', 0.75))
        pattern_details['m頭'] = wm_details['m頭']
    
    # 上升三角形 (Ascending Triangle) - 高點平坦，低點墊高
    recent_highs = highs[-20:]
    recent_lows = lows[-20:]
    if abs(recent_highs.max() - recent_highs[0]) / recent_highs[0] < 0.03:
        if recent_lows[-1] > recent_lows[0] * 1.03:
            patterns_detected.append(('上升三角', 0.7))
    
    # 下降三角形 (Descending Triangle) - 低點平坦，高點遞減
    if abs(recent_lows.min() - recent_lows[0]) / recent_lows[0] < 0.03:
        if recent_highs[-1] < recent_highs[0] * 0.97:
            patterns_detected.append(('下降三角', 0.7))
    
    # 頭肩頂 (Head and Shoulders)
    if len(swing_highs_idx if 'swing_highs_idx' in dir() else []) >= 3:
        pass
    
    # 多頭趨勢
    if current_price > start_price * 1.15:
        slope = (current_price - start_price) / start_price
        if slope > 0.3:
            patterns_detected.append(('多頭趨勢', 0.8))
        elif slope > 0.15:
            patterns_detected.append(('多頭趨勢', 0.6))
    
    # 空頭趨勢
    if current_price < start_price * 0.85:
        slope = (start_price - current_price) / start_price
        if slope > 0.3:
            patterns_detected.append(('空頭趨勢', 0.8))
        elif slope > 0.15:
            patterns_detected.append(('空頭趨勢', 0.6))
    
    # 突破確認
    if len(recent) >= 20:
        ma20_recent = closes[-20:]
        ma20 = sum(ma20_recent) / len(ma20_recent)
        if current_price > ma20 * 1.05:
            patterns_detected.append(('突破MA20', 0.6))
        elif current_price < ma20 * 0.95:
            patterns_detected.append(('跌破MA20', 0.6))
    
    # 盤整
    if len(patterns_detected) == 0:
        volatility = price_range / closes.mean()
        if volatility < 0.05:
            patterns_detected.append(('區間整理', 0.6))
        else:
            patterns_detected.append(('盤整', 0.4))
    
    best_pattern = max(patterns_detected, key=lambda x: x[1])
    result = {'pattern': best_pattern[0], 'confidence': best_pattern[1]}
    
    if pattern_details:
        result['details'] = pattern_details
    
    return result


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