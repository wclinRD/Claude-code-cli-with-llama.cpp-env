---
name: stock-analysis
description: 以日線級別分析價格行為、均線、技術指標、纏論、波浪理論、葛蘭威爾法則，評估個股/ETF/大盤並生成精美圖表，提供日線交易策略及進出場點位，並提供簡單結論
license: MIT
compatibility: opencode
metadata:
  version: "1.0.0"
  author: "opencode user"
  tags: ["stock", "technical-analysis", "trading", "chan-theory", "wave-theory"]
---

# Stock Analysis Skill

股票技術分析 Skill - 日線級別綜合分析工具

## 功能說明

本 Skill 提供完整的技術分析功能：

### 數據來源
- **yfinance**: 美股、ETF、熱門港股 (免 API Key，15分鐘延遲)
- **TWSE API**: 台股大盤/個股 (免費，即時)

### 分析項目

1. **價格行為分析**
   - 支撐/阻力位計算
   - 缺口分析
   - 趨勢線
   - 型態辨識 (頭肩、W底、M頭、三角形)

2. **均線分析 + 葛蘭威爾八大法則**
   - MA5/10/20/60/120/240
   - 均線排列 (多頭/空頭)
   - 葛蘭威爾法則 1-8 訊號

3. **技術指標**
   - RSI (14) 超買/超賣
   - MACD 金叉/死叉/背離
   - KD 值
   - OBV 能量潮

4. **纏論分析**
   - 筆與線段劃分
   - 中樞認定
   - 走勢類型判斷

5. **波浪理論**
   - 推動浪辨識
   - 修正浪判斷
   - 黃金分割率

6. **交易策略**
   - 日線級別訊號
   - 進場/退場點位
   - 停損建議

7. **圖表輸出**
   - Markdown 表格
   - SVG 圖形

## 使用方式

### 指令格式

```
/stock-analysis <股票代碼> [選項]
```

### 範例

```
/stock-analysis AAPL
/stock-analysis 2330.TW
/stock-analysis 0050
/stock-analysis AAPL --period 1y --chart svg
```

### 選項

| 選項 | 說明 | 預設 |
|------|------|------|
| --period | 資料期間 | 6mo |
| --chart | 圖表類型 (text/svg/both) | both |
| --source | 數據來源 (auto/yfinance/twse) | auto |

## 輸出範例

分析完成後會輸出：
1. 綜合評估摘要
2. 各項技術分析結果表格
3. 圖形化股價走勢圖
4. 交易策略建議 (進/退場點位)
5. 提供簡單結論

## 安裝依賴

```bash
pip install yfinance pandas numpy requests
```

或使用 uv:
```bash
uv pip install yfinance pandas numpy requests
```

## 執行範例

```bash
# 分析美股
python analyzer.py AAPL
python analyzer.py MSFT --period 1y

# 分析台股
python analyzer.py 2330.TW
python analyzer.py 0050 --period 6mo

# 輸出文字報告
python analyzer.py AAPL --chart text

# 輸出 SVG 圖表
python analyzer.py AAPL --chart svg
```