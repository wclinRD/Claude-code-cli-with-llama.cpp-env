"""
Stock Analyzer - 整合分析腳本
"""

import argparse
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

from data_fetcher import fetch_data, get_latest_price
from price_action import analyze_price_action
from moving_avg import analyze_moving_avg, calculate_mas
from indicators import analyze_signals, detect_divergence
from chan_theory import analyze_chan
from wave_theory import analyze_wave_structure, detect_elliott_waves, golden_ratio_analysis
from chart_generator import (
    generate_price_table, 
    generate_ma_table, 
    generate_indicator_table,
    generate_summary_table,
    generate_svg_chart,
    generate_comparison_chart
)
from strategy import (
    generate_daily_strategy,
    generate_trading_recommendation
)


def run_full_analysis(ticker: str, period: str = "6mo", chart_type: str = "both") -> dict:
    """執行完整分析"""
    
    print(f"正在分析: {ticker} ...")
    
    df = fetch_data(ticker, period=period)
    
    if df is None or df.empty:
        return {'error': f'無法取得 {ticker} 的數據'}
    
    df = calculate_mas(df)
    
    results = {}
    
    results['price_action'] = analyze_price_action(df)
    results['moving_avg'] = analyze_moving_avg(df)
    results['indicators'] = analyze_signals(df)
    results['chan_theory'] = analyze_chan(df)
    results['wave_theory'] = analyze_wave_structure(df)
    results['elliott_waves'] = detect_elliott_waves(df)
    results['golden_ratio'] = golden_ratio_analysis(df)
    
    output = {}
    output['ticker'] = ticker
    output['results'] = results
    
    output['price_table'] = generate_price_table(df)
    output['ma_table'] = generate_ma_table(results['moving_avg'].get('mas', {}))
    output['indicator_table'] = generate_indicator_table(results['indicators'])
    
    output['strategy_report'] = generate_daily_strategy(df, results)
    output['recommendation'] = generate_trading_recommendation(df, results)
    
    output['comparison_chart'] = generate_comparison_chart(results)
    
    if chart_type in ['svg', 'both']:
        output['svg_chart'] = generate_svg_chart(df)
    
    return output


def print_report(output: dict):
    """輸出報告"""
    
    if 'error' in output:
        print(f"\n錯誤: {output['error']}")
        return
    
    results = output.get('results', {})
    
    print("\n" + "=" * 60)
    print(f"股票技術分析報告 - {output.get('ticker')}")
    print("=" * 60)
    
    print("\n## 價格資訊")
    pa = results.get('price_action', {})
    if pa.get('current_price'):
        print(f"現在價格: {pa['current_price']:.2f}")
        if pa.get('nearest_support'):
            print(f"最近支撐: {pa['nearest_support']:.2f}")
        if pa.get('nearest_resistance'):
            print(f"最近阻力: {pa['nearest_resistance']:.2f}")
        if pa.get('pattern') and pa['pattern'].get('pattern'):
            print(f"型態辨識: {pa['pattern']['pattern']} (信心度: {pa['pattern']['confidence']*100:.0f}%)")
    
    print("\n## 均線分析")
    ma = results.get('moving_avg', {})
    mas = ma.get('mas', {})
    for name, value in mas.items():
        if value:
            print(f"{name}: {value:.2f}")
    if ma.get('alignment'):
        print(f"均線排列: {ma['alignment'].get('alignment')}")
        print(f"訊號: {ma['alignment'].get('signal')}")
    
    print("\n## 技術指標")
    ind = results.get('indicators', {})
    if ind.get('rsi'):
        print(f"RSI(14): {ind['rsi']}")
    if ind.get('macd'):
        print(f"MACD: {ind['macd']:.2f}, Signal: {ind['signal']:.2f}")
    if ind.get('k') and ind.get('d'):
        print(f"KD: K={ind['k']:.1f}, D={ind['d']:.1f}")
    print("\n指標訊號:")
    for sig in ind.get('signals', [])[:5]:
        print(f"  - {sig.get('indicator')}: {sig.get('signal')} ({sig.get('action', '')})")
    
    print("\n## 纏論分析")
    ct = results.get('chan_theory', {})
    if ct.get('trend'):
        print(f"走勢類型: {ct['trend'].get('trend')}")
        print(f"強度: {ct['trend'].get('strength')}")
    
    print("\n## 波浪理論")
    wt = results.get('wave_theory', {})
    if wt.get('wave_type'):
        print(f"波浪類型: {wt['wave_type']}")
    ew = results.get('elliott_waves', {})
    if ew.get('description'):
        print(f"波浪位置: {ew.get('description')}")
    
    print("\n## 黃金分割率")
    gr = results.get('golden_ratio', {})
    if gr.get('targets'):
        for name, value in gr['targets']:
            print(f"  {name}: {value}")
    if gr.get('recommendation'):
        print(f"建議: {gr['recommendation']}")
    
    print("\n" + "-" * 60)
    rec = output.get('recommendation', {})
    print(f"## 交易建議: {rec.get('action')}")
    print(f"評分: {rec.get('score')}/100")
    if rec.get('entry'):
        print(f"進場價: {rec.get('entry')}")
    if rec.get('target'):
        print(f"目標價: {rec.get('target')}")
    if rec.get('stop_loss'):
        print(f"停損價: {rec.get('stop_loss')}")
    if rec.get('risk_reward'):
        print(f"風險報酬比: {rec.get('risk_reward')}:1")
    
    if rec.get('reasons'):
        print("\n理由:")
        for r in rec['reasons']:
            print(f"  - {r}")
    
    print("\n" + "=" * 60)


def main():
    parser = argparse.ArgumentParser(description='Stock Technical Analysis Tool')
    parser.add_argument('ticker', nargs='?', help='Stock ticker symbol')
    parser.add_argument('--period', default='6mo', help='Data period (default: 6mo)')
    parser.add_argument('--chart', default='both', choices=['text', 'svg', 'both'], help='Chart type')
    parser.add_argument('--output', help='Output file path')
    
    args = parser.parse_args()
    
    if not args.ticker:
        print("Usage: python analyzer.py <ticker> [--period 6mo] [--chart both]")
        print("Examples:")
        print("  python analyzer.py AAPL")
        print("  python analyzer.py 2330.TW --period 1y")
        print("  python analyzer.py 0050 --chart text")
        return
    
    output = run_full_analysis(args.ticker, args.period, args.chart)
    
    if args.output:
        with open(args.output, 'w', encoding='utf-8') as f:
            f.write(output.get('strategy_report', ''))
            if output.get('svg_chart'):
                f.write('\n\n' + output['svg_chart'])
        print(f"Report saved to {args.output}")
    else:
        print_report(output)


if __name__ == '__main__':
    main()