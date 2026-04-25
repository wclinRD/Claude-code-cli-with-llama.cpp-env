# Stock-Analysis Skill 修改計劃

## 執行狀態: ✅ 完成

---

## Phase 0: 緊急修復 (Critical Bug Fixes) 🔴

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
| `todo.md` | 新建 |

---

## 未來強化 (暂不執行) ⚪

- API 重試機制
- 快取機制
- 輸入驗證裝飾器
- 更多技術指標
- data_fetcher.py 穩健性強化

---

## 修改日誌

### 2026-04-25
- [x] P0.1 indicators.py 除零修復 → 測試通過
- [x] P0.2 price_action.py 邏輯修復 → 已修正
- [x] P1.1 葛蘭威爾法則 4,5 → 已補全
- [x] P1.2 均線彈性化 → 已實作
- [x] P2 測試框架 → 58 tests passed

---

## Phase 3: 完整測試覆蓋 🔵

### P3.1: 未涵蓋模組測試

| 狀態 | 模組 | 測試數 | 優先度 |
|------|------|--------|--------|
| ⏳ | price_action.py | 13 | P1 |
| ⏳ | chan_theory.py | 8 | P1 |
| ⏳ | wave_theory.py | 10 | P2 |
| ⏳ | strategy.py | 12 | P2 |
| ⏳ | analyzer (端到端) | 15 | P1 |

### P3.2: 測試覆蓋缺口

| 模組 | 需測試功能 |
|------|------------|
| price_action.py | 支撐/阻力、缺口、W底/M頭、趨勢線 |
| chan_theory.py | 筆識別、線段識別、中樞計算、走勢類型 |
| wave_theory.py | 峰值偵測、波浪模式、黃金分割 |
| strategy.py | 技術面多空、訊號整合、趨勢判斷 |
| analyzer.py | 完整流程整合 |

### P3.3: 預期測試結果

```
Phase 3 完成後預期:
- test_indicators.py: 30 tests ✓
- test_moving_avg.py: 28 tests ✓
- test_price_action.py: 13 tests (new)
- test_chan_theory.py: 8 tests (new)
- test_wave_theory.py: 10 tests (new)
- test_strategy.py: 12 tests (new)
- test_analyzer_integration.py: 15 tests (new)

Total: 116 tests
```