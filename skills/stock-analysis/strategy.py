"""
Strategy Module - 專業投資分析產生器
模擬專業基金經理人的分析邏輯
"""

import pandas as pd
import numpy as np
from typing import Dict, List, Tuple, Optional
from datetime import datetime
from enum import Enum


class StopLossType(Enum):
    FIXED = "fixed"
    ATR = "atr"
    PERCENT = "percent"
    TRAILING = "trailing"


class PositionSide(Enum):
    LONG = "long"
    SHORT = "short"


def calculate_stop_loss(
    entry_price: float,
    side: PositionSide = PositionSide.LONG,
    stop_type: StopLossType = StopLossType.PERCENT,
    atr: Optional[float] = None,
    atr_multiplier: float = 2.0,
    percent: float = 5.0,
) -> float:
    """計算停損價格"""
    if side == PositionSide.LONG:
        if stop_type == StopLossType.ATR and atr:
            return entry_price - (atr * atr_multiplier)
        elif stop_type == StopLossType.PERCENT:
            return entry_price * (1 - percent / 100)
        else:
            return entry_price * (1 - percent / 100)
    else:
        if stop_type == StopLossType.ATR and atr:
            return entry_price + (atr * atr_multiplier)
        elif stop_type == StopLossType.PERCENT:
            return entry_price * (1 + percent / 100)
        else:
            return entry_price * (1 + percent / 100)
    return entry_price


def calculate_take_profit(
    entry_price: float,
    side: PositionSide = PositionSide.LONG,
    risk_reward_ratio: float = 2.0,
    fixed_percent: Optional[float] = None,
) -> float:
    """計算停利價格 (risk_reward_ratio 為 R:R 倍數)"""
    if fixed_percent:
        if side == PositionSide.LONG:
            return entry_price * (1 + fixed_percent / 100)
        else:
            return entry_price * (1 - fixed_percent / 100)
    
    risk_percent = 2.0
    risk_amount = entry_price * risk_percent / 100
    reward = risk_amount * risk_reward_ratio
    
    if side == PositionSide.LONG:
        return entry_price + reward
    else:
        return entry_price - reward


def calculate_trailing_stop(
    current_price: float,
    entry_price: float,
    highest_price: float,
    side: PositionSide = PositionSide.LONG,
    atr: Optional[float] = None,
    atr_multiplier: float = 2.0,
    activation_percent: float = 3.0,
) -> float:
    """計算移動停損價格"""
    if side == PositionSide.LONG:
        if atr:
            trailing_stop = highest_price - (atr * atr_multiplier)
        else:
            trailing_stop = highest_price * (1 - activation_percent / 100)
        return max(trailing_stop, entry_price * 0.97)
    else:
        lowest_price = current_price
        if atr:
            trailing_stop = lowest_price + (atr * atr_multiplier)
        else:
            trailing_stop = lowest_price * (1 + activation_percent / 100)
        return min(trailing_stop, entry_price * 1.03)


def calculate_risk_management(
    entry_price: float,
    current_price: float,
    side: PositionSide = PositionSide.LONG,
    risk_percent: float = 2.0,
    target_reward_ratio: float = 2.0,
    use_trailing: bool = True,
    atr: Optional[float] = None,
) -> Dict:
    """完整風控計算"""
    if side == PositionSide.LONG:
        risk_amount = entry_price - current_price
        if risk_amount <= 0:
            risk_amount = entry_price * risk_percent / 100
        stop_loss = calculate_stop_loss(entry_price, side, percent=risk_percent)
        take_profit = calculate_take_profit(entry_price, side, risk_reward_ratio=target_reward_ratio)
    else:
        risk_amount = current_price - entry_price
        if risk_amount <= 0:
            risk_amount = entry_price * risk_percent / 100
        stop_loss = calculate_stop_loss(entry_price, side, percent=risk_percent)
        take_profit = calculate_take_profit(entry_price, side, risk_reward_ratio=target_reward_ratio)
    
    risk = abs(entry_price - stop_loss)
    reward = abs(take_profit - entry_price)
    risk_reward = reward / risk if risk > 0 else 0
    
    return {
        'entry_price': round(entry_price, 2),
        'stop_loss': round(stop_loss, 2),
        'take_profit': round(take_profit, 2),
        'risk_percent': round(risk_percent, 2),
        'reward_percent': round(target_reward_ratio * risk_percent, 2),
        'risk_reward_ratio': round(risk_reward, 2),
        'use_trailing': use_trailing,
    }


def calculate_kelly_criterion(
    win_rate: float,
    avg_win: float,
    avg_loss: float,
    fraction: float = 0.25,
) -> Dict:
    """Kelly Criterion 部位計算"""
    if avg_loss <= 0 or win_rate <= 0 or win_rate >= 1:
        return {
            'kelly_fraction': 0,
            'optimal_position': 0,
            'recommended_fraction': fraction,
            'edge': 0,
            'verdict': '數據不足',
        }
    
    win_loss_ratio = avg_win / avg_loss
    kelly = (win_rate * win_loss_ratio - (1 - win_rate)) / win_loss_ratio
    
    kelly = max(0, min(kelly, 1))
    
    half_kelly = kelly / 2
    
    if kelly > 0.25:
        verdict = "過度積極，建議減半"
        recommended_fraction = 0.25
    elif kelly > 0.1:
        verdict = "建議使用 Half-Kelly"
        recommended_fraction = half_kelly
    elif kelly > 0:
        verdict = "保守參與"
        recommended_fraction = kelly
    else:
        verdict = "無正期望値"
        recommended_fraction = 0
    
    return {
        'kelly_fraction': round(kelly, 4),
        'optimal_position': round(kelly * 100, 2),
        'recommended_fraction': round(recommended_fraction, 4),
        'edge': round(win_rate * win_loss_ratio - (1 - win_rate), 4),
        'verdict': verdict,
    }


def calculate_max_drawdown(df: pd.DataFrame, column: str = 'Close') -> Dict:
    """計算歷史最大回檔 (Max Drawdown)
    
    Args:
        df: 價格資料 DataFrame
        column: 價格欄位名稱
    
    Returns:
        最大回檔相關數據
    """
    if df is None or len(df) < 2 or column not in df.columns:
        return {'max_drawdown': 0, 'peak': 0, 'trough': 0, 'duration': 0}
    
    prices = df[column].values
    
    peak = prices[0]
    max_dd = 0
    peak_idx = 0
    trough_idx = 0
    
    for i, price in enumerate(prices):
        if price > peak:
            peak = price
            peak_idx = i
        
        dd = (peak - price) / peak
        if dd > max_dd:
            max_dd = dd
            trough_idx = i
    
    return {
        'max_drawdown': round(max_dd * 100, 2),
        'peak': round(peak, 2),
        'trough': round(prices[trough_idx], 2),
        'peak_date': peak_idx,
        'trough_date': trough_idx,
        'duration': trough_idx - peak_idx
    }


def calculate_var(
    df: pd.DataFrame,
    confidence: float = 0.95,
    column: str = 'Close',
    method: str = 'historical'
) -> Dict:
    """計算 VaR (Value at Risk) 風險值
    
    Args:
        df: 價格資料 DataFrame
        confidence: 置信水準 (預設 95%)
        column: 價格欄位名稱
        method: 計算方法 (historical, parametric, monte_carlo)
    
    Returns:
        VaR 相關數據
    """
    if df is None or len(df) < 30 or column not in df.columns:
        return {'var': 0, 'confidence': confidence}
    
    returns = df[column].pct_change().dropna()
    
    if method == 'historical':
        var = returns.quantile(1 - confidence)
    elif method == 'parametric':
        mean = returns.mean()
        std = returns.std()
        z_score = 1.645 if confidence == 0.95 else 1.96
        var = mean - z_score * std
    else:
        var = returns.quantile(1 - confidence)
    
    return {
        'var': round(abs(var) * 100, 2),
        'var_daily': round(abs(var) * df[column].iloc[-1], 2),
        'confidence': confidence,
        'method': method
    }


def calculate_position_size_kelly(
    portfolio_value: float,
    win_rate: float,
    avg_win: float,
    avg_loss: float,
    max_risk_per_trade: float = 0.02,
) -> Dict:
    """使用 Kelly Criterion 計算部位大小"""
    kelly_result = calculate_kelly_criterion(win_rate, avg_win, avg_loss)
    
    fraction = min(kelly_result['recommended_fraction'], max_risk_per_trade)
    
    position_value = portfolio_value * fraction
    
    risk_amount = portfolio_value * max_risk_per_trade
    
    shares = int(position_value / avg_win) if avg_win > 0 else 0
    
    return {
        'position_value': int(position_value),
        'position_percent': round(fraction * 100, 2),
        'shares': shares,
        'risk_amount': int(risk_amount),
        'kelly_info': kelly_result,
    }


def calculate_volatility_adjusted_position(
    portfolio_value: float,
    atr: float,
    current_price: float,
    target_risk_percent: float = 2.0,
) -> Dict:
    """波動率調整部位計算"""
    atr_percent = (atr / current_price) * 100
    
    if atr_percent <= 0:
        return {
            'position_percent': target_risk_percent,
            'position_value': int(portfolio_value * target_risk_percent / 100),
            'shares': 0,
        }
    
    risk_adjusted_percent = min(target_risk_percent / (atr_percent / target_risk_percent) * 2, 20)
    
    position_value = portfolio_value * risk_adjusted_percent / 100
    shares = int(position_value / current_price)
    
    return {
        'position_percent': round(risk_adjusted_percent, 2),
        'position_value': int(position_value),
        'shares': shares,
        'atr_percent': round(atr_percent, 2),
    }


def rank_signals_by_weight(signals: List[Dict], weights: Dict) -> List[Dict]:
    """多訊號權重排序"""
    scored = []
    
    for signal in signals:
        signal_type = signal.get('type', 'neutral')
        weight = weights.get(signal_type, 0)
        
        if signal_type == 'buy':
            weight += 10
        elif signal_type == 'sell':
            weight -= 10
        
        priority = signal.get('priority', 0)
        weight += priority
        
        scored.append({**signal, 'weight': weight})
    
    scored.sort(key=lambda x: x['weight'], reverse=True)
    
    return scored


def optimize_risk_reward(
    entry: float,
    targets: List[float],
    stops: List[float],
) -> Dict:
    """風險報酬優化"""
    results = []
    
    for target in targets:
        for stop in stops:
            risk = abs(entry - stop)
            reward = abs(target - entry)
            
            if risk <= 0:
                continue
            
            rr_ratio = reward / risk
            
            results.append({
                'target': target,
                'stop': stop,
                'risk': round(risk, 2),
                'reward': round(reward, 2),
                'rr_ratio': round(rr_ratio, 2),
            })
    
    results.sort(key=lambda x: x['rr_ratio'], reverse=True)
    
    best = results[0] if results else {}
    
    valid = [r for r in results if r['rr_ratio'] >= 2.0]
    
    return {
        'best': best,
        'all_options': results,
        'valid_options': valid,
    }


def analyze_technical_sentiment(results: Dict) -> Dict:
    """分析技術面多空"""
    signals = []
    strength = 0
    
    if 'indicators' in results:
        ind = results['indicators']
        
        rsi = ind.get('rsi', 50)
        if rsi > 80:
            signals.append({"type": "warning", "text": f"RSI 極度超買 ({rsi:.1f})，隨時可能回調"})
            strength -= 25
        elif rsi > 70:
            signals.append({"type": "warning", "text": f"RSI 超買 ({rsi:.1f})，需留意拉回"})
            strength -= 15
        elif rsi < 20:
            signals.append({"type": "opportunity", "text": f"RSI 極度超賣 ({rsi:.1f})，浮現投資機會"})
            strength += 25
        elif rsi < 30:
            signals.append({"type": "opportunity", "text": f"RSI 超賣 ({rsi:.1f})，可能反彈"})
            strength += 15
        
        macd = ind.get('macd', 0)
        signal = ind.get('signal', 0)
        if macd > signal and macd > 0:
            signals.append({"type": "bullish", "text": "MACD 持續多头格局"})
            strength += 10
        elif macd < signal and macd < 0:
            signals.append({"type": "bearish", "text": "MACD 呈现空头格局"})
            strength -= 10
        
        k = ind.get('k', 50)
        d = ind.get('d', 50)
        if k > d and k < 25:
            signals.append({"type": "opportunity", "text": "KD 低檔黃金交叉，佈局時機"})
            strength += 15
        elif k < d and k > 75:
            signals.append({"type": "warning", "text": "KD 高檔死亡交叉，慎防回調"})
            strength -= 15
    
    if 'advanced_indicators' in results:
        adv = results['advanced_indicators']
        
        bb = adv.get('bollinger_bands', {})
        if bb.get('upper'):
            price = results.get('price_action', {}).get('current_price', 0)
            if price > bb['upper']:
                signals.append({"type": "warning", "text": "股價突破布林上軌，留意短期回調"})
                strength += 5
            elif price < bb['lower']:
                signals.append({"type": "opportunity", "text": "股價跌破布林下軌，反彈機會大"})
                strength -= 5
        
        dmi = adv.get('dmi', {})
        plus_di = dmi.get('plus_di') or 0
        minus_di = dmi.get('minus_di') or 0
        adx = dmi.get('adx') or 0
        
        if adx > 30:
            if plus_di > minus_di:
                signals.append({"type": "bullish", "text": f"DMI 確認強勢多頭 (ADX={adx:.0f})"})
                strength += 15
            else:
                signals.append({"type": "bearish", "text": f"DMI 確認強勢空頭 (ADX={adx:.0f})"})
                strength -= 15
        elif adx < 15:
            signals.append({"type": "neutral", "text": "DMI 趨勢不明，觀望為宜"})
        
        cci = adv.get('cci') or 0
        if cci > 150:
            signals.append({"type": "warning", "text": f"CCI 極度超買 ({cci:.0f})"})
            strength -= 10
        elif cci < -150:
            signals.append({"type": "opportunity", "text": f"CCI 極度超賣 ({cci:.0f})"})
            strength += 10
    
    sentiment = "中立"
    if strength > 20:
        sentiment = "極度偏多"
    elif strength > 10:
        sentiment = "偏多"
    elif strength < -20:
        sentiment = "極度偏空"
    elif strength < -10:
        sentiment = "偏空"
    
    return {'sentiment': sentiment, 'strength': strength, 'signals': signals}


def analyze_macro_impact(results: Dict) -> Dict:
    """分析總體經濟影響"""
    impacts = []
    score = 0
    
    macro = results.get('macro', {})
    
    usd = macro.get('usd_twd', {})
    usd_change = usd.get('change_pct', 0)
    if usd_change > 1:
        impacts.append({"type": "risk", "text": "美元大幅升值，台股資金外流壓力大"})
        score -= 15
    elif usd_change > 0.5:
        impacts.append({"type": "warning", "text": "美元升值，電子業匯兌壓力"})
        score -= 5
    elif usd_change < -1:
        impacts.append({"type": "positive", "text": "美元貶值，有利台股資金流入"})
        score += 15
    elif usd_change < -0.5:
        impacts.append({"type": "positive", "text": "美元小幅貶值，電子業受益"})
        score += 5
    
    oil = macro.get('crude_oil', {})
    oil_change = oil.get('change_pct', 0)
    if oil_change > 5:
        impacts.append({"type": "risk", "text": "原油暴漲，通膨升溫，聯準會立場疑慮"})
        score -= 15
    elif oil_change > 3:
        impacts.append({"type": "warning", "text": "原油上漲，能源成本壓力"})
        score -= 5
    
    sp = macro.get('sp500', {})
    nasdaq = macro.get('nasdaq', {})
    
    sp_change = sp.get('change_pct', 0)
    if sp_change < -2:
        impacts.append({"type": "risk", "text": "美股重挫，台股恐受連動下挫"})
        score -= 20
    elif sp_change < -1:
        impacts.append({"type": "warning", "text": "美股下跌，謹慎看待"})
        score -= 10
    elif sp_change > 2:
        impacts.append({"type": "positive", "text": "美股大漲，帶動台股氣勢"})
        score += 15
    
    nasdaq_change = nasdaq.get('change_pct', 0)
    if nasdaq_change < -2:
        impacts.append({"type": "risk", "text": "NASDAQ 重挫，科技股壓力大"})
        score -= 10
    
    bond = macro.get('us_10y_bond', {})
    bond_rate = bond.get('rate', 0)
    if bond_rate > 5:
        impacts.append({"type": "risk", "text": "美債殖利率飆高，股市資金抽離壓力大"})
        score -= 15
    elif bond_rate > 4.5:
        impacts.append({"type": "warning", "text": "美債殖利率偏高，評價有壓"})
        score -= 5
    elif bond_rate < 3.5:
        impacts.append({"type": "positive", "text": "美債殖利率回落，股市支撐有力"})
        score += 10
    
    impact = "中性"
    if score > 15:
        impact = "有利"
    elif score > 5:
        impact = "略有利"
    elif score < -15:
        impact = "不利"
    elif score < -5:
        impact = "略不利"
    
    return {'impact': impact, 'score': score, 'factors': impacts}


def analyze_news_sentiment(results: Dict) -> Dict:
    """分析新聞情緒"""
    related = results.get('related_news', [])
    
    positive_keywords = ['漲', '突破', '創新高', '買超', '填息', '利多', '看好', '上漲', '大漲', '調升', '目標價', '獲利', '訂單']
    negative_keywords = ['跌', '重挫', '賣超', '利空', '看跌', '下挫', '大跌', '失守', '虧損', '裁員', '警告']
    
    positive_count = 0
    negative_count = 0
    key_news = []
    
    for news in related[:5]:
        title = news.get('title', '')
        is_positive = False
        is_negative = False
        
        for kw in positive_keywords:
            if kw in title:
                positive_count += 1
                is_positive = True
                break
        
        if not is_positive:
            for kw in negative_keywords:
                if kw in title:
                    negative_count += 1
                    is_negative = True
                    break
        
        if is_positive or is_negative:
            key_news.append(title[:50])
    
    sentiment = "中立"
    score = 0
    
    if positive_count > negative_count + 1:
        sentiment = "偏多"
        score = 20
    elif negative_count > positive_count + 1:
        sentiment = "偏空"
        score = -20
    
    return {
        'sentiment': sentiment,
        'score': score,
        'positive_count': positive_count,
        'negative_count': negative_count,
        'key_news': key_news
    }


def analyze_momentum(df: pd.DataFrame, results: Dict) -> Dict:
    """分析動能和趨勢"""
    if df is None or len(df) < 20:
        return {'momentum': '不明', 'strength': 0}
    
    df = df.tail(20)
    
    current = df.iloc[-1]['Close']
    ma5 = df['Close'].tail(5).mean()
    ma10 = df['Close'].tail(10).mean()
    ma20 = df['Close'].tail(20).mean()
    ma60 = df['Close'].tail(60).mean() if len(df) >= 60 else ma20
    
    change_5d = ((current - df.iloc[-6]['Close']) / df.iloc[-6]['Close'] * 100) if len(df) > 5 else 0
    change_20d = ((current - df.iloc[-21]['Close']) / df.iloc[-21]['Close'] * 100) if len(df) > 20 else 0
    change_60d = ((current - df.iloc[-61]['Close']) / df.iloc[-61]['Close'] * 100) if len(df) > 60 else change_20d
    
    momentum = "橫盤整理"
    strength = 0
    
    if current > ma5 > ma10 > ma20 > ma60:
        momentum = "強勢多頭"
        strength = 25
    elif current > ma5 and current > ma10 and ma5 > ma10:
        momentum = "短多格局"
        strength = 15
    elif current < ma5 < ma10 < ma20 < ma60:
        momentum = "強勢空頭"
        strength = -25
    elif current < ma5 and current < ma10 and ma5 < ma10:
        momentum = "短空格局"
        strength = -15
    
    if change_5d > 8:
        strength += 10
    elif change_5d > 5:
        strength += 5
    elif change_5d < -8:
        strength -= 10
    elif change_5d < -5:
        strength -= 5
    
    return {
        'momentum': momentum,
        'strength': strength,
        'change_5d': round(change_5d, 2),
        'change_20d': round(change_20d, 2),
        'change_60d': round(change_60d, 2),
        'ma_position': {
            'price_vs_ma5': round((current / ma5 - 1) * 100, 2),
            'price_vs_ma20': round((current / ma20 - 1) * 100, 2),
            'price_vs_ma60': round((current / ma60 - 1) * 100, 2) if len(df) >= 60 else None
        }
    }


def analyze_valuation(results: Dict) -> Dict:
    """分析評價面"""
    info = results.get('stock_info', {})
    
    pe = info.get('pe_ratio')
    div_yield = info.get('dividend_yield')
    market_cap = info.get('market_cap')
    
    valuation = "合理"
    score = 0
    factors = []
    
    if pe:
        if pe < 10:
            valuation = "嚴重低估"
            score = 20
            factors.append(f"本益比僅 {pe:.1f}，明顯低估")
        elif pe < 15:
            valuation = "偏低"
            score = 10
            factors.append(f"本益比 {pe:.1f}，低於平均")
        elif pe > 40:
            valuation = "偏高"
            score = -10
            factors.append(f"本益比 {pe:.1f}，評價偏高")
        elif pe > 60:
            valuation = "嚴重高估"
            score = -20
            factors.append(f"本益比 {pe:.1f}，風險較高")
    
    if div_yield and div_yield > 0.05:
        score += 10
        factors.append(f"殖利率 {div_yield*100:.1f}%優異")
    elif div_yield and div_yield > 0.03:
        score += 5
        factors.append(f"殖利率 {div_yield*100:.1f}%穩健")
    
    if market_cap:
        if market_cap > 1e12:
            factors.append(f"市值 {market_cap/1e12:.1f}兆，大型藍籌")
        elif market_cap > 1e11:
            factors.append(f"市值 {market_cap/1e11:.1f}百億，中型成長")
    
    return {'valuation': valuation, 'score': score, 'factors': factors}


def calculate_position_size(results: Dict, portfolio_value: float = 1000000) -> Dict:
    """計算建議部位大小"""
    tech = analyze_technical_sentiment(results)
    macro = analyze_macro_impact(results)
    valuation = analyze_valuation(results)
    
    base_score = 50
    base_score += tech['strength'] * 0.5
    base_score += macro['score'] * 0.3
    base_score += valuation['score'] * 0.2
    
    base_score = max(0, min(100, base_score))
    
    if base_score >= 80:
        position_pct = 30
        risk_level = "積極型"
    elif base_score >= 60:
        position_pct = 20
        risk_level = "穩健型"
    elif base_score >= 40:
        position_pct = 10
        risk_level = "保守型"
    else:
        position_pct = 5
        risk_level = "觀望型"
    
    position_value = portfolio_value * position_pct / 100
    
    return {
        'position_pct': position_pct,
        'position_value': int(position_value),
        'risk_level': risk_level,
        'base_score': round(base_score, 1)
    }


def generate_investment_thesis(results: Dict, df: pd.DataFrame) -> Dict:
    """生成專業投資論點"""
    
    price = results.get('price_action', {}).get('current_price')
    info = results.get('stock_info', {})
    name = info.get('name', '該公司')
    sector = info.get('sector', 'N/A')
    
    tech = analyze_technical_sentiment(results)
    macro = analyze_macro_impact(results)
    news = analyze_news_sentiment(results)
    momentum = analyze_momentum(df, results)
    valuation = analyze_valuation(results)
    
    thesis_points = []
    
    if tech['sentiment'] in ['偏多', '極度偏多']:
        thesis_points.append(f"技術面呈現{tech['sentiment']}格局，多項指標顯示上漲動能充足")
    elif tech['sentiment'] in ['偏空', '極度偏空']:
        thesis_points.append(f"技術面須留意{tech['sentiment']}格局，建議謹慎操作")
    
    if momentum['momentum'] in ['強勢多頭', '短多格局']:
        thesis_points.append(f"短線動能強勁，近5日漲幅{momentum['change_5d']:.1f}%，趨勢有利")
    
    if valuation['valuation'] in ['偏低', '嚴重低估']:
        thesis_points.append(f"評價面具吸引力，本益比相對低估，殖利率穩健")
    
    if news['sentiment'] == '偏多':
        thesis_points.append(f"市場消息面偏多，近期相關新聞聚焦正面")
    
    macro_impact = macro['impact']
    if macro_impact in ['有利', '略有利']:
        thesis_points.append(f"總體環境{macro_impact}，外圍市場對台股影響正面")
    elif macro_impact in ['不利', '略不利']:
        thesis_points.append(f"總體環境{macro_impact}，需留意系統性風險")
    
    risks = []
    for sig in tech['signals']:
        if sig['type'] == 'warning':
            risks.append(sig['text'])
    
    for fac in macro['factors']:
        if fac['type'] == 'risk':
            risks.append(fac['text'])
    
    return {
        'company': name,
        'sector': sector,
        'current_price': price,
        'bull_case': thesis_points,
        'risks': risks[:5],
        'tech_sentiment': tech['sentiment'],
        'macro_impact': macro['impact'],
        'valuation': valuation['valuation'],
        'momentum': momentum['momentum']
    }


def generate_professional_recommendation(df: pd.DataFrame, results: Dict) -> Dict:
    """生成專業投資建議"""
    
    tech = analyze_technical_sentiment(results)
    macro = analyze_macro_impact(results)
    news = analyze_news_sentiment(results)
    momentum = analyze_momentum(df, results)
    valuation = analyze_valuation(results)
    thesis = generate_investment_thesis(results, df)
    position = calculate_position_size(results)
    
    total_score = 50
    total_score += tech['strength'] * 0.3
    total_score += macro['score'] * 0.2
    total_score += news['score'] * 0.15
    total_score += momentum['strength'] * 0.2
    total_score += valuation['score'] * 0.15
    
    total_score = max(0, min(100, total_score))
    
    if total_score >= 80:
        action = "強烈建議買入"
        action_en = "Strong Buy"
    elif total_score >= 65:
        action = "建議買入"
        action_en = "Buy"
    elif total_score >= 50:
        action = "觀望"
        action_en = "Hold"
    elif total_score >= 35:
        action = "建議賣出"
        action_en = "Sell"
    else:
        action = "強烈建議賣出"
        action_en = "Strong Sell"
    
    pa = results.get('price_action', {})
    support = pa.get('nearest_support')
    resistance = pa.get('nearest_resistance')
    current = pa.get('current_price')
    
    if support and resistance and current:
        upside = (resistance - current) / current * 100
        downside = (current - support) / current * 100
        risk_reward = upside / downside if downside > 0 else 0
    else:
        upside = downside = risk_reward = 0
    
    return {
        'action': action,
        'action_en': action_en,
        'score': round(total_score, 1),
        'target_price': resistance,
        'stop_loss': support * 0.95 if support else None,
        'upside_pct': round(upside, 1) if upside else None,
        'downside_pct': round(downside, 1) if downside else None,
        'risk_reward': round(risk_reward, 2) if risk_reward else None,
        'position': position,
        'thesis': thesis,
        'analysis': {
            'technical': tech,
            'macro': macro,
            'news': news,
            'momentum': momentum,
            'valuation': valuation
        }
    }

def calculate_overall_score(results: Dict) -> int:
    """計算綜合評分 (0-100)"""
    score = 50
    
    if 'moving_avg' in results:
        ma = results['moving_avg']
        alignment = ma.get('alignment', {}).get('alignment')
        if alignment == 'bullish':
            score += 20
        elif alignment == 'bearish':
            score -= 20
    
    if 'indicators' in results:
        ind = results['indicators']
        for sig in ind.get('signals', []):
            if sig.get('action') == 'buy':
                score += 5
            elif sig.get('action') == 'sell':
                score -= 5
    
    if 'advanced_indicators' in results:
        adv = results['advanced_indicators']
        dmi = adv.get('dmi', {})
        if dmi:
            plus_di = dmi.get('plus_di') or 0
            minus_di = dmi.get('minus_di') or 0
            adx = dmi.get('adx') or 0
            if adx > 25:
                if plus_di > minus_di:
                    score += 10
                else:
                    score -= 10
    
    return max(0, min(100, score))


def generate_entry_exit_points(results: Dict) -> Dict:
    """產生進場/退場點位"""
    if 'price_action' not in results:
        return {}
    
    pa = results['price_action']
    current_price = pa.get('current_price')
    
    if not current_price:
        return {}
    
    nearest_support = pa.get('nearest_support')
    nearest_resistance = pa.get('nearest_resistance')
    
    if nearest_resistance and nearest_support:
        if nearest_resistance - current_price < current_price - nearest_support:
            buy_price = current_price
            sell_price = nearest_resistance
            stop_loss = nearest_support * 0.97
        else:
            buy_price = current_price * 0.98
            sell_price = round((nearest_resistance + current_price) / 2, 2)
            stop_loss = nearest_support * 0.95
    else:
        return {}
    
    return {
        'current_price': current_price,
        'recommended_buy': buy_price,
        'recommended_sell': sell_price,
        'stop_loss': stop_loss,
    }


def analyze_risk_reward(results: Dict) -> Dict:
    """分析風險報酬比"""
    points = generate_entry_exit_points(results)
    
    if not points or not points.get('recommended_buy') or not points.get('recommended_sell'):
        return {}
    
    buy = points['recommended_buy']
    sell = points['recommended_sell']
    stop = points['stop_loss']
    
    if not stop or not buy or not sell:
        return {}
    
    reward = sell - buy
    risk = buy - stop
    
    if risk <= 0:
        return {}
    
    ratio = reward / risk
    
    return {
        'risk_reward': round(ratio, 2),
        'entry': round(buy, 2),
        'target': round(sell, 2),
        'stop': round(stop, 2),
    }


def generate_strategy_signal(results: Dict) -> Dict:
    """產生交易訊號"""
    score = calculate_overall_score(results)
    
    if score >= 75:
        signal = '強烈買入'
    elif score >= 60:
        signal = '買入'
    elif score >= 45:
        signal = '觀望'
    elif score >= 30:
        signal = '賣出'
    else:
        signal = '強烈賣出'
    
    return {'signal': signal, 'score': score}


def generate_daily_strategy(df: pd.DataFrame, results: Dict) -> str:
    """生成日線交易策略報告"""
    analysis = generate_professional_recommendation(df, results)
    
    lines = ["# 綜合分析報告\n"]
    lines.append(f"## 操作建議: {analysis['action']}")
    lines.append(f"## 評分: {analysis['score']}/100\n")
    
    thesis = analysis.get('thesis', {})
    lines.append("## 投資論點")
    for point in thesis.get('bull_case', []):
        lines.append(f"- {point}")
    
    lines.append("\n## 技術面")
    tech = analysis.get('analysis', {}).get('technical', {})
    lines.append(f"- {tech.get('sentiment')}")
    
    lines.append("\n## 總體環境")
    macro = analysis.get('analysis', {}).get('macro', {})
    lines.append(f"- {macro.get('impact')}")
    
    return "\n".join(lines)


def generate_trading_recommendation(df: pd.DataFrame, results: Dict) -> Dict:
    """生成最終交易建議"""
    analysis = generate_professional_recommendation(df, results)
    risk = analyze_risk_reward(results)
    
    thesis = analysis.get('thesis', {})
    reasons = thesis.get('bull_case', [])
    
    return {
        'action': analysis.get('action'),
        'score': int(analysis.get('score', 50)),
        'reasons': reasons,
        'entry': risk.get('entry'),
        'target': risk.get('target'),
        'stop_loss': risk.get('stop'),
        'risk_reward': risk.get('risk_reward'),
    }


def generate_risk_report(df: Optional[pd.DataFrame] = None) -> Dict:
    """生成風險報告
    
    Args:
        df: 價格資料 DataFrame
    
    Returns:
        風險相關數據
    """
    risk_report = {'max_drawdown': None, 'var': None}
    
    if df is None or len(df) < 30:
        return risk_report
    
    dd = calculate_max_drawdown(df)
    var_95 = calculate_var(df, confidence=0.95)
    var_99 = calculate_var(df, confidence=0.99)
    
    return {
        'max_drawdown': dd,
        'var_95': var_95,
        'var_99': var_99,
        'risk_level': 'high' if dd['max_drawdown'] > 20 or var_95['var'] > 5 else 'medium' if dd['max_drawdown'] > 10 or var_95['var'] > 3 else 'low'
    }
