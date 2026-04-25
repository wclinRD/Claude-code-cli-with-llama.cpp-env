# Stock-Analysis Skill 修改計劃

## 執行狀態: ✅ Phase 7 完成 (技術指標擴充)

---

## Phase 7: 技術指標擴充 ✅ (已完成)

### P7.1: 已完成 ✅

| 優先度 | 項目 | 說明 |
|--------|------|------|
| ✅ | MFI | Money Flow Index - 資金流量 |
| ✅ | Stochastic | 完整版隨機指標 (K, D, SD) |
| ✅ | VWAP | Volume Weighted Average Price |
| ✅ | ATR-Gao | 改進版 ATR |
| ✅ | K 線圖 | generate_candlestick_svg() |
| ✅ | 指標子圖 | generate_indicator_panel_svg() |

### P7.2: 測試驗證

```
58 tests passed ✅
新增指標全部通過驗證
```

---

## Phase 6: 數據穩定性強化 🟡

### P6.1: 已完成 ✅

| 優先度 | 項目 | 說明 |
|--------|------|------|
| ✅ | validate_dataframe() | DataFrame 驗證函數 |
| ✅ | validate_price() | 價格合理性驗證 |
| ✅ | load_from_cache() | 快取載入 |
| ✅ | save_to_cache() | 快取保存 |
| ✅ | rate_limit() | 速率限制裝飾器 |
| ✅ | 增強 retry_on_failure() | 加入 backoff 參數 |

### P6.2: 新增函數

```
data_fetcher.py 新增:
- validate_dataframe(df, required_columns)
- validate_price(price, symbol)
- get_cache_path(ticker, data_type)
- load_from_cache(ticker, data_type, max_age_hours)
- save_to_cache(df, ticker, data_type)
- clear_cache(ticker)
- rate_limit(host) 裝飾器工廠
- 增強 retry_on_failure(backoff)
```

---

### P5.1: 評估發現的問題 (已修復 ✅)

| 優先度 | 問題 | 檔案 | 狀態 |
|--------|------|------|------|
| ✅ | RSI 除零風險 (line 26) | indicators.py | ✅ 已修復 |
| ✅ | 裸異常處理 (38處) | data_fetcher.py | ✅ 已修復 |
| ✅ | 缺少 lxml 依賴 | requirements.txt | ✅ 已修復 |
| ✅ | pytest.mark.integration 未註冊 | tests/conftest.py | ✅ 已修復 |

### P5.2: 修復進度

```
[x] indicators.py RSI 除零修復
[x] data_fetcher.py 異常處理強化
[x] requirements.txt 依賴補全
[x] pytest 標記註冊
[x] 測試驗證: 158 passed ✅
```

### P5.3: 修復明細

| 檔案 | 修復內容 |
|------|----------|
| indicators.py:26 | RSI 除零: 使用 np.where() 處理 avg_loss=0 |
| indicators.py:61 | KD 除零: denom.replace(0, np.nan) |
| indicators.py:230 | Williams%R 除零: 添加分母保護 |
| indicators.py:246 | CCI 除零: 添加分母保護 |
| indicators.py:264-277 | DMI 除零: atr 和 di_sum 保護 |
| data_fetcher.py:434,454,619,733,1323,1371 | 裸異常改為 `except Exception` |
| requirements.txt | 新增 lxml, pytest |
| tests/conftest.py | 註冊 pytest.mark.integration |

---

## Phase 0-4: 已完成 ✅

### P4.1: 測試驗證結果

```
158 tests collected
158 passed ✅
```

### P4.2: 已修正項目

| 狀態 | 項目 | 說明 |
|------|------|------|
| ✅ | detect_market() | 美股回傳 "NASDAQ" (而非 "US") |
| ✅ | resolve_stock_code() | 新增美股代碼直接返回邏輯 |
| ✅ | API 重試機制 | get_stock_code_list() / search_stock_by_name() 失敗時自動重試 3 次 |

### P4.3: 未來強化 (暂不執行) ⚪

| 優先度 | 項目 | 說明 |
|--------|------|------|
| 🟡 中 | 輸入驗證 | 股票代碼格式驗證 |
| 🟢 低 | 更多技術指標 | STOCHRSI, ADX 等 |

---

## Phase 0-3: 已完成 ✅

### P0.1: indicators.py 除零問題修復

| 狀態 | 項目 | 行號 |
|------|------|------|
| ✅ | RSI 計算: avg_loss 為 0 時除零 | 26 |
| ✅ | KD 計算: high_n - low_n 為 0 | 59 |
| ✅ | ATR 計算: df['Close'] 為 0 | 211 |
| ✅ | Williams%R: 分母為 0 | 226 |
| ✅ | CCI 計算: mean_deviation 為 0 | 242 |
| ✅ | DMI 計算: atr 為 0, di_sum 為 0 | 260, 269 |

> 測試驗證：indicators.py 所有 30 個測試通過

### P0.2: price_action.py 邏輯錯誤修復

| 狀態 | 項目 | 行號 |
|------|------|------|
| ✅ | W底偵測 end_idx 邏輯錯誤 | 222 |
| ✅ | M頭偵測 end_idx 邏輯錯誤 | 276 |

---

## Phase 1: 功能完整性 🟡

### P1.1: 補全葛蘭威爾八大法則

| 狀態 | 法則 | 內容 |
|------|------|------|
| ✅ | 1 | MA4 從下降轉為上升，股價突破 MA4 |
| ✅ | 2 | 股價突破 MA4 後回測不跌破 |
| ✅ | 3 | 股價在 MA4 上方，突然跌破 MA4 又站回 |
| ✅ | 4 | MA4 上升，股價從下突破 MA4 |
| ✅ | 5 | MA4 下降，股價從上跌破 MA4 |
| ✅ | 6 | 股價快速下跌遠離 MA4，出現反彈 |
| ✅ | 7 | 股價離 MA4 越來越遠，應獲利了結 |
| ✅ | 8 | MA4 從上升轉為下跌，股價跌破 MA4 |

### P1.2: 均線計算彈性化

| 狀態 | 項目 |
|------|------|
| ✅ | 根據資料長度動態計算 MA (不強制要求240天) |
| ✅ | 資料不足時顯示 NaN 而非直接返回 |

---

## Phase 2: 測試框架建立 🟢

### P2.1: 測試目錄結構

```
tests/
├── __init__.py
├── conftest.py          # 共用 fixture
├── test_indicators.py   # 技術指標測試 (30 tests)
└── test_moving_avg.py   # 均線測試 (28 tests)
```

### P2.2: 測試結果

```
============================= test session starts ==============================
58 passed in 0.67s
=============================
```

---

## 修改檔案清單

| 檔案 | 變更 |
|------|------|
| `moving_avg.py` | 均線彈性化 + 葛蘭威爾法則 4,5 補全 |
| `price_action.py` | 修復 end_idx 邏輯錯誤 |
| `tests/__init__.py` | 新建 |
| `tests/conftest.py` | 新建共用 fixtures |
| `tests/test_indicators.py` | 新建 30 個測試 |
| `tests/test_moving_avg.py` | 新建 28 個測試 |
| `tests/test_price_action.py` | 新建 22 個測試 |
| `tests/test_chan_theory.py` | 新建 18 個測試 |
| `tests/test_wave_theory.py` | 新建 22 個測試 |
| `tests/test_strategy.py` | 新建 23 個測試 |
| `tests/test_analyzer_integration.py` | 新建 15 個測試 |
| `todo.md` | 新建 |

---

## 未來強化 (暂不執行) ⚪

### 優先強化項目

| 優先度 | 項目 | 說明 |
|--------|------|------|
| 🔴 高 | API 重試機制 | data_fetcher.py 網路請求失敗時自動重試 |
| 🔴 高 | 快取機制 | 避免重複 API 呼叫造成浪費 |
| 🟡 中 | 輸入驗證 | 股票代碼格式驗證 |
| 🟡 中 | quote.py 函數補全 | get_latest_price 函數 |
| 🟢 低 | 更多技術指標 | STOCHRSI, ADX 等 |

### 發現的潛在問題

| 狀態 | 項目 | 說明 |
|------|------|------|
| ⚠️ | detect_market() 回傳 "US" | 與預期 "NASDAQ" 不同 |
| ⚠️ | quote.py 缺少 get_latest_price | 需要從 data_fetcher 導入或補全 |
| ✅ | 測試覆蓋 | 153 個測試全部通過 |

---

## Phase 6: 數據穩定性強化 🔴

### P6.1: 待項目

| 優先度 | 項目 | 說明 |
|--------|------|------|
| 🔴 高 | 全域錯誤處理裝飾器 | `@retry_api` 裝飾器处理 API 請求失敗 |
| 🔴 高 | 數據驗證 | null check、範圍合理性驗證 |
| 🟡 中 | Rate limit 處理 | yfinance 15min/req 限制 |
| 🟡 中 | 離線緩存 | SQLite/File cache |

---

## Phase 7: 技術指標擴充 🟡

### P7.1: 待項目

| 優先度 | 項目 | 說明 |
|--------|------|------|
| 🔴 高 | MFI | Money Flow Index - 資金流量 |
| 🔴 高 | ADX | Average Directional Index - 趨勢強度 |
| 🔴 高 | Stochastic | 隨機指標 |
| 🟡 中 | CCI | Commodity Channel Index |
| 🟡 中 | VWAP | Volume Weighted Average Price |
| 🟢 低 | 多週期分析 | 日/週/月 RSI 對比 |
| 🟢 低 | 背離偵測 | 價格 vs 指標背離 |

### P7.2: 需新增函數

```
indicators.py 新增:
- calculate_mfi(df, period=14)
- calculate_adx(df, period=14)
- calculate_stochastic(df, k=14, d=3)
- calculate_vwap(df)
- detect_divergence_advanced(df, indicator)
```

---

## Phase 8: 纏論/型態強化 🟡

### P8.1: 待項目

| 優先度 | 項目 | 說明 |
|--------|------|------|
| 🔴 高 | 筆識別算法優化 | 更嚴謹的包含處理 |
| 🔴 高 | 筆破壞判斷 | 筆被後續筆破壞的判斷 |
| 🟡 中 | 頭肩頂/底識別 | Head and Shoulders |
| 🟡 中 | 旗型/旗竿識別 | Flag/Pennant |
| 🟢 低 | 楔形整理 | Wedge |

### P8.2: 需優化函數

```
chan_theory.py:
- identify笔() - 添加包含處理
- detect_笔破壞() - 新增
- identify_线段() - 完善生成規則

price_action.py:
- detect_head_shoulders()
- detect_flag()
- detect_wedge()
```

---

## Phase 9: 交易策略量化 🟡

### P9.1: 待項目

| 優先度 | 項目 | 說明 |
|--------|------|------|
| 🔴 高 | 完整風控模組 | 停損/停利/移動停損 |
| 🔴 高 | 部位計算 | Kelly Criterion |
| 🟡 中 | 風險報酬優化 | 多訊號權重排序 |
| 🟢 低 | 回測框架 | in-sample/out-of-sample |

### P9.2: 需新增函數

```
strategy.py 新增:
- calculate_position_size(capital, risk_pct, entry, stop_loss)
- calculate_kelly_criterion(win_rate, avg_win, avg_loss)
- apply_trailing_stop(entry, current, trail_pct)
- rank_signals(signals[])
- backtest_signals(df, signals)
```

---

## Phase 10: 圖表輸出強化 🟢

### P10.1: 待項目

| 優先度 | 項目 | 說明 |
|--------|------|------|
| 🔴 高 | K 線圖輸出 | SVG/Canvas 繪製 |
| 🟡 中 | 均線疊加 | MA5/10/20/60 |
| 🟡 中 | 技術指標子圖 | 獨立區域繪製指標 |
| 🟢 低 | 互動式 HTML | Plotly 圖表 |

### P10.2: 需新增函數

```
chart_generator.py 新增:
- generate_candlestick_svg(df)
- generate_ma_overlay(df, mas)
- generate_indicator_panel(df, indicator)
- generate_plotly_chart(df)
```

---

## 技術債務 ⚪

| 優先度 | 項目 |
|--------|------|
| 🟡 中 | 缺乏型態標註 (type hints) |
| 🟢 低 | 模組耦合過高 |
| 🟢 低 | 硬編碼參數過多 |

---

## 新增測試覆蓋目標

| 優先度 | 模組 | 新增測試 |
|--------|------|----------|
| 🔴 高 | data_fetcher (網路) | 5 |
| 🟡 中 | indicators (MFI/ADX等) | 15 |
| 🟡 中 | chan_theory (筆破壞) | 10 |
| 🟢 低 | strategy (風控) | 8 |
| 🟢 低 | chart_generator | 5 |

---

## Phase 3: 完整測試覆蓋 🔵

### P3.1: 未涵蓋模組測試

| 狀態 | 模組 | 測試數 | 優先度 |
|------|------|--------|--------|
| ✅ | price_action.py | 22 | P1 |
| ✅ | chan_theory.py | 18 | P1 |
| ✅ | wave_theory.py | 22 | P2 |
| ✅ | strategy.py | 23 | P2 |
| ✅ | analyzer (端到端) | 15 | P1 |

### P3.2: 測試覆蓋缺口

| 模組 | 需測試功能 |
|------|------------|
| price_action.py | 支撐/阻力、缺口、W底/M頭、趨勢線 |
| chan_theory.py | 筆識別、線段識別、中樞計算、走勢類型 |
| wave_theory.py | 峰值偵測、波浪模式、黃金分割 |
| strategy.py | 技術面多空、訊號整合、趨勢判斷 |
| analyzer.py | 完整流程整合 |

### P3.3: 測試結果

```
============================= test session starts ==============================
153 passed in 2.39s
=============================
```

測試檔案:
- test_indicators.py: 30 tests ✓
- test_moving_avg.py: 28 tests ✓
- test_price_action.py: 22 tests ✓ (new)
- test_chan_theory.py: 18 tests ✓ (new)
- test_wave_theory.py: 22 tests ✓ (new)
- test_strategy.py: 23 tests ✓ (new)
- test_analyzer_integration.py: 15 tests ✓ (new, 5 integration 需要網路)