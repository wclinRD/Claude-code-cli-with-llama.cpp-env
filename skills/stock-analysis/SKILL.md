---
name: stock-analysis
description: 專業股市技術分析工具，模擬基金經理人分析邏輯，支援台股/美股/ETF 完整分析，包含技術指標、進階指標、籌碼分析、總體經濟、新聞情緒、評價分析，輸出專業投資報告。當未指定股票時，自動分析大盤整體走勢（美股看 S&P 500，台股看加權指數）
license: MIT
compatibility: opencode
metadata:
  version: "4.0.0"
  author: "opencode user"
  tags: ["stock", "technical-analysis", "trading", "professional", "taiwan-stock", "us-stock"]
---

# Stock Analysis Skill

專業股市技術分析工具 - 模擬基金經理人分析邏輯

## 功能說明

本 Skill 提供專業級的技術分析服務，模擬專業基金經理人的投資決策流程：

### 數據來源
- **yfinance**: 美股、ETF (免 API Key，15 分鐘延遲)
- **TWSE API**: 上市股票 (免費)
- **櫃買中心**: 上櫃股票 (6 開頭)
- **Stock Lookup Table**: 台灣/美股代號對照表
- **產業基本面**: 本益比、殖利率、市值
- **網路爬蟲**: 即時財經新聞 (無需 API)

### 股票代號查詢 (API 方式)
使用 OpenAPI API 即時查詢公司名稱↔代號對應：

```python
import requests

# 查詢公司名稱對應的股票代號
def get_company_by_name(name: str) -> list[dict]:
    """根據公司名稱查詢所有匹配的股票代號"""
    url = "https://openapi.twse.com.tw/v1/company/newlisting"
    response = requests.get(url)
    if response.status_code == 200:
        data = response.json()
        results = []
        for item in data:
            company = item.get("Company", "").strip()
            if name in company:
                results.append({
                    "code": item.get("Code"),
                    "name": company,
                    "listed_date": item.get("ListedDate"),
                })
        return results
    return []

# 查詢股票代號對應的公司名稱
def get_twse_company(code: str) -> dict | None:
    """根據股票代號查詢公司名稱"""
    url = "https://openapi.twse.com.tw/v1/company/newlisting"
    response = requests.get(url)
    if response.status_code == 200:
        data = response.json()
        for item in data:
            if item.get("Code") == code:
                return item
    return None

# 範例使用
companies = get_company_by_name("台")
# 返回：[{'code': '2330', 'name': '台灣實業股份有限公司', ...}]
```

### 分析維度

#### 1. 技術分析
- RSI (14) 超買/超賣偵測
- MACD 金叉/死叉/背離
- KD 隨機指標
- 布林帶 (Bollinger Bands)
- CCI 商品通道指標
- DMI 趨向指標 (+DI/-DI/ADX)
- 威廉指標
- ATR 平均真實波幅

#### 2. 趨勢動能分析
- 5 日/20 日/60 日漲跌幅
- 均線排列判斷 (多頭/空頭)
- 動能強度評估

#### 3. 總體經濟環境
- 美元/台幣匯率
- 原油價格 (WTI)
- 黃金價格
- 美國 10 年公債殖利率
- S&P 500 / NASDAQ 指數

#### 4. 市場情緒分析
- 新聞關鍵字情緒偵測
- 個股相關新聞彙整
- 市場整體氛圍判斷

#### 5. 評價分析
- 本益比 (PE Ratio)
- 殖利率
- 市值評估

#### 6. 籌碼分析
- 法人持股 (外商/投信/自營商)
- 融資融券餘額

#### 7. 進階技術理論
- 纏論分析 (筆、線段、中樞)
- 波浪理論 (艾略特波浪)
- 黃金分割率

### 輸出報告

#### 專業投資報告格式
```
📈 專業投資分析報告 - [股票名稱] ([代碼])
=================================================================

🎯 【投資評等】
  [買入/觀望/賣出] (Hold/Buy/Sell)
  綜合評分：XX/100
  建議部位：[積極型/穩健型/保守型/觀望型]

💼 【投資論點】
  1. [利多因素 1]
  2. [利多因素 2]
  ...

⚠️ 【風險提醒】
  1. [風險因素 1]
  2. [風險因素 2]
  ...

📊 【技術分析】: [偏多/偏空/中立]
🌍 【總體環境】: [有利/不利/中性]
📰 【市場情緒】: [偏多/偏空/中立]
💰 【評價分析】: [合理/偏高/偏低]

📌 【結論】
  [综合评估与操作建议]
=================================================================
```

## 使用方式

### 指令格式

```
/stock-analysis [股票代碼] [選項]
```

### 省略股票代碼時

當未指定股票代碼時，自動分析大盤整體走勢：
- **美股**：S&P 500 (^GSPC) + NASDAQ (^IXIC)
- **台股**：加權指數 (^TWII)

這可以快速掌握整體市場動態，不用輸入特定股票代碼。

### 範例

```bash
# 分析大盤整體走勢（美股/台股自動判斷）
/stock-analysis

# 分析台股大盤
/stock-analysis ^TWII
/stock-analysis 0050
/stock-analysis 2330.TW

# 分析美股大盤
/stock-analysis ^GSPC
/stock-analysis SPY

# 分析美股
/stock-analysis AAPL
/stock-analysis NVDA

# 分析 ETF
/stock-analysis 00918
/stock-analysis 00919

# 調整分析期間
/stock-analysis 2308 --period 1y
/stock-analysis 0050 --period 3mo

# 使用代號查詢表 (名稱↔代號) - API 方式
/stock-analysis 台積電
/stock-analysis 聯電
/stock-analysis 世芯
/stock-analysis Apple
/stock-analysis NVIDIA

### 選項

| 選項 | 說明 | 預設 |
|------|------|------|
| --period | 資料期間 (1mo/3mo/6mo/1y/2y/5y) | 6mo |
| --chart | 圖表類型 (text/svg/both) | both |
| --compare | 多股票比較 | - |

### 多股票比較範例

```bash
python analyzer.py 0050 --compare 0051 00919
```

## 支援市場

| 類型 | 代碼範例 |
|------|----------|
| 台股上市 | 2330, 2308, 2454, 0050 |
| 台股上櫃 | 6415, 6515, 8255 |
| 台股 ETF | 0050, 0051, 00918, 00919, 00929 |
| 美股 | AAPL, MSFT, NVDA, TSLA |
| 美股 ETF | SPY, QQQ, VTI |
| 股票代號查詢 | API (OpenAPI.twse.com.tw) |

## 安裝依賴

```bash
pip install yfinance pandas numpy requests beautifulsoup4
```

或使用 uv:
```bash
uv pip install yfinance pandas numpy requests beautifulsoup4
```

## 執行範例

```bash
# 基本分析
python analyzer.py 2308

# 長期趨勢分析
python analyzer.py 2308 --period 1y

# 文字報告輸出
python analyzer.py 2308 --chart text

# 多股票比較
python analyzer.py 0050 --compare 0051 00919

# 使用 API 查詢公司名稱
python analyzer.py "台積電"
python analyzer.py "聯電"
python analyzer.py "世芯"
python analyzer.py "Apple"
python analyzer.py "NVIDIA"
```

## 分析維度說明

### 投資評分邏輯
- 技術面權重 30%
- 總體環境權重 20%
- 趨勢動能權重 20%
- 市場情緒權重 15%
- 評價面權重 15%

### 部位建議
| 評分 | 建議部位 | 比重 |
|------|----------|------|
| 80+ | 積極型 | 30% |
| 60-79 | 穩健型 | 20% |
| 40-59 | 保守型 | 10% |
| <40 | 觀望型 | 5% |

### 風險報酬比評估
- ≥3.0 : 極佳
- 2.0-2.9 : 良好
- 1.5-1.9 : 一般
- <1.0 : 較差

## 版本紀錄

- v4.0.0: 新增 OpenAPI API 即時查詢公司名稱↔股票代號
- v3.0.0: 專業投資報告格式，模擬基金經理人分析邏輯
- v2.0.0: 新增多股票比較、產業分析、總體經濟數據
- v1.0.0: 基礎技術分析功能
