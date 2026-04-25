#!/usr/bin/env python3
"""
即時報價查詢工具
用法: python quote.py <股票代碼或名稱> [<股票2> <股票3> ...]
範例:
  python quote.py 2330
  python quote.py 台積電 台達電 鴻海
  python quote.py 2330 2308 2317 0050
"""

import sys
import os
import time

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from data_fetcher import (
    fetch_realtime_quote,
    fetch_multiple_quotes,
    resolve_stock_code,
    detect_otc_market
)


def main():
    import argparse
    
    parser = argparse.ArgumentParser(description='即時報價查詢工具')
    parser.add_argument('stocks', nargs='*', help='股票代碼或名稱 (省略則顯示大盤)')
    parser.add_argument('-w', '--watch', action='store_true', help='持續監控')
    parser.add_argument('-i', '--interval', type=int, default=3, help='監控間隔秒數')
    args = parser.parse_args()
    
    if not args.stocks:
        stocks = ['0050']
    else:
        stocks = args.stocks
    
    stock_codes = []
    otc_codes = []
    
    for arg in stocks:
        code = resolve_stock_code(arg)
        if code:
            if detect_otc_market(code):
                otc_codes.append(code)
            else:
                stock_codes.append(code)
        elif arg.isdigit():
            if detect_otc_market(arg):
                otc_codes.append(arg)
            else:
                stock_codes.append(arg)
        else:
            print(f"無法識別: {arg}")
    
    all_codes = stock_codes + otc_codes
    
    if not all_codes:
        print("沒有有效的股票代碼")
        return
    
    if args.watch:
        watch_quotes(all_codes, args.interval, stock_codes, otc_codes)
    else:
        show_quotes(all_codes, stock_codes, otc_codes)


def show_quotes(all_codes, stock_codes, otc_codes):
    tse_quotes = []
    otc_quotes = []
    
    if stock_codes:
        tse_quotes = fetch_multiple_quotes(stock_codes, "tse")
    
    if otc_codes:
        otc_quotes = fetch_multiple_quotes(otc_codes, "otc")
    
    quotes = tse_quotes + otc_quotes
    
    if not quotes:
        print("無法取得報價")
        return
    
    print("=" * 50)
    print("即時報價")
    print("=" * 50)
    
    for q in quotes:
        code = q['code'] or 'N/A'
        name = q['name'] or 'N/A'
        price = q['close'] or 0
        prev = q['prev_close'] or 0
        change = price - prev
        change_pct = (change / prev * 100) if prev > 0 else 0
        volume = q['volume'] or 0
        
        sign = "+" if change >= 0 else ""
        print(f"{code:>6} {name:<10} {price:>8.2f} {sign}{change:.2f} ({sign}{change_pct:>5.2f}%) 成交量: {volume:,}")
        print(f"       開: {q['open']:.2f}  高: {q['high']:.2f}  低: {q['low']:.2f}  昨收: {prev:.2f}")
        print()


def watch_quotes(all_codes, interval=3, stock_codes=None, otc_codes=None):
    import time
    
    if stock_codes is None:
        stock_codes = []
    if otc_codes is None:
        otc_codes = []
    
    print("Ctrl+C 結束監控")
    print("=" * 50)
    
    prev_prices = {}
    
    try:
        while True:
            tse_quotes = []
            otc_quotes = []
            
            if stock_codes:
                tse_quotes = fetch_multiple_quotes(stock_codes, "tse")
            
            if otc_codes:
                otc_quotes = fetch_multiple_quotes(otc_codes, "otc")
            
            quotes = tse_quotes + otc_quotes
            
            if not quotes:
                print("無法取得報價")
                time.sleep(interval)
                continue
            
            print(f"\n--- {time.strftime('%H:%M:%S')} ---")
            
            for q in quotes:
                code = q['code'] or 'N/A'
                name = q['name'] or 'N/A'
                price = q['close'] or 0
                prev = q['prev_close'] or 0
                
                change = price - prev
                change_pct = (change / prev * 100) if prev > 0 else 0
                
                color = ""
                if code in prev_prices:
                    prev_price = prev_prices[code]
                    if price > prev_price:
                        color = "↑"
                    elif price < prev_price:
                        color = "↓"
                
                sign = "+" if change >= 0 else ""
                print(f"{code:>6} {name:<10} {price:>8.2f} {sign}{change:.2f} ({sign}{change_pct:>5.2f}%) {color}")
                
                prev_prices[code] = price
            
            time.sleep(interval)
    
    except KeyboardInterrupt:
        print("\n結束監控")


if __name__ == "__main__":
    main()