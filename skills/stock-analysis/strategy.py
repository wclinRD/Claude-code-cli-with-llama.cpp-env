"""
Strategy Module - 交易策略產生器
綜合所有分析產生交易建議
"""

import pandas as pd
from typing import Dict, List, Tuple


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
    
    if 'wave_theory' in results:
        wt = results['wave_theory']
        if wt.get('description') and '上漲' in wt.get('description', ''):
            score += 10
        elif wt.get('description') and '下跌' in wt.get('description', ''):
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
    
    buy_price = None
    sell_price = None
    stop_loss = None
    
    nearest_support = pa.get('nearest_support')
    nearest_resistance = pa.get('nearest_resistance')
    
    if nearest_resistance and nearest_support:
        mid_price = (nearest_resistance + nearest_support) / 2
        
        if nearest_resistance - current_price < current_price - nearest_support:
            buy_price = current_price
            sell_price = nearest_resistance
            stop_loss = nearest_support * 0.97
        else:
            buy_price = current_price * 0.98
            sell_price = round((nearest_resistance + current_price) / 2, 2)
            stop_loss = nearest_support * 0.95
    
    if 'indicators' in results:
        ind = results['indicators']
        
        rsi = ind.get('rsi')
        if rsi and rsi < 35:
            if not buy_price:
                buy_price = current_price
        
        for sig in ind.get('signals', []):
            if sig.get('indicator') == 'MACD' and sig.get('action') == 'buy':
                if not buy_price:
                    buy_price = current_price
    
    return {
        'current_price': current_price,
        'recommended_buy': buy_price,
        'recommended_sell': sell_price,
        'stop_loss': stop_loss,
        'risk_ratio': round((sell_price - stop_loss) / (buy_price - stop_loss), 2) if buy_price and sell_price and stop_loss else None
    }


def analyze_risk_reward(results: Dict) -> Dict:
    """分析風險報酬比"""
    points = generate_entry_exit_points(results)
    
    if not points or not points.get('recommended_buy') or not points.get('recommended_sell'):
        return {'risk_reward': None}
    
    buy = points['recommended_buy']
    sell = points['recommended_sell']
    stop = points['stop_loss']
    
    if not stop or not buy or not sell:
        return {'risk_reward': None}
    
    reward = sell - buy
    risk = buy - stop
    
    if risk <= 0:
        return {'risk_reward': None, 'comment': 'Invalid stop loss'}
    
    ratio = reward / risk
    
    if ratio >= 3:
        comment = '極佳風險報酬比'
    elif ratio >= 2:
        comment = '良好風險報酬比'
    elif ratio >= 1.5:
        comment = '一般風險報酬��'
    else:
        comment = '風險報酬比不佳'
    
    return {
        'risk_reward': round(ratio, 2),
        'entry': round(buy, 2),
        'target': round(sell, 2),
        'stop': round(stop, 2),
        'comment': comment
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
    
    points = generate_entry_exit_points(results)
    risk_reward = analyze_risk_reward(results)
    
    return {
        'signal': signal,
        'score': score,
        'entry': points.get('recommended_buy'),
        'target': points.get('recommended_sell'),
        'stop_loss': points.get('stop_loss'),
        'risk_reward': risk_reward.get('risk_reward'),
        'reason': []
    }


def generate_daily_strategy(df: pd.DataFrame, results: Dict) -> str:
    """生成日線交易策略報告"""
    lines = ["# 日線級別交易策略報告\n"]
    
    lines.append("## 綜合評估")
    strategy = generate_strategy_signal(results)
    lines.append(f"- **訊號**: {strategy['signal']}")
    lines.append(f"- **評分**: {strategy['score']}/100")
    
    lines.append("\n## 進場策略")
    if strategy.get('entry'):
        lines.append(f"- **進場價**: {strategy['entry']}")
    if strategy.get('target'):
        lines.append(f"- **目標價**: {strategy['target']}")
    if strategy.get('stop_loss'):
        lines.append(f"- **停損價**: {strategy['stop_loss']}")
    if strategy.get('risk_reward'):
        lines.append(f"- **風險報酬比**: {strategy['risk_reward']}:1")
    
    lines.append("\n## 各項技術分析 Summary")
    
    lines.append("\n### 價格行為")
    if 'price_action' in results:
        pa = results['price_action']
        lines.append(f"- 現在價格: {pa.get('current_price')}")
        if pa.get('pattern') and pa['pattern'].get('pattern'):
            lines.append(f"- 型態: {pa['pattern'].get('pattern')}")
    
    lines.append("\n### 均線狀態")
    if 'moving_avg' in results:
        ma = results['moving_avg']
        alignment = ma.get('alignment', {}).get('alignment')
        lines.append(f"- 均線排列: {alignment}")
        
        signals = ma.get('signals', [])
        buy_signals = [s for s in signals if s.get('action') == 'buy']
        sell_signals = [s for s in signals if s.get('action') == 'sell']
        
        if buy_signals:
            lines.append(f"- 買入訊號數: {len(buy_signals)}")
        if sell_signals:
            lines.append(f"- 賣出訊號數: {len(sell_signals)}")
    
    lines.append("\n### 技術指標")
    if 'indicators' in results:
        ind = results['indicators']
        if ind.get('rsi'):
            lines.append(f"- RSI(14): {ind['rsi']}")
        if ind.get('macd'):
            lines.append(f"- MACD: {ind['macd']}")
        if ind.get('k') and ind.get('d'):
            lines.append(f"- K: {ind['k']}, D: {ind['d']}")
    
    lines.append("\n### 纏論")
    if 'chan_theory' in results:
        ct = results['chan_theory']
        lines.append(f"- 走勢: {ct.get('trend', {}).get('trend', 'N/A')}")
    
    lines.append("\n### 波浪理論")
    if 'wave_theory' in results:
        wt = results['wave_theory']
        lines.append(f"- 波浪: {wt.get('description', wt.get('pattern', 'N/A'))}")
    
    return "\n".join(lines)


def generate_trading_recommendation(df: pd.DataFrame, results: Dict) -> Dict:
    """生成最終交易建議"""
    strategy = generate_strategy_signal(results)
    points = generate_entry_exit_points(results)
    risk = analyze_risk_reward(results)
    
    reasons = []
    
    if 'moving_avg' in results:
        ma = results['moving_avg']
        if ma.get('alignment', {}).get('alignment') == 'bullish':
            reasons.append("均線多頭排列")
    
    if 'indicators' in results:
        ind = results['indicators']
        for sig in ind.get('signals', []):
            if sig.get('indicator') == 'MACD' and sig.get('signal') == 'golden_cross':
                reasons.append("MACD 出現黃金交叉")
            if sig.get('indicator') == 'RSI' and sig.get('signal') == 'oversold':
                reasons.append("RSI 超賣")
    
    if 'wave_theory' in results:
        wt = results['wave_theory']
        if wt.get('wave') in ['wave_3', 'wave_5']:
            reasons.append(f"艾略特波浪處於{wt.get('wave')}上漲階段")
    
    return {
        'action': strategy['signal'],
        'score': strategy['score'],
        'reasons': reasons,
        'entry': points.get('recommended_buy'),
        'target': points.get('recommended_sell'),
        'stop_loss': points.get('stop_loss'),
        'risk_reward': risk.get('risk_reward'),
        'analysis_aligned': len(reasons) >= 2
    }