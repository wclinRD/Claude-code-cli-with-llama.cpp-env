"""
Chart Generator Module - 圖表生成器
生成 Markdown 表格和 SVG 圖形
"""

import pandas as pd
import numpy as np
from typing import Dict, List
from datetime import datetime


def generate_price_table(df: pd.DataFrame, days: int = 30) -> str:
    """生成價格表格 (Markdown)"""
    if df is None or df.empty:
        return "No data"
    
    recent = df.tail(days)
    
    lines = ["| Date | Open | High | Low | Close | Volume |"]
    lines.append("|" + "-|" * 6)
    
    for _, row in recent.iterrows():
        date = row['Date'].strftime('%Y-%m-%d') if hasattr(row['Date'], 'strftime') else str(row['Date'])[:10]
        lines.append(f"| {date} | {row['Open']:.2f} | {row['High']:.2f} | {row['Low']:.2f} | {row['Close']:.2f} | {int(row['Volume']):,} |")
    
    return "\n".join(lines)


def generate_ma_table(mas: Dict) -> str:
    """生成均線表格"""
    if not mas:
        return "No data"
    
    lines = ["| MA | Value |", "|-:|:-:|"]
    
    for ma, value in mas.items():
        if value:
            lines.append(f"| {ma} | {value:.2f} |")
    
    return "\n".join(lines)


def generate_indicator_table(indicators: Dict) -> str:
    """生成技術指標表格"""
    if not indicators:
        return "No data"
    
    lines = ["| Indicator | Value | Signal |", "|-:|:-:|:-:|"]
    
    rsi = indicators.get('rsi')
    if rsi:
        signal = "Overbought" if rsi > 70 else "Oversold" if rsi < 30 else "Neutral"
        lines.append(f"| RSI(14) | {rsi} | {signal} |")
    
    macd = indicators.get('macd')
    signal = indicators.get('macd', 0)
    if macd:
        lines.append(f"| MACD | {macd:.2f} | {'Bullish' if macd > 0 else 'Bearish'} |")
    
    k = indicators.get('k')
    d = indicators.get('d')
    if k and d:
        lines.append(f"| KD | K:{k:.1f} D:{d:.1f} | {'Bullish' if k > d else 'Bearish'} |")
    
    if 'signals' in indicators:
        for sig in indicators['signals']:
            lines.append(f"| {sig.get('indicator')} | {sig.get('value', '')} | {sig.get('signal', '')} |")
    
    return "\n".join(lines)


def generate_summary_table(results: Dict) -> str:
    """生成綜合分析摘要表格"""
    lines = ["| Analysis | Result |", "|-:|:-:|"]
    
    if 'price_action' in results:
        pa = results['price_action']
        if 'current_price' in pa:
            lines.append(f"| Current Price | {pa['current_price']:.2f} |")
        if 'pattern' in pa and pa.get('pattern'):
            lines.append(f"| Pattern | {pa['pattern'].get('pattern')} ({pa['pattern'].get('confidence')}%) |")
    
    if 'moving_avg' in results:
        ma = results['moving_avg']
        if 'alignment' in ma:
            lines.append(f"| MA Alignment | {ma['alignment'].get('alignment')} |")
    
    if 'indicators' in results:
        ind = results['indicators']
        for sig in ind.get('signals', [])[:3]:
            lines.append(f"| {sig.get('indicator')} | {sig.get('signal')} |")
    
    return "\n".join(lines)


def generate_svg_chart(df: pd.DataFrame, width: int = 800, height: int = 400) -> str:
    """生成股價走勢 SVG 圖表"""
    if df is None or df.empty or len(df) < 10:
        return ""
    
    recent = df.tail(60)
    
    prices = recent['Close'].values
    highs = recent['High'].values
    lows = recent['Low'].values
    
    price_min = min(lows)
    price_max = max(highs)
    price_range = price_max - price_min
    
    if price_range == 0:
        price_range = 1
    
    padding = 40
    chart_width = width - padding * 2
    chart_height = height - padding * 2
    
    def y_to_pix(price):
        return padding + chart_height - ((price - price_min) / price_range * chart_height)
    
    def x_to_pix(i):
        return padding + (i / (len(recent) - 1)) * chart_width if len(recent) > 1 else padding
    
    price_points = [f"{x_to_pix(i)},{y_to_pix(p)}" for i, p in enumerate(prices)]
    
    fill_path = f"M {x_to_pix(0)},{y_to_pix(prices[0])} L " + " L ".join(price_points) + f" L {x_to_pix(len(prices)-1)},{y_to_pix(prices[-1])} L {x_to_pix(0)},{y_to_pix(prices[-1])} Z"
    
    line_path = "M " + " L ".join(price_points)
    
    ma20 = recent['MA20'].values if 'MA20' in recent.columns else None
    if ma20 is not None and not pd.isna(ma20).all():
        ma_points = [f"{x_to_pix(i)},{y_to_pix(m)}" for i, m in enumerate(ma20) if not pd.isna(m)]
        ma20_path = "M " + " L ".join(ma_points) if ma_points else ""
    else:
        ma20_path = ""
    
    svg = f'''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {width} {height}" width="{width}" height="{height}">
  <rect width="{width}" height="{height}" fill="#1a1a2e"/>
  <text x="{padding}" y="25" fill="#888" font-size="12" font-family="monospace">{recent.iloc[0]['Date'].strftime('%Y-%m-%d' if hasattr(recent.iloc[0]['Date'], 'strftime') else str(recent.iloc[0]['Date'])[:10])}</text>
  <text x="{width-padding}" y="25" fill="#888" font-size="12" font-family="monospace" text-anchor="end">{recent.iloc[-1]['Date'].strftime('%Y-%m-%d' if hasattr(recent.iloc[-1]['Date'], 'strftime') else str(recent.iloc[-1]['Date'])[:10])}</text>
  <path d="{line_path}" fill="none" stroke="#00d4ff" stroke-width="2"/>
  <path d="{fill_path}" fill="url(#gradient)" opacity="0.3"/>
  {"<path d=\"" + ma20_path + "\" fill=\"none\" stroke=\"#ff6b6b\" stroke-width=\"1\" stroke-dasharray=\"4\"/>" if ma20_path else ""}
  <text x="{padding}" y="{height-10}" fill="#666" font-size="10" font-family="monospace">{price_min:.2f}</text>
  <text x="{padding}" y="{padding+15}" fill="#666" font-size="10" font-family="monospace">{price_max:.2f}</text>
  <defs>
    <linearGradient id="gradient" x1="0%" y1="0%" x2="0%" y2="100%">
      <stop offset="0%" stop-color="#00d4ff" stop-opacity="0.4"/>
      <stop offset="100%" stop-color="#00d4ff" stop-opacity="0"/>
    </linearGradient>
  </defs>
</svg>'''
    
    return svg


def generate_comparison_chart(results: Dict) -> str:
    """生成比較圖表"""
    lines = ["# 技術分析比較圖表\n"]
    
    lines.append("## 價格資訊")
    if 'price_action' in results:
        pa = results['price_action']
        lines.append(f"- 現在價格: {pa.get('current_price')}")
        if pa.get('nearest_support'):
            lines.append(f"- 最近支撐: {pa['nearest_support']:.2f}")
        if pa.get('nearest_resistance'):
            lines.append(f"- 最近阻力: {pa['nearest_resistance']:.2f}")
    
    lines.append("\n## 均線狀態")
    if 'moving_avg' in results:
        ma = results['moving_avg']
        lines.append(f"- 均線排列: {ma.get('alignment', {}).get('alignment', 'N/A')}")
        lines.append(f"- 訊號: {ma.get('alignment', {}).get('signal', 'N/A')}")
    
    lines.append("\n## 技術指標")
    if 'indicators' in results:
        ind = results['indicators']
        for sig in ind.get('signals', [])[:5]:
            lines.append(f"- **{sig.get('indicator')}**: {sig.get('signal')} ({sig.get('action', 'N/A')})")
    
    lines.append("\n## 纏論")
    if 'chan_theory' in results:
        ct = results['chan_theory']
        lines.append(f"- 走勢: {ct.get('trend', {}).get('trend', 'N/A')}")
    
    lines.append("\n## 波浪理論")
    if 'wave_theory' in results:
        wt = results['wave_theory']
        lines.append(f"- 波浪類型: {wt.get('wave_type', 'N/A')}")
        lines.append(f"- 波浪位置: {wt.get('elliott_position', wt.get('wave_stage', 'N/A'))}")
    
    if 'wave_forecast' in results:
        wf = results['wave_forecast']
        lines.append("\n## 波浪走勢預測")
        lines.append(f"- 現價: {wf.get('current_price', 'N/A')}")
        if 'forecasts' in wf:
            for f in wf['forecasts']:
                prob = int(f.get('probability', 0) * 100)
                lines.append(f"- {f.get('scenario', 'N/A')} ({prob}%): {f.get('description', 'N/A')}")
                lines.append(f"  目標: {f.get('target', 'N/A')}, 停損: {f.get('stop_loss', 'N/A')}")
        if 'time_estimate' in wf:
            te = wf['time_estimate']
            lines.append(f"- 時間預測: 短期 {te.get('short', 'N/A')}, 中期 {te.get('medium', 'N/A')}")
    
    return "\n".join(lines)