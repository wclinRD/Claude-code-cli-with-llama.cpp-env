"""
Chart Generator Module - 圖表生成器
生成 Markdown 表格和 SVG 圖形
"""

import pandas as pd
import numpy as np
from typing import Dict, List, Optional
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


def generate_candlestick_svg(df: pd.DataFrame, width: int = 800, height: int = 400, show_ma: List[str] = None) -> str:
    """
    生成 K 線圖 SVG
    
    Args:
        df: 包含 Open, High, Low, Close 的 DataFrame
        width: 圖寬
        height: 圖高
        show_ma: 要顯示的均線列表，如 ['MA5', 'MA20']
    
    Returns:
        SVG 字符串
    """
    if df is None or df.empty or len(df) < 10:
        return ""
    
    recent = df.tail(60).copy()
    
    if 'MA5' not in recent.columns and 'MA20' not in recent.columns:
        from moving_avg import calculate_mas
        recent = calculate_mas(recent)
    
    opens = recent['Open'].values
    highs = recent['High'].values
    lows = recent['Low'].values
    closes = recent['Close'].values
    
    price_min = min(lows)
    price_max = max(highs)
    price_range = price_max - price_min
    
    if price_range == 0:
        price_range = 1
    
    padding = 50
    chart_width = width - padding * 2
    chart_height = height - padding * 2
    candle_width = max(2, chart_width / len(recent) * 0.7)
    candle_gap = chart_width / len(recent)
    
    def y_to_pix(price):
        return padding + chart_height - ((price - price_min) / price_range * chart_height)
    
    def x_to_pix(i):
        return padding + i * candle_gap + candle_gap / 2
    
    candle_paths = []
    ma_paths = {}
    
    for i in range(len(recent)):
        o = opens[i]
        h = highs[i]
        l = lows[i]
        c = closes[i]
        
        is_bullish = c >= o
        
        color = "#00d4ff" if is_bullish else "#ff4757"
        
        high_y = y_to_pix(h)
        low_y = y_to_pix(l)
        open_y = y_to_pix(o)
        close_y = y_to_pix(c)
        
        x = x_to_pix(i)
        
        wick = f'<line x1="{x}" y1="{high_y}" x2="{x}" y2="{low_y}" stroke="{color}" stroke-width="1"/>'
        
        body_top = min(open_y, close_y)
        body_bottom = max(open_y, close_y)
        body_height = max(1, body_bottom - body_top)
        
        body = f'<rect x="{x - candle_width/2}" y="{body_top}" width="{candle_width}" height="{body_height}" fill="{color}"/>'
        
        candle_paths.append(f"{wick}\n{body}")
    
    candle_svg = "\n".join(candle_paths)
    
    mas_to_show = show_ma or ['MA20']
    for ma_name in mas_to_show:
        if ma_name in recent.columns:
            ma_values = recent[ma_name].values
            ma_points = [f"{x_to_pix(i)},{y_to_pix(m)}" for i, m in enumerate(ma_values) if not pd.isna(m)]
            if ma_points:
                ma_color = {"MA5": "#ff6b6b", "MA10": "#ffd93d", "MA20": "#6bcb77", "MA60": "#4d96ff"}.get(ma_name, "#ff9f43")
                ma_paths[ma_name] = f'<path d="M {" L ".join(ma_points)}" fill="none" stroke="{ma_color}" stroke-width="1.5"/>'
    
    ma_svg = "\n".join(ma_paths.values())
    
    date_start = recent.iloc[0]['Date']
    date_end = recent.iloc[-1]['Date']
    date_start_str = date_start.strftime('%Y-%m-%d') if hasattr(date_start, 'strftime') else str(date_start)[:10]
    date_end_str = date_end.strftime('%Y-%m-%d') if hasattr(date_end, 'strftime') else str(date_end)[:10]
    
    svg = f'''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {width} {height}" width="{width}" height="{height}">
  <rect width="{width}" height="{height}" fill="#1a1a2e"/>
  <text x="{padding}" y="25" fill="#888" font-size="11" font-family="monospace">{date_start_str}</text>
  <text x="{width-padding}" y="25" fill="#888" font-size="11" font-family="monospace" text-anchor="end">{date_end_str}</text>
  {candle_svg}
  {ma_svg}
  <line x1="{padding}" y1="{padding}" x2="{padding}" y2="{height-padding}" stroke="#333" stroke-width="1"/>
  <line x1="{padding}" y1="{height-padding}" x2="{width-padding}" y2="{height-padding}" stroke="#333" stroke-width="1"/>
  <text x="{padding}" y="{height-15}" fill="#666" font-size="10" font-family="monospace">{price_min:.2f}</text>
  <text x="{padding}" y="{padding+15}" fill="#666" font-size="10" font-family="monospace">{price_max:.2f}</text>
  <text x="{width-10}" y="15" fill="#888" font-size="10" font-family="monospace" text-anchor="end">K-Line</text>
</svg>'''
    
    return svg


def generate_indicator_panel_svg(df: pd.DataFrame, indicator: str = "RSI", width: int = 800, height: int = 150) -> str:
    """
    生成技術指標子圖 SVG
    
    Args:
        df: 包含指標數據的 DataFrame
        indicator: 指標名稱 (RSI, MACD, KD)
        width: 圖寬
        height: 圖高
    
    Returns:
        SVG 字符串
    """
    if df is None or df.empty or len(df) < 10:
        return ""
    
    recent = df.tail(60)
    padding = 40
    chart_width = width - padding * 2
    chart_height = height - padding * 2
    
    if indicator == "RSI" and 'RSI' in recent.columns:
        values = recent['RSI'].values
        min_val, max_val = 0, 100
    elif indicator == "MACD" and 'MACD' in recent.columns:
        values = recent['MACD'].values
        min_val, max_val = min(values), max(values)
    elif indicator == "KD" and 'K' in recent.columns:
        values = recent['K'].values
        min_val, max_val = 0, 100
    else:
        return ""
    
    val_range = max_val - min_val
    if val_range == 0:
        val_range = 1
    
    def y_to_pix(val):
        return padding + chart_height - ((val - min_val) / val_range * chart_height)
    
    def x_to_pix(i):
        return padding + (i / (len(recent) - 1)) * chart_width if len(recent) > 1 else padding
    
    points = [f"{x_to_pix(i)},{y_to_pix(v)}" for i, v in enumerate(values)]
    line_path = "M " + " L ".join(points)
    
    if indicator == "RSI":
        threshold_color = "#ff4757"
        line_color = "#ffd93d"
        extra_lines = f'''<line x1="{padding}" y1="{y_to_pix(70)}" x2="{width-padding}" y2="{y_to_pix(70)}" stroke="{threshold_color}" stroke-width="1" stroke-dasharray="4"/>
<line x1="{padding}" y1="{y_to_pix(30)}" x2="{width-padding}" y2="{y_to_pix(30)}" stroke="{threshold_color}" stroke-width="1" stroke-dasharray="4"/>'''
    else:
        extra_lines = ""
    
    svg = f'''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {width} {height}" width="{width}" height="{height}">
  <rect width="{width}" height="{height}" fill="#1a1a2e"/>
  <text x="{padding}" y="20" fill="#888" font-size="11" font-family="monospace">{indicator}</text>
  <path d="{line_path}" fill="none" stroke="{line_color}" stroke-width="2"/>
  {extra_lines}
  <text x="{padding}" y="{height-10}" fill="#666" font-size="9" font-family="monospace">{min_val:.0f}</text>
  <text x="{padding}" y="{padding+12}" fill="#666" font-size="9" font-family="monospace">{max_val:.0f}</text>
</svg>'''
    
    return "\n".join(lines)


def generate_multi_period_chart(
    df: pd.DataFrame,
    periods: List[str] = ['1d', '1w', '1mo'],
    width: int = 800,
    height: int = 300
) -> str:
    """生成多週期圖表
    
    Args:
        df: 日線 DataFrame
        periods: 週期列表 ('1d'=日, '1w'=週, '1mo'=月)
        width: 圖寬
        height: 圖高
    
    Returns:
        SVG 圖表字串
    """
    if df is None or df.empty or len(df) < 60:
        return ""
    
    padding = 40
    chart_width = width - padding * 2
    chart_height = height - padding * 2
    
    def y_to_pix(price, price_min, price_max):
        if price_max == price_min:
            return padding + chart_height // 2
        return padding + chart_height - ((price - price_min) / (price_max - price_min) * chart_height)
    
    def x_to_pix(i, total):
        return padding + (i / max(total - 1, 1)) * chart_width
    
    charts = []
    
    for period in periods:
        if period == '1w':
            df_period = df.resample('W').agg({'Open': 'first', 'High': 'max', 'Low': 'min', 'Close': 'last'})
        elif period == '1mo':
            df_period = df.resample('M').agg({'Open': 'first', 'High': 'max', 'Low': 'min', 'Close': 'last'})
        else:
            df_period = df.tail(30)
        
        if len(df_period) < 5:
            continue
        
        prices = df_period['Close'].values
        price_min, price_max = min(prices), max(prices)
        
        points = []
        for i, p in enumerate(prices):
            x = x_to_pix(i, len(prices))
            y = y_to_pix(p, price_min, price_max)
            points.append(f"{x},{y}")
        
        line_path = "M " + " L ".join(points)
        
        color_map = {'1d': '#00d4ff', '1w': '#ffd93d', '1mo': '#ff6b6b'}
        color = color_map.get(period, '#00d4ff')
        
        label_map = {'1d': '日線', '1w': '週線', '1mo': '月線'}
        
        chart_svg = f'''<g id="{period}">
  <text x="{padding}" y="{len(charts) * (height + 20) + 25}" fill="{color}" font-size="12" font-family="monospace">{label_map.get(period, period)}</text>
  <path d="{line_path}" fill="none" stroke="{color}" stroke-width="2"/>
  <text x="{width - padding}" y="{len(charts) * (height + 20) + 25}" fill="#666" font-size="10" font-family="monospace" text-anchor="end">{prices[-1]:.2f}</text>
</g>'''
        charts.append(chart_svg)
    
    if not charts:
        return ""
    
    total_height = len(charts) * (height + 10) + 50
    
    svg = f'''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {width} {total_height}" width="{width}" height="{total_height}">
  <rect width="{width}" height="{total_height}" fill="#1a1a2e"/>
  {chr(10).join(charts)}
</svg>'''
    
    return svg


def resample_to_period(df: pd.DataFrame, period: str = '1w') -> pd.DataFrame:
    """將日線資料轉換為週/月線
    
    Args:
        df: 日線 DataFrame
        period: 目標週期 ('1w', '1mo')
    
    Returns:
        轉換後的 DataFrame
    """
    if df is None or df.empty:
        return df
    
    agg_dict = {'Open': 'first', 'High': 'max', 'Low': 'min', 'Close': 'last', 'Volume': 'sum'}
    
    if 'Adj Close' in df.columns:
        agg_dict['Adj Close'] = 'last'
    
    if period == '1w':
        return df.resample('W').agg(agg_dict)
    elif period == '1mo':
        return df.resample('M').agg(agg_dict)
    else:
        return df.tail(30)