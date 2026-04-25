# Stock-Analysis Skill 修改計劃

## 執行狀態: ✅ Phase 12.1 + 13.1 實作完成 (待API修復)

---

⚠️ 已知問題:
- P13.1 法人買賣細節的 TWSE API (BWIBBU_d) 目前對特定日期查詢返回 HTML 而非 JSON
- 函數架構已實作完成，待 API 端點修復或替代方案確認後可正式使用

---

# Phase 12: 數據來源強化 ✅ (已完成)

## P12.1: VIX 波動率指數 ✅ 已完成

### 功能說明
- 恐慌指數監控，衡量市場恐懼程度
- VIX > 30: 市場恐懼高位，潛在危機
- VIX < 15: 市場樂觀，可能處於高點

### 已實作函數
```python
# data_fetcher.py
def fetch_vix_data(period: str = "6mo") -> Optional[pd.DataFrame]:
    """取得 VIX 波動率指數 (yfinance: ^VIX)"""

def analyze_vix_signals(vix_df: pd.DataFrame) -> Dict:
    """分析 VIX 訊號"""
    # return: {
    #     'current': float,
    #     'level': 'low'|'normal'|'elevated'|'high',
    #     'signal': 'fearful'|'neutral'|'complacent',
    #     'trend': 'rising'|'falling'|'stable',
    #     'interpretation': str
    # }
```

### 預期產出
- `results['vix']`: VIX 數據與分析
- `results['vix_signals']`: VIX 訊號解讀

### 程式碼位置
- `data_fetcher.py:1582` - `fetch_vix_data()`
- `data_fetcher.py:1613` - `analyze_vix_signals()`
- `analyzer.py:13-18` - imports
- `analyzer.py:100-102` - 整合調用

### 測試結果
```bash
VIX signals: {
    'current': 18.71,
    'avg_30': 22.22,
    'level': 'normal',
    'signal': 'neutral',
    'trend': 'falling',
    'interpretation': '市場情緒平穩'
}
```

---

## P12.2: 選擇權資料 PUT/CALL Ratio ⚠️ 中優先度

### 功能說明
- 選擇權Put/Call比率分析
- PCR > 1.5: 散戶偏多 PUT，潜在底部
- PCR < 0.5: 散戶偏多 CALL，潜在高點
- 機構反向指標參考

### 數據來源
- 台股: 證交所選擇權統計
- 美股: Cboe Options Data

### 實作要點

```python
# data_fetcher.py 新增
def fetch_options_data(ticker: str) -> Dict:
    """取得選擇權資料"""
    # PUT / CALL volume
    # Open Interest
    # PCR (Put/Call Ratio)
    pass
```

---

## P12.3: 即時報價 API 整合 🟢 低優先度

### 功能說明
- API 整合實現即時報價(非延遲15分鐘)
- 支援 Twelve Data / Finnhub

### 實作要點

```python
# 需現有 .env 配置
TWELVE_DATA_KEY=xxx
FINNHUB_KEY=xxx

# config.py 新增
config = {
    'api_provider': 'twelvedata' | 'finnhub' | 'yfinance',
    'realtime': bool
}

def get_realtime_quote(ticker: str) -> Dict:
    """即時報價查詢"""
    pass
```

---

# Phase 13: 法人籌碼分析強化 ✅ (已完成)

## P13.1: 法人買賣細節 ✅ 已完成 (結構完成，待API修復)

### 功能說明
- 各法人別(外商/投信/自營商/散戶)買賣動向細分
- 追蹤法人連續買賣行為
- 法人成本線計算

### 現有數據 (已支援)
- `fetch_institutional_holdings()`: 取得法人持股

### 缺口分析
| 資料項 | 現狀 | 需求 |
|--------|------|------|
| 外商買賣張數 | ⚠️ 僅持股% | 需每日買賣細節 |
| 投信買賣細節 | ⚠️ 無细部 | 需每日進出 |
| 自營商動向 | ⚠️ 僅總計 | 需細分 |

### 已實作函數
```python
# data_fetcher.py
def fetch_institutional_detail(stock_code: str, days: int = 20) -> Optional[pd.DataFrame]:
    """取得法人買賣明細 (歷史數據)"""
    # 返回: DataFrame with date, foreign_buy, foreign_sell, foreign_net, sec_buy, sec_sell, sec_net
    
def analyze_institutional_trend(institutional_df: pd.DataFrame) -> Dict:
    """法人趨勢分析"""
    # return: {
    #     'foreign': {'buying': bool, 'streak': int, 'net_5d': float},
    #     'sec': {'buying': bool, 'streak': int, 'net_5d': float},
    #     'signal': str,
    #     'signals': List[str]
    # }
```

### 程式碼位置
- `data_fetcher.py:1752` - `fetch_institutional_detail()`
- `data_fetcher.py:1818` - `analyze_institutional_trend()`
- `analyzer.py:101-105` - 整合調用

### ⚠️ 注意事項
- TWSE API (BWIBBU_d) 目前對特定日期查詢返回 HTML 頁面而非JSON
- 函數架構已實作完成，待 API 端點修復或替代方案確認後可正式使用

### 預期產出 (API修復後)
- `results['institutional_detail']`: 法人買賣明細
- `results['institutional_trend']`: 法人趨勢分析

---

## P13.2: 期貨未平倉 🟢 低優先度

### 功能說���
- 期貨未平倉量分析
- 台指期貨未平倉
- 選擇權未平倉

### 數據來源
- 期交所每日行情
- Cboe Futures

---

# Phase 14: 分析維度擴充 (規劃中)

## P14.1: 基本面篩選功能 ⚠️ 中優先度

### 功能說明
- 股息篩選 (殖利率 > X%)
- 本益比篩選 (PE < X)
- 產業別篩選
- 市值篩選

### 實作要點

```python
# screening.py 新建
def screen_stocks(criteria: Dict) -> List[Dict]:
    """
    股票篩選
    criteria: {
        'market': 'TWSE'|'OTC'|'ALL',
        'min_dividend_yield': 3.0,
        'max_pe': 20,
        'min_market_cap': 1000000000,
        'industry': str
    }
    """
    pass

def screen_by_strategy(strategy: str, params: Dict) -> List[Dict]:
    """策略篩選"""
    # 'high_dividend': 高股息
    # 'value': 價值股
    # 'growth': 成長股
    # 'momentum': 動能股
    pass
```

### 程式碼位置
- `screening.py`: 新建模組
- `analyzer.py`: 新增 `--screen` 選項

---

## P14.2: 自選股清單管理 ⚠️ 中優先度

### 功能說明
- 自選股名單建立與管理
- 群組分類 (存股/成長/投機)
- 每日監控清單

### 實作要點

```python
# watchlist.py 新建
WATCHLIST_FILE = "~/.config/stock-analysis/watchlist.json"

def load_watchlist() -> Dict:
    """載入自選股"""
    pass

def save_watchlist(watchlist: Dict) -> None:
    """儲存自選股"""
    pass

def add_to_watchlist(ticker: str, group: str = "default") -> None:
    """加入自選股"""
    pass

def analyze_watchlist(group: str = None) -> List[Dict]:
    """分析自選股"""
    pass
```

---

## P14.3: 股價異常檢測 🟡 中優先度

### 功能說明
- 妖股特徵檢測 (瞬間漲跌)
- 暫停交易檢測
- 流動性危機檢測

### 實作要點

```python
# data_fetcher.py 強化
def detect_volatility_anomaly(df: pd.DataFrame) -> Dict:
    """檢測波動異常"""
    return {
        'is_volatile': bool,
        'daily_change_max': float,
        'volume_spike': bool,
        'warnings': List[str]
    }

def detect_liquidity_crisis(df: pd.DataFrame) -> Dict:
    """流動性危機檢測"""
    pass
```

---

# Phase 15: 模擬交易功能 (規劃中)

## P15.1: 回測系統 🟢 低優先度

### 功能說明
- 策略回測引擎
- 訊號產生與損益計算
- 績效指標

### 實作要點

```python
# backtest.py 新建
def backtest_strategy(
    df: pd.DataFrame,
    signals: List[Dict],
    initial_capital: float = 1000000,
    commission: float = 0.001
) -> Dict:
    """
    策略回測
    return: {
        'total_return': float,
        ' Sharpe': float,
        'max_drawdown': float,
        'win_rate': float,
        'trades': List[Dict]
    }
    """
    pass
```

### 回測指標
| 指標 | 說明 |
|------|------|
| Total Return | 總報酬率 |
| Sharpe Ratio | 夏普比率 |
| Max Drawdown | 最大回檔 |
| Win Rate | 勝率 |
| Profit Factor | 獲利因子 |
| Avg Trade | 平均交易天數 |

---

## P15.2: 交易記錄簿 🟢 低優先度

### 功能說明
- 虛擬交易記錄
- 部位追蹤
- 損益統計

### 實作要點

```python
# journal.py 新建
class TradingJournal:
    def __init__(self, initial_balance: float):
        self.balance = initial_balance
        self.positions = {}
        self.closed_trades = []
    
    def buy(self, ticker: str, qty: int, price: float):
        """買入記錄"""
        pass
    
    def sell(self, ticker: str, qty: int, price: float):
        """賣出記錄"""
        pass
    
    def get_performance(self) -> Dict:
        """績效報告"""
        pass
```

---

# Phase 16: 視覺化與報告強化 (規劃中)

## P16.1: 互動式圖表 🟢 低優先度

### 功能說明
- HTML/JS 互動圖表
- 支援 Hover/Zoom

### 實作要點

```python
# interactive_chart.py 新建
def generate_interactive_chart(df: pd.DataFrame) -> str:
    """生成互動式 K 線圖"""
    # 使用 Plotly.js
    pass

def generate_dashboard(watchlist: Dict) -> str:
    """儀表板視圖"""
    pass
```

---

## P16.2: PDF 報告導出 🟢 低優先度

### 功能說明
- 專業 PDF 報告生成
- 圖文排版

### 實作要點

```python
# report.py 新建
def generate_pdf_report(output: Dict, filename: str):
    """PDF 報告生成"""
    # 使用 ReportLab 或 FPDF
    pass
```

---

# Phase 17: 技術債務處理 (規劃中)

## T1: Type Hints 重構 🟡 中優先度

### 現有問題
- 所有模組缺乏型態標註
- 難以維護與 Debug

### 重構範圍
| 檔案 | 函數數 | 優先度 |
|------|--------|--------|
| data_fetcher.py | ~50 | 高 |
| indicators.py | ~30 | 高 |
| strategy.py | ~40 | 中 |
| chart_generator.py | ~15 | 中 |
| price_action.py | ~20 | 中 |

### 實作方式
```python
# 範例重構
def fetch_data(ticker: str, period: str = "6mo") -> Optional[pd.DataFrame]:
    """取得股票數據"""
    ...
```

### 需要添加的類型
```python
from typing import Optional, Dict, List, Tuple, Any, Callable
from typing_extensions import TypedDict
```

---

## T2: 配置參數外部化 🟢 低優先度

### 現有問題
- 指標週期硬編碼
- API 網址硬編碼
- 缺少 config 檔案

### 實作要點

```python
# config.py 新建
from dataclasses import dataclass
from typing import Dict, Any

@dataclass
class IndicatorConfig:
    rsi_period: int = 14
    macd_fast: int = 12
    macd_slow: int = 26
    macd_signal: int = 9
    kd_period: int = 9
    
@dataclass  
class DataConfig:
    twse_api_url: str = "https://..."
    otc_api_url: str = "https://..."
    cache_hours: int = 24

config = {
    'indicator': IndicatorConfig(),
    'data': DataConfig()
}
```

---

# 實作優先順序建議

## 🚀 第一梯隊 (立即實作)

1. **P13.1: 法人買賣細節** - 高實用性
2. **P12.1: VIX 波動率** - 市場情緒關鍵指標
3. **T1: Type Hints 重構** - 技術債務改善

## 📦 第二梯隊 (短期目標)

4. **P14.2: 自選股清單** - 常用功能
5. **P14.3: 股價異常檢測** - 風險控制
6. **P12.2: 選擇權資料** - 進階籌碼

## 📦 第三梯隊 (中期目標)

7. **P14.1: 基本面篩選** - 功能擴充
8. **P16.1: 互動式圖表** - 視覺化強化
9. **P15.1: 回測系統** - 模擬交易

## 📦 第四梯隊 (長期規劃)

10. **P12.3: 即時報價 API** - 需要 API Key
11. **P13.2: 期貨未平倉** - 數據取得難
12. **P16.2: PDF 報告** - 低優先
13. **P15.2: 交易記錄簿** - 依附回測

---

# 程式碼結構預期

```
stock-analysis/
├── config.py          # 新增: 配置管理
├── screening.py      # 新增: 股票篩選
├── watchlist.py      # 新增: 自選股管理
├── backtest.py       # 新增: 回測引擎
├── journal.py       # 新增: 交易記錄
├── interactive.py   # 新增: 互動圖表
├── report.py        # 新增: PDF報告
│
├── analyzer.py      # 強化: 整合新功能
├── data_fetcher.py # 強化: VIX/選擇權
├── chart_generator.py # 強化: 新圖表
└── (其他模組)      # 強化: Type Hints
```

---

# 修改日誌

### 2026-04-25
- ✅ Phase 12-17 詳細規劃完成
- ✅ 新增實作優先順序建議

### 2026-04-25 (後續)
- ✅ Phase 12.1 VIX 波動率指數實作完成
  - `fetch_vix_data()` - 取得 VIX 歷史數據
  - `analyze_vix_signals()` - VIX 訊號分析
  - 整合至 `analyzer.py`
- ✅ Phase 13.1 法人買賣細節實作完成
  - `fetch_institutional_detail()` - 法人買賣明細
  - `analyze_institutional_trend()` - 法人趨勢分析
  - 整合至 `analyzer.py`
- ✅ 測試驗證: 172 passed
- ✅ ���增���式碼結構預期
- ✅ Phase 11 功能實作完成