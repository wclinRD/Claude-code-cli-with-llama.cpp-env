"""
Technical Indicators Module - 技術指標
RSI, MACD, KD, OBV
"""

import pandas as pd
import numpy as np
from typing import Dict, List


def calculate_rsi(df: pd.DataFrame, period: int = 14) -> pd.DataFrame:
    """計算 RSI"""
    if df is None or len(df) < period:
        return df
    
    df = df.copy()
    
    delta = df['Close'].diff()
    
    gain = delta.where(delta > 0, 0)
    loss = -delta.where(delta < 0, 0)
    
    avg_gain = gain.rolling(window=period, min_periods=period).mean()
    avg_loss = loss.rolling(window=period, min_periods=period).mean()
    
    rs = avg_gain / avg_loss
    df['RSI'] = 100 - (100 / (1 + rs))
    
    return df


def calculate_macd(df: pd.DataFrame, fast: int = 12, slow: int = 26, signal: int = 9) -> pd.DataFrame:
    """計算 MACD"""
    if df is None or len(df) < slow:
        return df
    
    df = df.copy()
    
    ema_fast = df['Close'].ewm(span=fast, adjust=False).mean()
    ema_slow = df['Close'].ewm(span=slow, adjust=False).mean()
    
    df['MACD'] = ema_fast - ema_slow
    df['Signal'] = df['MACD'].ewm(span=signal, adjust=False).mean()
    df['Histogram'] = df['MACD'] - df['Signal']
    
    return df


def calculate_kd(df: pd.DataFrame, n: int = 9, m1: int = 3, m2: int = 3) -> pd.DataFrame:
    """計算 KD 隨機指標"""
    if df is None or len(df) < n:
        return df
    
    df = df.copy()
    
    low_n = df['Low'].rolling(window=n).min()
    high_n = df['High'].rolling(window=n).max()
    
    rsv = (df['Close'] - low_n) / (high_n - low_n) * 100
    rsv = rsv.fillna(50)
    
    df['K'] = rsv.ewm(span=m1, adjust=False).mean()
    df['D'] = df['K'].ewm(span=m2, adjust=False).mean()
    df['J'] = 3 * df['K'] - 2 * df['D']
    
    return df


def calculate_obv(df: pd.DataFrame) -> pd.DataFrame:
    """計算 OBV 能量潮"""
    if df is None or len(df) < 2:
        return df
    
    df = df.copy()
    
    obv = [0]
    for i in range(1, len(df)):
        if df.iloc[i]['Close'] > df.iloc[i-1]['Close']:
            obv.append(obv[-1] + df.iloc[i]['Volume'])
        elif df.iloc[i]['Close'] < df.iloc[i-1]['Close']:
            obv.append(obv[-1] - df.iloc[i]['Volume'])
        else:
            obv.append(obv[-1])
    
    df['OBV'] = obv
    df['OBV_MA'] = df['OBV'].rolling(window=20).mean()
    
    return df


def analyze_signals(df: pd.DataFrame) -> Dict:
    """分析技術指標訊號"""
    if df is None or len(df) < 30:
        return {'error': 'Insufficient data'}
    
    df = calculate_rsi(df)
    df = calculate_macd(df)
    df = calculate_kd(df)
    df = calculate_obv(df)
    
    latest = df.iloc[-1]
    prev = df.iloc[-2]
    
    signals = []
    
    rsi = latest.get('RSI')
    if rsi:
        if rsi > 70:
            signals.append({'indicator': 'RSI', 'signal': 'overbought', 'value': round(rsi, 2), 'action': 'sell'})
        elif rsi < 30:
            signals.append({'indicator': 'RSI', 'signal': 'oversold', 'value': round(rsi, 2), 'action': 'buy'})
        else:
            signals.append({'indicator': 'RSI', 'signal': 'neutral', 'value': round(rsi, 2), 'action': 'hold'})
    
    macd = latest.get('MACD')
    signal_line = latest.get('Signal')
    macd_prev = prev.get('MACD')
    signal_prev = prev.get('Signal')
    
    if macd and signal_line:
        if macd > signal_line and macd_prev <= signal_prev:
            signals.append({'indicator': 'MACD', 'signal': 'golden_cross', 'value': f"MACD:{macd:.2f}, Signal:{signal_line:.2f}", 'action': 'buy'})
        elif macd < signal_line and macd_prev >= signal_prev:
            signals.append({'indicator': 'MACD', 'signal': 'death_cross', 'value': f"MACD:{macd:.2f}, Signal:{signal_line:.2f}", 'action': 'sell'})
        else:
            direction = 'bullish' if macd > signal_line else 'bearish'
            signals.append({'indicator': 'MACD', 'signal': direction, 'value': f"MACD:{macd:.2f}, Signal:{signal_line:.2f}", 'action': 'hold'})
    
    k = latest.get('K')
    d = latest.get('D')
    k_prev = prev.get('K')
    d_prev = prev.get('D')
    
    if k and d:
        if k > d and k_prev <= d_prev:
            signals.append({'indicator': 'KD', 'signal': 'golden_cross', 'value': f"K:{k:.2f}, D:{d:.2f}", 'action': 'buy'})
        elif k < d and k_prev >= d_prev:
            signals.append({'indicator': 'KD', 'signal': 'death_cross', 'value': f"K:{k:.2f}, D:{d:.2f}", 'action': 'sell'})
        else:
            direction = 'bullish' if k > d else 'bearish'
            signals.append({'indicator': 'KD', 'signal': direction, 'value': f"K:{k:.2f}, D:{d:.2f}", 'action': 'hold'})
    
    return {
        'rsi': round(rsi, 2) if rsi else None,
        'macd': round(macd, 2) if macd else None,
        'signal': round(signal_line, 2) if signal_line else None,
        'histogram': round(latest.get('Histogram', 0), 2),
        'k': round(k, 2) if k else None,
        'd': round(d, 2) if d else None,
        'j': round(latest.get('J', 0), 2),
        'obv': round(latest.get('OBV', 0)),
        'signals': signals
    }


def detect_divergence(df: pd.DataFrame, indicator: str = 'RSI', lookback: int = 30) -> Dict:
    """偵測背離"""
    if df is None or len(df) < lookback * 2:
        return {'divergence': None}
    
    recent = df.tail(lookback)
    
    price_low = recent['Low'].min()
    price_high = recent['High'].max()
    price_current = recent.iloc[-1]['Close']
    
    if indicator == 'RSI':
        df = calculate_rsi(df)
        rsi_low = recent['RSI'].min()
        rsi_high = recent['RSI'].max()
        rsi_current = recent.iloc[-1]['RSI']
        
        if price_current < price_low * 1.05 and rsi_current > rsi_high * 0.9:
            return {'divergence': 'bullish_divergence', 'description': '價格新低但 RSI 未破低'}
        
        if price_current > price_high * 0.95 and rsi_current < rsi_high * 1.1:
            return {'divergence': 'bearish_divergence', 'description': '價格新高但 RSI 未破高'}
    
    return {'divergence': None}