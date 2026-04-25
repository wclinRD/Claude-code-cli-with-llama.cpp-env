"""
Wave Theory Module - 波浪理論
艾略特波浪、推動浪、修正浪、黄金分割率
"""

import pandas as pd
import numpy as np
from typing import Dict, List, Tuple


def find_wave_peaks(df: pd.DataFrame, lookback: int = 60) -> Dict:
    """尋找波浪的高低點 - 增強版"""
    if df is None or len(df) < 10:
        return {'peaks': [], 'troughs': []}
    
    recent = df.tail(lookback).copy().reset_index(drop=True)
    
    peaks = []
    troughs = []
    
    # 使用多尺度峰值檢測
    for window in [3, 5, 7]:
        for i in range(window // 2, len(recent) - window // 2):
            window_data = recent.iloc[i-window//2:i+window//2+1]
            is_peak = recent.iloc[i]['High'] == window_data['High'].max()
            is_trough = recent.iloc[i]['Low'] == window_data['Low'].min()
            
            if is_peak:
                peaks.append({
                    'date': str(recent.iloc[i]['Date']),
                    'price': float(recent.iloc[i]['High']),
                    'index': i,
                    'window': window
                })
            if is_trough:
                troughs.append({
                    'date': str(recent.iloc[i]['Date']),
                    'price': float(recent.iloc[i]['Low']),
                    'index': i,
                    'window': window
                })
    
    # 去重，按價格排序
    peaks = sorted(peaks, key=lambda x: x['price'], reverse=True)[:8]
    troughs = sorted(troughs, key=lambda x: x['price'])[:8]
    
    return {'peaks': peaks, 'troughs': troughs}


def detect_wave_pattern(df: pd.DataFrame, peaks: List, troughs: List) -> Tuple[str, str]:
    """檢測波浪模式 - 增強版"""
    if not peaks or not troughs:
        return 'unclear', 'unknown'
    
    current_price = df.iloc[-1]['Close']
    
    # 收集所有頂底點，按時間排序
    all_points = []
    for p in peaks:
        all_points.append(('peak', p['index'], p['price']))
    for t in troughs:
        all_points.append(('trough', t['index'], t['price']))
    
    all_points.sort(key=lambda x: x[1])
    
    if len(all_points) < 4:
        return 'unclear', 'insufficient_data'
    
    # 分析趨勢方向
    recent_points = all_points[-6:]  # 取最後6個點
    if len(recent_points) >= 4:
        # 計算總漲幅
        first_price = recent_points[0][2]
        last_price = recent_points[-1][2]
        change = (last_price - first_price) / first_price * 100
        
        # 識別推動浪 (5浪結構)
        if change > 15:
            # 計算高低點交替次數
            high_count = sum(1 for pt in recent_points if pt[0] == 'peak')
            low_count = sum(1 for pt in recent_points if pt[0] == 'trough')
            
            if high_count >= 3 and low_count >= 2:
                # 判斷在哪一浪
                if current_price > last_price * 0.95:
                    return 'impulse_wave', 'wave_5_extended'
                elif current_price > recent_points[-2][2]:
                    return 'impulse_wave', 'wave_4'
                elif current_price > recent_points[-3][2]:
                    return 'impulse_wave', 'wave_3'
                else:
                    return 'impulse_wave', 'wave_1_or_5'
            else:
                return 'impulse_wave', 'early_stage'
        
        # 識別修正浪
        elif change < -15:
            return 'corrective_wave', 'abc_correction'
        
        # 盤整
        elif abs(change) < 8:
            return 'consolidation', 'triangle_or_flat'
        
        # 趨勢不明但有波動
        else:
            return 'unclear', 'mixed_signals'
    
    return 'unclear', 'unknown'


def identify_elliott_wave(df: pd.DataFrame, peaks: List, troughs: List) -> str:
    """識別艾略特波浪位置"""
    if len(peaks) < 3 or len(troughs) < 3:
        return 'wave_1'
    
    current_price = df.iloc[-1]['Close']
    
    # 按價格排序找出最高/最低點
    highest = max(p['price'] for p in peaks)
    lowest = min(t['price'] for t in troughs)
    range_pct = (highest - lowest) / lowest * 100
    
    # 根據当前位置判断
    if current_price > highest * 0.95:
        if range_pct > 30:
            return 'wave_5_completion'
        else:
            return 'wave_3_extension'
    elif current_price > highest * 0.78:
        return 'wave_4'
    elif current_price > (highest + lowest) / 2:
        return 'wave_3'
    elif current_price > lowest * 1.22:
        return 'wave_2'
    else:
        return 'wave_1'


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
    """分析波浪結構 - 增強版"""
    if df is None or len(df) < 30:
        return {'error': 'Insufficient data'}
    
    peaks_troughs = find_wave_peaks(df)
    peaks = peaks_troughs['peaks']
    troughs = peaks_troughs['troughs']
    
    current = df.iloc[-1]
    current_price = current['Close']
    
    # 使用新的模式檢測
    wave_type, wave_stage = detect_wave_pattern(df, peaks, troughs)
    
    # 識別艾略特波浪位置
    if wave_type != 'unclear':
        elliott_pos = identify_elliott_wave(df, peaks, troughs)
    else:
        # 根據價格變化推斷
        if len(df) >= 60:
            price_start = df.iloc[-60]['Close']
            change = (current_price - price_start) / price_start * 100
            if change > 20:
                elliott_pos = 'wave_5'
            elif change > 10:
                elliott_pos = 'wave_3'
            elif change < -20:
                elliott_pos = 'wave_C'
            elif change < -10:
                elliott_pos = 'wave_A'
            else:
                elliott_pos = 'consolidation'
        else:
            elliott_pos = 'unknown'
    
    # 計算支撐與壓力
    nearest_supports = []
    for t in troughs:
        if t['price'] < current_price:
            nearest_supports.append(t['price'])
    
    nearest_resistances = []
    for p in peaks:
        if p['price'] > current_price:
            nearest_resistances.append(p['price'])
    
    # 計算斐波那契
    if peaks and troughs:
        high = max(p['price'] for p in peaks)
        low = min(t['price'] for t in troughs)
        fib = calculate_fibonacci_retracements(low, high)
    else:
        fib = {}
    
    wave_count = min(len(peaks), len(troughs))
    
    # 轉換為中文描述
    type_name = {
        'impulse_wave': '推動浪',
        'corrective_wave': '修正浪',
        'consolidation': '盤整',
        'unclear': '待確認'
    }.get(wave_type, '待確認')
    
    stage_name = {
        'wave_5_extended': '第5浪延伸',
        'wave_4': '第4浪回調',
        'wave_3': '第3浪上漲',
        'wave_1_or_5': '第1浪或第5浪',
        'early_stage': '初期上漲',
        'abc_correction': 'ABC修正',
        'triangle_or_flat': '三角整理',
        'mixed_signals': '混合訊號',
        'insufficient_data': '數據不足',
        'unknown': '待確認'
    }.get(wave_stage, '待確認')
    
    return {
        'wave_type': type_name,
        'wave_stage': stage_name,
        'wave_count': wave_count,
        'elliott_position': elliott_pos,
        'fibonacci': fib,
        'nearest_support': nearest_supports[0] if nearest_supports else None,
        'nearest_resistance': nearest_resistances[0] if nearest_resistances else None,
        'peaks': peaks[:5],
        'troughs': troughs[:5]
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


def predict_wave_progression(df: pd.DataFrame, wave_type: str, current_wave: str) -> Dict:
    """預測波浪後續走勢"""
    if df is None or len(df) < 20:
        return {'forecast': '數據不足'}
    
    current_price = df.iloc[-1]['Close']
    recent = df.tail(60)
    
    high = recent['High'].max()
    low = recent['Low'].min()
    range_val = high - low
    
    # 根據當前波浪位置預測
    forecasts = []
    
    if wave_type in ['推動浪', 'impulse_wave']:
        if 'wave_5' in current_wave or '延伸' in current_wave:
            # 第5浪可能結束，進入修正
            forecasts = [
                {
                    'scenario': '樂觀',
                    'probability': 0.25,
                    'description': '第5浪延伸，繼續創高',
                    'target': round(current_price * 1.1, 2),
                    'stop_loss': round(high * 0.95, 2)
                },
                {
                    'scenario': '正常',
                    'probability': 0.50,
                    'description': '第5浪結束，拉回修正A浪',
                    'target': round(high * 0.809, 2),
                    'stop_loss': round(high, 2)
                },
                {
                    'scenario': '保守',
                    'probability': 0.25,
                    'description': '大幅回調，測試第4浪支撐',
                    'target': round(high * 0.618, 2),
                    'stop_loss': round(high * 0.95, 2)
                }
            ]
        elif 'wave_3' in current_wave:
            # 第3浪之後還有第5浪
            target_5 = round(high * 1.382, 2)
            forecasts = [
                {
                    'scenario': '樂觀',
                    'probability': 0.60,
                    'description': '第3浪延續，挑戰第5浪目標',
                    'target': target_5,
                    'stop_loss': round(current_price * 0.95, 2)
                },
                {
                    'scenario': '正常',
                    'probability': 0.30,
                    'description': '拉回第4浪後繼續上漲',
                    'target': round(high * 1.236, 2),
                    'stop_loss': round(low + range_val * 0.382, 2)
                },
                {
                    'scenario': '保守',
                    'probability': 0.10,
                    'description': '提前結束，上演失敗第5浪',
                    'target': round(high, 2),
                    'stop_loss': round(low + range_val * 0.5, 2)
                }
            ]
        elif 'wave_1' in current_wave or 'early' in current_wave:
            # 初期上漲
            target_3 = round(high * 1.618, 2)
            forecasts = [
                {
                    'scenario': '樂觀',
                    'probability': 0.70,
                    'description': '第1浪確認，邁向第3浪主升段',
                    'target': target_3,
                    'stop_loss': round(current_price * 0.92, 2)
                },
                {
                    'scenario': '正常',
                    'probability': 0.25,
                    'description': '回調後繼續上漲',
                    'target': round(high * 1.236, 2),
                    'stop_loss': round(low + range_val * 0.236, 2)
                },
                {
                    'scenario': '保守',
                    'probability': 0.05,
                    'description': '第1浪失敗，反向測試低點',
                    'target': round(low, 2),
                    'stop_loss': round(low * 0.95, 2)
                }
            ]
        else:
            forecasts = [
                {
                    'scenario': '樂觀',
                    'probability': 0.45,
                    'description': '持續上漲，挑戰前高',
                    'target': round(high * 1.1, 2),
                    'stop_loss': round(low + range_val * 0.5, 2)
                },
                {
                    'scenario': '正常',
                    'probability': 0.40,
                    'description': '區間整理後突破',
                    'target': round(high * 1.05, 2),
                    'stop_loss': round(low + range_val * 0.382, 2)
                },
                {
                    'scenario': '保守',
                    'probability': 0.15,
                    'description': '拉回測試支撐',
                    'target': round(low + range_val * 0.618, 2),
                    'stop_loss': round(low, 2)
                }
            ]
    
    elif wave_type in ['修正浪', 'corrective_wave', 'ABC修正']:
        forecasts = [
            {
                'scenario': '樂觀',
                'probability': 0.30,
                'description': 'B浪反彈，測試前波高點',
                'target': round(high * 0.786, 2),
                'stop_loss': round(low, 2)
            },
            {
                'scenario': '正常',
                'probability': 0.50,
                'description': 'C浪下跌，完成修正',
                'target': round(low, 2),
                'stop_loss': round(high * 0.95, 2)
            },
            {
                'scenario': '保守',
                'probability': 0.20,
                'description': '擴大下跌，測試前低',
                'target': round(low * 0.9, 2),
                'stop_loss': round(low * 0.95, 2)
            }
        ]
    
    elif wave_type in ['盤整', 'consolidation']:
        forecasts = [
            {
                'scenario': '樂觀',
                'probability': 0.35,
                'description': '突破上軌，結束盤整',
                'target': round(high * 1.08, 2),
                'stop_loss': round(low, 2)
            },
            {
                'scenario': '正常',
                'probability': 0.45,
                'description': '持續盤整區間震盪',
                'target': round(high, 2),
                'stop_loss': round(low, 2)
            },
            {
                'scenario': '保守',
                'probability': 0.20,
                'description': '跌破下軌，進入下跌',
                'target': round(low * 0.92, 2),
                'stop_loss': round(high, 2)
            }
        ]
    
    else:  # 待確認
        forecasts = [
            {
                'scenario': '樂觀',
                'probability': 0.40,
                'description': '確認多頭，挑戰前高',
                'target': round(high * 1.1, 2),
                'stop_loss': round(low * 0.95, 2)
            },
            {
                'scenario': '正常',
                'probability': 0.35,
                'description': '區間震盪',
                'target': round((high + low) / 2, 2),
                'stop_loss': round(low, 2)
            },
            {
                'scenario': '保守',
                'probability': 0.25,
                'description': '確認空頭，跌破支撐',
                'target': round(low * 0.9, 2),
                'stop_loss': round(high, 2)
            }
        ]
    
    # 計算時間預測 (假設每浪約 10-20 交易日)
    avg_bars_per_wave = 15
    bar_count = len(recent)
    
    time_estimate = {
        'short': f'{int(avg_bars_per_wave * 0.8)}-{int(avg_bars_per_wave * 1.2)}交易日',
        'medium': f'{int(avg_bars_per_wave * 2)}-{int(avg_bars_per_wave * 3)}交易日',
        'long': f'{int(avg_bars_per_wave * 4)}-{int(avg_bars_per_wave * 6)}交易日'
    }
    
    return {
        'current_price': round(current_price, 2),
        'current_wave': current_wave,
        'wave_type': wave_type,
        'forecasts': forecasts,
        'time_estimate': time_estimate,
        'key_levels': {
            'current_high': round(high, 2),
            'current_low': round(low, 2),
            'range': round(range_val, 2)
        }
    }