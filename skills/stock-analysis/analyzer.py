"""
Stock Analyzer - 整合分析腳本
"""

import argparse
import re
import sys
from pathlib import Path
from datetime import datetime

sys.path.insert(0, str(Path(__file__).parent))

from data_fetcher import (
    fetch_data, get_latest_price, fetch_institutional_holdings, 
    fetch_margin_short, fetch_stock_info, fetch_daily_summary, fetch_industry_performance,
    detect_otc_market, fetch_gretai_range, detect_market, fetch_macro_data,
    fetch_all_news, fetch_stock_news_by_keyword
)
from price_action import analyze_price_action
from moving_avg import analyze_moving_avg, calculate_mas
from indicators import analyze_signals, detect_divergence, analyze_advanced_signals
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
    generate_trading_recommendation,
    generate_professional_recommendation,
    analyze_technical_sentiment,
    analyze_macro_impact,
    analyze_news_sentiment,
    analyze_momentum,
    analyze_valuation,
    generate_investment_thesis,
    calculate_position_size
)


def run_full_analysis(ticker: str, period: str = "6mo", chart_type: str = "both") -> dict:
    """執行完整分析"""
    
    print(f"正在分析: {ticker} ...")
    
    market = detect_market(ticker)
    df = None
    
    if market == "TWSE":
        twse_code = ticker.replace('.TW', '')
        if detect_otc_market(twse_code):
            month_map = {'1mo': 1, '3mo': 3, '6mo': 6, '1y': 12, '2y': 24, '5y': 60}
            months = month_map.get(period, 6)
            df = fetch_gretai_range(twse_code, months)
        else:
            df = fetch_data(ticker, period=period)
    else:
        df = fetch_data(ticker, period=period)
    
    if df is None or df.empty:
        return {'error': f'無法取得 {ticker} 的數據'}
    
    df = calculate_mas(df)
    
    results = {}
    
    results['price_action'] = analyze_price_action(df)
    results['moving_avg'] = analyze_moving_avg(df)
    results['indicators'] = analyze_signals(df)
    results['advanced_indicators'] = analyze_advanced_signals(df)
    results['chan_theory'] = analyze_chan(df)
    results['wave_theory'] = analyze_wave_structure(df)
    results['elliott_waves'] = detect_elliott_waves(df)
    results['golden_ratio'] = golden_ratio_analysis(df)
    
    twse_code = ticker.replace('.TW', '')
    if market == "TWSE" and re.match(r'^\d{4,6}$', twse_code):
        results['institutional'] = fetch_institutional_holdings(twse_code)
        results['margin_short'] = fetch_margin_short(twse_code)
        results['stock_info'] = fetch_stock_info(ticker)
    
    results['market_summary'] = fetch_daily_summary()
    results['industry'] = fetch_industry_performance()
    results['macro'] = fetch_macro_data()
    
    twse_code = ticker.replace('.TW', '')
    if re.match(r'^\d{4,6}$', twse_code):
        results['related_news'] = fetch_stock_news_by_keyword(twse_code)
    
    results['all_news'] = fetch_all_news()
    
    output = {}
    output['ticker'] = ticker
    output['results'] = results
    
    output['price_table'] = generate_price_table(df)
    output['ma_table'] = generate_ma_table(results['moving_avg'].get('mas', {}))
    output['indicator_table'] = generate_indicator_table(results['indicators'])
    
    output['strategy_report'] = generate_daily_strategy(df, results)
    output['recommendation'] = generate_trading_recommendation(df, results)
    output['professional'] = generate_professional_recommendation(df, results)
    
    output['comparison_chart'] = generate_comparison_chart(results)
    
    if chart_type in ['svg', 'both']:
        output['svg_chart'] = generate_svg_chart(df)
    
    return output


def print_report(output: dict):
    """輸出專業分析報告"""
    
    if 'error' in output:
        print(f"\n錯誤: {output['error']}")
        return
    
    results = output.get('results', {})
    prof = output.get('professional', {})
    ticker = output.get('ticker')
    
    info = results.get('stock_info', {})
    name = info.get('name', ticker)
    price = results.get('price_action', {}).get('current_price')
    
    print("\n" + "=" * 65)
    print(f"📈 專業投資分析報告 - {name} ({ticker})")
    print("=" * 65)
    print(f"報告日期: {datetime.now().strftime('%Y-%m-%d')}")
    print(f"最新股價: {'N/A' if not price else f'${price:.2f}'}")
    print("-" * 65)
    
    if prof:
        thesis = prof.get('thesis', {})
        
        print("\n🎯 【投資評等】")
        action = prof.get('action', 'N/A')
        action_en = prof.get('action_en', '')
        score = prof.get('score', 0)
        
        emoji = "🟢" if "買入" in action else "🔴" if "賣出" in action else "🟡"
        print(f"  {emoji} {action} ({action_en})")
        print(f"  綜合評分: {score}/100")
        
        position = prof.get('position', {})
        if position:
            print(f"  建議部位: {position.get('risk_level')} - 部位比重 {position.get('position_pct')}%")
        
        print("\n💼 【投資論點】")
        bull_case = thesis.get('bull_case', [])
        if bull_case:
            for i, point in enumerate(bull_case, 1):
                print(f"  {i}. {point}")
        else:
            print("  目前無明顯利多論點")
        
        risks = thesis.get('risks', [])
        if risks:
            print("\n⚠️ 【風險提醒】")
            for i, risk in enumerate(risks, 1):
                print(f"  {i}. {risk}")
        
        print("\n📊 【技術分析】")
        tech = prof.get('analysis', {}).get('technical', {})
        print(f"  技術面: {tech.get('sentiment', 'N/A')}")
        for sig in tech.get('signals', [])[:3]:
            icon = "📈" if sig.get('type') == 'bullish' else "📉" if sig.get('type') == 'bearish' else "⚡" if sig.get('type') == 'warning' else "💡"
            print(f"    {icon} {sig.get('text', '')}")
        
        print("\n🌊 【趨勢動能】")
        mom = prof.get('analysis', {}).get('momentum', {})
        print(f"  趨勢判斷: {mom.get('momentum', 'N/A')}")
        print(f"  5日漲跌幅: {mom.get('change_5d', 'N/A')}%" if mom.get('change_5d') else "  5日漲跌幅: N/A")
        print(f"  20日漲跌幅: {mom.get('change_20d', 'N/A')}%" if mom.get('change_20d') else "  20日漲跌幅: N/A")
        
        print("\n🌍 【總體環境】")
        macro = prof.get('analysis', {}).get('macro', {})
        print(f"  環境判斷: {macro.get('impact', 'N/A')}")
        for fac in macro.get('factors', [])[:3]:
            icon = "✅" if fac.get('type') == 'positive' else "⚠️" if fac.get('type') == 'warning' else "❌"
            print(f"    {icon} {fac.get('text', '')}")
        
        print("\n📰 【市場情緒】")
        news = prof.get('analysis', {}).get('news', {})
        print(f"  新聞情緒: {news.get('sentiment', 'N/A')}")
        
        print("\n💰 【評價分析】")
        val = prof.get('analysis', {}).get('valuation', {})
        print(f"  評價: {val.get('valuation', 'N/A')}")
        for fac in val.get('factors', []):
            print(f"    • {fac}")
        
        if prof.get('upside_pct'):
            print(f"\n📐 【價位預測】")
            print(f"  目標價: ${prof.get('target_price', 'N/A')}")
            print(f"  停損價: ${prof.get('stop_loss', 'N/A')}")
            print(f"  上漲空間: +{prof.get('upside_pct')}%")
            print(f"  下跌風險: -{prof.get('downside_pct')}%")
            rr = prof.get('risk_reward')
            if rr:
                print(f"  風險報酬比: {rr}:1")
    
    print("\n" + "=" * 65)
    print("📌 【結論】")
    
    if prof:
        thesis = prof.get('thesis', {})
        print(f"  {thesis.get('company', ticker)} 當前呈現「{thesis.get('momentum', '')}」趨勢，")
        print(f"  技術面「{thesis.get('tech_sentiment', '')}」，總體環境「{thesis.get('macro_impact', '')}」。")
        
        action = prof.get('action', '')
        if "買入" in action:
            print(f"\n  建議可適度建立部位，但需嚴守停損紀律。")
        elif "賣出" in action:
            print(f"\n  建議減碼或觀望為宜，等待更好的進場時機。")
        else:
            print(f"\n  建議持續觀望，等待趨勢更明顯后再行布局。")
    
    print("=" * 65)
    
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
    
    adv = results.get('advanced_indicators', {})
    if adv and not adv.get('error'):
        print("\n## 進階技術指標")
        bb = adv.get('bollinger_bands', {})
        if bb.get('upper'):
            print(f"布林帶: 上軌 {bb['upper']:.2f} / 中軌 {bb['middle']:.2f} / 下軌 {bb['lower']:.2f}")
        if adv.get('atr'):
            print(f"ATR: {adv['atr']:.2f} ({adv.get('atr_pct', 0):.2f}%)")
        if adv.get('williams_r'):
            print(f"威廉指標: {adv['williams_r']:.2f}")
        if adv.get('cci'):
            print(f"CCI: {adv['cci']:.2f}")
        dmi = adv.get('dmi', {})
        if dmi and dmi.get('adx'):
            plus = dmi.get('plus_di') or 0
            minus = dmi.get('minus_di') or 0
            print(f"DMI: +DI {plus:.1f} / -DI {minus:.1f} / ADX {dmi['adx']:.1f}")
    
    inst = results.get('institutional')
    ms = results.get('margin_short')
    if inst or ms:
        print("\n## 籌碼分析")
        if inst:
            print(f"法人持股: {inst}")
        if ms:
            print(f"融資餘額: {ms.get('margin_balance', 'N/A')} | 融券餘額: {ms.get('short_balance', 'N/A')}")
    
    info = results.get('stock_info')
    if info and info.get('name'):
        print("\n## 基本資料")
        print(f"名稱: {info.get('name')}")
        if info.get('sector'):
            print(f"產業: {info.get('sector')} / {info.get('industry', '')}")
        if info.get('market_cap'):
            cap = info['market_cap']
            if cap > 1e12:
                print(f"市值: {cap/1e12:.2f} 兆")
            elif cap > 1e9:
                print(f"市值: {cap/1e9:.2f} 億")
        if info.get('pe_ratio'):
            print(f"本益比: {info['pe_ratio']:.2f}")
        if info.get('dividend_yield'):
            print(f"殖利率: {info['dividend_yield']*100:.2f}%")
    
    market = results.get('market_summary')
    if market and market.get('index'):
        print("\n## 大盤資訊")
        print(f"加權指數: {market.get('index')} ({market.get('change_pct')}%)")
    
    industry = results.get('industry')
    if industry and industry.get('industries'):
        print("\n## 產業表現")
        for ind_data in industry['industries'][:5]:
            print(f"  {ind_data['industry']}: {ind_data['change_pct']}%")
    
    macro = results.get('macro', {})
    if macro and any(macro.values()):
        print("\n## 總體經濟")
        if macro.get('usd_twd'):
            usd = macro['usd_twd']
            print(f"美元/台幣: {usd['rate']} ({usd['change_pct']:+.2f}%)")
        if macro.get('crude_oil'):
            oil = macro['crude_oil']
            print(f"原油(WTI): ${oil['price']} ({oil['change_pct']:+.2f}%)")
        if macro.get('gold'):
            gold = macro['gold']
            print(f"黃金: ${gold['price']} ({gold['change_pct']:+.2f}%)")
        if macro.get('us_10y_bond'):
            bond = macro['us_10y_bond']
            print(f"美10年公債: {bond['rate']}%")
        if macro.get('sp500'):
            sp = macro['sp500']
            print(f"S&P 500: {sp['index']} ({sp['change_pct']:+.2f}%)")
        if macro.get('nasdaq'):
            nd = macro['nasdaq']
            print(f"NASDAQ: {nd['index']} ({nd['change_pct']:+.2f}%)")
    
    related_news = results.get('related_news', [])
    if related_news:
        print("\n## 相關新聞")
        for news in related_news[:5]:
            print(f"  • {news.get('title', '')}")
    
    all_news = results.get('all_news', {})
    
    if all_news.get('rss'):
        print("\n## 財經新聞")
        for news in all_news['rss'][:6]:
            title = news.get('title', '')
            if title:
                print(f"  • {title}")
    
    google = all_news.get('google', [])
    if google:
        print("\n## Google 財經")
        for news in google[:5]:
            title = news.get('title', '')
            if title:
                print(f"  • {title}")
    
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
        print("\n綜合訊號:")
        for r in rec['reasons']:
            print(f"  ✓ {r}")
    
    tech_sentiment = results.get('indicators', {})
    if tech_sentiment.get('rsi'):
        rsi = tech_sentiment['rsi']
        if rsi > 70:
            print(f"  ⚠️ RSI 超買 ({rsi:.1f})，留意拉回風險")
        elif rsi < 30:
            print(f"  ⚠️ RSI 超賣 ({rsi:.1f})，留意反彈機會")
    
    adv_ind = results.get('advanced_indicators', {})
    if adv_ind.get('dmi'):
        dmi = adv_ind['dmi']
        plus = dmi.get('plus_di') or 0
        minus = dmi.get('minus_di') or 0
        adx = dmi.get('adx') or 0
        if adx > 25:
            trend = "多頭" if plus > minus else "空頭"
            print(f"  📊 DMI 確認趨勢: {trend} (ADX={adx:.0f})")
    
    macro = results.get('macro', {})
    if macro.get('sp500'):
        sp = macro['sp500']
        if sp.get('change_pct', 0) < -1:
            print(f"  ⚠️ 美股重挫，謹慎看待")
        elif sp.get('change_pct', 0) > 1:
            print(f"  ✓ 美股大漲，樂觀看待")
    
    print("\n" + "=" * 60)


def main():
    parser = argparse.ArgumentParser(description='Stock Technical Analysis Tool')
    parser.add_argument('ticker', nargs='?', help='Stock ticker symbol (省略時分析大盤整體走勢)')
    parser.add_argument('--period', default='6mo', help='Data period (default: 6mo)')
    parser.add_argument('--chart', default='both', choices=['text', 'svg', 'both'], help='Chart type')
    parser.add_argument('--output', help='Output file path')
    parser.add_argument('--compare', nargs='*', help='Compare multiple stocks')
    parser.add_argument('--market', default='auto', choices=['auto', 'us', 'tw'], help='Market selection when no ticker provided')
    
    args = parser.parse_args()
    
    if not args.ticker:
        if args.market == 'tw':
            args.ticker = '^TWII'
        else:
            args.ticker = '^GSPC'
        
        print("=" * 60)
        print("大盤整體走勢分析")
        print("=" * 60)
        return
    
    if args.compare:
        print("\n" + "=" * 60)
        print("多股票比較分析")
        print("=" * 60)
        
        all_tickers = [args.ticker] + args.compare
        
        comparison_data = []
        for t in all_tickers:
            result = run_full_analysis(t, args.period, 'text')
            if 'error' not in result:
                pa = result['results'].get('price_action', {})
                ind = result['results'].get('indicators', {})
                adv = result['results'].get('advanced_indicators', {})
                
                comparison_data.append({
                    'ticker': t,
                    'price': pa.get('current_price'),
                    'change_pct': pa.get('daily_change_pct'),
                    'rsi': ind.get('rsi'),
                    'macd': ind.get('macd'),
                    'atr_pct': adv.get('atr_pct'),
                    'recommendation': result['recommendation'].get('action')
                })
        
        print(f"\n{'代碼':<10} {'價格':>10} {'漲跌%':>10} {'RSI':>8} {'MACD':>10} {'ATR%':>8} {'建議':>8}")
        print("-" * 70)
        for data in comparison_data:
            price = f"{data['price']:.2f}" if data['price'] else 'N/A'
            change = f"{data['change_pct']:.2f}" if data['change_pct'] else 'N/A'
            rsi = f"{data['rsi']:.2f}" if data['rsi'] else 'N/A'
            macd = f"{data['macd']:.2f}" if data['macd'] else 'N/A'
            atr = f"{data['atr_pct']:.2f}" if data['atr_pct'] else 'N/A'
            print(f"{data['ticker']:<10} {price:>10} {change:>10} {rsi:>8} {macd:>10} {atr:>8} {data['recommendation'] or 'N/A':>8}")
        
        print("\n" + "=" * 60)
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