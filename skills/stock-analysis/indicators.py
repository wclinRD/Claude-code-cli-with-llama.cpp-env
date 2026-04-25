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
    
    rs = np.where(avg_loss == 0, 100, avg_gain / avg_loss)
    df['RSI'] = 100 - (100 / (1 + rs))
    
    df['RSI'] = df['RSI'].fillna(50)
    
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
    
    denom = high_n - low_n
    denom = denom.replace(0, np.nan)
    rsv = (df['Close'] - low_n) / denom * 100
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


def calculate_bollinger_bands(df: pd.DataFrame, period: int = 20, std_dev: float = 2.0) -> pd.DataFrame:
    """計算布林帶"""
    if df is None or len(df) < period:
        return df
    
    df = df.copy()
    
    df['BB_Middle'] = df['Close'].rolling(window=period).mean()
    rolling_std = df['Close'].rolling(window=period).std()
    df['BB_Upper'] = df['BB_Middle'] + (rolling_std * std_dev)
    df['BB_Lower'] = df['BB_Middle'] - (rolling_std * std_dev)
    df['BB_Width'] = (df['BB_Upper'] - df['BB_Lower']) / df['BB_Middle'] * 100
    
    return df


def calculate_atr(df: pd.DataFrame, period: int = 14) -> pd.DataFrame:
    """計算 ATR 平均真實波幅"""
    if df is None or len(df) < period:
        return df
    
    df = df.copy()
    
    high_low = df['High'] - df['Low']
    high_close = abs(df['High'] - df['Close'].shift())
    low_close = abs(df['Low'] - df['Close'].shift())
    
    true_range = pd.concat([high_low, high_close, low_close], axis=1).max(axis=1)
    df['ATR'] = true_range.rolling(window=period).mean()
    df['ATR_Pct'] = (df['ATR'] / df['Close']) * 100
    
    return df


def calculate_williams_r(df: pd.DataFrame, period: int = 14) -> pd.DataFrame:
    """計算威廉指標"""
    if df is None or len(df) < period:
        return df
    
    df = df.copy()
    
    highest_high = df['High'].rolling(window=period).max()
    lowest_low = df['Low'].rolling(window=period).min()
    
    denom = highest_high - lowest_low
    denom = denom.replace(0, np.nan)
    df['Williams_R'] = -((highest_high - df['Close']) / denom) * 100
    df['Williams_R'] = df['Williams_R'].fillna(-50)
    
    return df


def calculate_cci(df: pd.DataFrame, period: int = 20) -> pd.DataFrame:
    """計算 CCI 商品通道指標"""
    if df is None or len(df) < period:
        return df
    
    df = df.copy()
    
    typical_price = (df['High'] + df['Low'] + df['Close']) / 3
    sma = typical_price.rolling(window=period).mean()
    mean_deviation = typical_price.rolling(window=period).apply(lambda x: abs(x - x.mean()).mean())
    
    denom = 0.015 * mean_deviation
    denom = denom.replace(0, np.nan)
    df['CCI'] = (typical_price - sma) / denom
    df['CCI'] = df['CCI'].fillna(0)
    
    return df


def calculate_dmi(df: pd.DataFrame, period: int = 14) -> pd.DataFrame:
    """計算 DMI 趨向指標"""
    if df is None or len(df) < period + 1:
        return df
    
    df = df.copy()
    
    high_diff = df['High'].diff()
    low_diff = -df['Low'].diff()
    
    plus_dm = high_diff.where((high_diff > low_diff) & (high_diff > 0), 0)
    minus_dm = low_diff.where((low_diff > high_diff) & (low_diff > 0), 0)
    
    atr = df['High'] - df['Low']
    atr = atr.rolling(window=period).mean()
    atr = atr.replace(0, np.nan)
    
    df['Plus_DM'] = plus_dm.rolling(window=period).mean()
    df['Minus_DM'] = minus_dm.rolling(window=period).mean()
    
    df['Plus_DI'] = (df['Plus_DM'] / atr) * 100
    df['Minus_DI'] = (df['Minus_DM'] / atr) * 100
    
    di_sum = df['Plus_DI'] + df['Minus_DI']
    di_sum = di_sum.replace(0, np.nan)
    df['DX'] = (abs(df['Plus_DI'] - df['Minus_DI']) / di_sum) * 100
    df['DX'] = df['DX'].fillna(0)
    df['ADX'] = df['DX'].rolling(window=period).mean()
    df['ADX'] = df['ADX'].fillna(0)
    
    return df


def calculate_all_indicators(df: pd.DataFrame) -> pd.DataFrame:
    """計算所有技術指標"""
    df = calculate_rsi(df)
    df = calculate_macd(df)
    df = calculate_kd(df)
    df = calculate_obv(df)
    df = calculate_bollinger_bands(df)
    df = calculate_atr(df)
    df = calculate_williams_r(df)
    df = calculate_cci(df)
    df = calculate_dmi(df)
    return df


def analyze_advanced_signals(df: pd.DataFrame) -> Dict:
    """分析進階技術指標訊號"""
    if df is None or len(df) < 30:
        return {'error': 'Insufficient data'}
    
    df = calculate_all_indicators(df)
    
    latest = df.iloc[-1]
    signals = []
    
    bb = latest.get('BB_Upper'), latest.get('BB_Middle'), latest.get('BB_Lower')
    if all(bb):
        if latest['Close'] > bb[0]:
            signals.append({'indicator': 'BB', 'signal': 'overbought', 'value': f"價格超越上軌", 'action': 'sell'})
        elif latest['Close'] < bb[2]:
            signals.append({'indicator': 'BB', 'signal': 'oversold', 'value': f"價格跌破下軌", 'action': 'buy'})
        else:
            signals.append({'indicator': 'BB', 'signal': 'neutral', 'value': f"中軌:{bb[1]:.2f}", 'action': 'hold'})
    
    atr = latest.get('ATR')
    if atr:
        signals.append({'indicator': 'ATR', 'signal': 'volatility', 'value': round(atr, 2), 'action': 'info'})
    
    wr = latest.get('Williams_R')
    if wr:
        if wr < -80:
            signals.append({'indicator': 'Williams_R', 'signal': 'oversold', 'value': round(wr, 2), 'action': 'buy'})
        elif wr > -20:
            signals.append({'indicator': 'Williams_R', 'signal': 'overbought', 'value': round(wr, 2), 'action': 'sell'})
        else:
            signals.append({'indicator': 'Williams_R', 'signal': 'neutral', 'value': round(wr, 2), 'action': 'hold'})
    
    cci = latest.get('CCI')
    if cci:
        if cci > 100:
            signals.append({'indicator': 'CCI', 'signal': 'overbought', 'value': round(cci, 2), 'action': 'sell'})
        elif cci < -100:
            signals.append({'indicator': 'CCI', 'signal': 'oversold', 'value': round(cci, 2), 'action': 'buy'})
        else:
            signals.append({'indicator': 'CCI', 'signal': 'neutral', 'value': round(cci, 2), 'action': 'hold'})
    
    plus_di = latest.get('Plus_DI')
    minus_di = latest.get('Minus_DI')
    adx = latest.get('ADX')
    if plus_di and minus_di and adx:
        if plus_di > minus_di and adx > 25:
            signals.append({'indicator': 'DMI', 'signal': 'uptrend', 'value': f"+DI:{plus_di:.1f}, -DI:{minus_di:.1f}, ADX:{adx:.1f}", 'action': 'buy'})
        elif minus_di > plus_di and adx > 25:
            signals.append({'indicator': 'DMI', 'signal': 'downtrend', 'value': f"+DI:{plus_di:.1f}, -DI:{minus_di:.1f}, ADX:{adx:.1f}", 'action': 'sell'})
        else:
            signals.append({'indicator': 'DMI', 'signal': 'neutral', 'value': f"ADX:{adx:.1f}", 'action': 'hold'})
    
    return {
        'bollinger_bands': {'upper': round(bb[0], 2) if bb[0] else None, 'middle': round(bb[1], 2) if bb[1] else None, 'lower': round(bb[2], 2) if bb[2] else None},
        'atr': round(atr, 2) if atr else None,
        'atr_pct': round(latest.get('ATR_Pct', 0), 2),
        'williams_r': round(wr, 2) if wr else None,
        'cci': round(cci, 2) if cci else None,
        'dmi': {'plus_di': round(plus_di, 2) if plus_di else None, 'minus_di': round(minus_di, 2) if minus_di else None, 'adx': round(adx, 2) if adx else None},
        'signals': signals
    }