---
name: web-tools-guide
description: 網頁抓取工具使用指南，教導 Playwright 與 WebScraper 的正確使用方式
license: MIT
compatibility: opencode
---

# Web 工具使用指南

本技能教導如何正確使用 **Playwright** 和 **WebScraper Toolkit** 進行網頁抓取，當普通 fetch 不順利時，建議改用這兩個工具。

## 適用情境

當遇到以下情況時，請使用此技能：
- `fetch()` 無法抓取反爬頁面
- 遇到 Cloudflare 驗證
- 網頁有 JavaScript 渲染
- 需要動態內容抓取
- API 文檔需要瀏覽器渲染

---

## 一、Playwright - 瀏覽器自動化

### 特性
- 完全模擬真實瀏覽器
- 可執行 JavaScript
- 支援無頭模式
- 可執行複雜的 UI 操作

### 安裝

```bash
# 方法 1：使用 npx
npm install -g @playwright/test
playwright install chromium

# 方法 2：使用 pip
python3 -m venv /tmp/venv
source /tmp/venv/bin/activate
pip install playwright
playwright install chromium
```

### 基本用法

#### 1. 同步模式（簡單使用）

```python
from playwright.sync_api import sync_playwright

with sync_playwright() as p:
    browser = p.chromium.launch(headless=True)  # 無頭模式
    page = browser.new_page()
    
    page.goto('https://example.com', wait_until='networkidle')
    
    # 執行 JavaScript
    result = page.evaluate('document.title')
    print(result)
    
    # 獲取內容
    html = page.content()
    
    browser.close()
```

#### 2. 獲取表格數據

```python
from playwright.sync_api import sync_playwright
import json

with sync_playwright() as p:
    browser = p.chromium.launch(headless=True)
    page = browser.new_page()
    
    page.goto('https://example.com/table-data', wait_until='networkidle')
    
    # 獲取表格
    table = page.locator('table').all()
    for row in table:
        cells = []
        for cell in row:
            cells.append(cell.inner_text().strip())
        print(cells)
    
    browser.close()
```

#### 3. 填寫表單並提交

```python
from playwright.sync_api import sync_playwright

with sync_playwright() as p:
    browser = p.chromium.launch(headless=True)
    page = browser.new_page()
    
    page.goto('https://example.com/form')
    
    # 填寫表單
    page.fill('input[name="username"]', 'john')
    page.fill('input[name="email"]', 'john@example.com')
    
    # 點擊提交
    page.click('button[type="submit"]')
    
    # 獲取結果
    result = page.locator('div#result').inner_text()
    print(result)
    
    browser.close()
```

#### 4. 處理反爬

```python
from playwright.sync_api import sync_playwright

with sync_playwright() as p:
    browser = p.chromium.launch(headless=True)
    page = browser.new_page()
    
    # 啟用 stealth
    from playwright._impl._page import Page
    page._page_instance.__class__.extra_headers = {
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7)'
    }
    
    page.goto('https://example.com', wait_until='networkidle')
    
    # 執行 JavaScript
    content = page.evaluate("document.body.innerText")
    print(content)
    
    browser.close()
```

---

## 二、WebScraper Toolkit - 批量網頁抓取

### 特性
- 支援多 worker 並發
- 自動處理反爬
- 輸出多種格式
- 適合批量抓取

### 安裝

```bash
# 1. 使用 venv 安裝
python3 -m venv /tmp/venv
source /tmp/venv/bin/activate

# 2. 安裝 toolkit
pip install web-scraper-toolkit

# 3. 安裝瀏覽器
pipx run web-scraper-toolkit playwright install chromium
```

### 基本用法

#### 1. 單頁抓取

```bash
# Markdown 格式（預設）
/tmp/venv/bin/web-scraper --url https://example.com --format markdown

# JSON 格式
/tmp/venv/bin/web-scraper --url https://example.com --format json

# HTML 格式
/tmp/venv/bin/web-scraper --url https://example.com --format html

# 輸出到檔案
/tmp/venv/bin/web-scraper --url https://example.com --format json --export
/tmp/venv/bin/web-scraper --url https://example.com --format json --merge
```

#### 2. 批量抓取

```bash
# 從 URL 列表抓取
/tmp/venv/bin/web-scraper --input urls.txt --format markdown --workers 5 --export

# 指定輸出目錄
/tmp/venv/bin/web-scraper --input urls.txt --format json --workers 3 --output-dir ./output
```

#### 3. 自動 contacts 提取

```bash
/tmp/venv/bin/web-scraper --url https://example.com --contacts
```

---

## 三、工具選擇指南

| 情境 | 推薦工具 | 理由 |
|------|---------|------|
| 需要執行 JavaScript | Playwright | 完整瀏覽器模擬 |
| 單頁抓取 | Playwright 或 WebScraper | 兩者皆可 |
| 多頁批量抓取 | WebScraper | 支援並發 worker |
| 填寫表單/點擊按鈕 | Playwright | 支援 UI 操作 |
| 反爬嚴重 | WebScraper | 自動繞過 |
| 需要 Screenshot | Playwright | 支援截圖 |
| 需要 PDF 輸出 | Playwright | 支援 PDF 渲染 |

---

## 四、失敗重試策略

當 `fetch()` 失敗時，按順序嘗試：

1. **使用 Playwright**
   ```python
   # 基本嘗試
   from playwright.sync_api import sync_playwright
   
   with sync_playwright() as p:
       browser = p.chromium.launch(headless=True)
       page = browser.new_page()
       page.goto('https://example.com', wait_until='networkidle')
       content = page.evaluate("document.body.innerText")
   ```

2. **使用 WebScraper**
   ```bash
   /tmp/venv/bin/web-scraper --url https://example.com --format json --headless
   ```

3. **調整參數**
   - Playwright: 增加 `wait_until`, 調整 `timeout`
   - WebScraper: 減少 `--workers`, 增加 `--delay`

---

## 五、常見問題解決

### Playwright 問題

| 問題 | 解決方案 |
|------|---------|
| `ModuleNotFoundError` | 確保使用 `from playwright.sync_api import sync_playwright` |
| `Playwright not found` | 重新執行 `playwright install chromium` |
| 無頭模式卡住 | 增加 `wait_until` 或減少 `timeout` |
| 反爬封鎖 | 使用 stealth 模式或代理 |

### WebScraper 問題

| 問題 | 解決方案 |
|------|---------|
| `command not found` | 使用 `/tmp/venv/bin/web-scraper` |
| 無法抓取 | 嘗試 `--headless` 模式 |
| 被封禁 | 減少 `--workers`，增加 `--delay` |
| 輸出為空 | 檢查 URL 是否正確 |

---

## 六、完整範例

### 範例 1：抓取 API 文檔

```python
from playwright.sync_api import sync_playwright
import json

with sync_playwright() as p:
    browser = p.chromium.launch(headless=True)
    page = browser.new_page()
    
    # 抓取 TWSE API 文檔
    page.goto('https://openapi.twse.com.tw', wait_until='networkidle')
    
    # 找到 JSON schema
    json_text = page.evaluate("""
        document.querySelector('pre').textContent
    """)
    
    api_info = json.loads(json_text)
    print(api_info['info']['title'])
    
    browser.close()
```

### 範例 2：抓取網站內容

```python
from playwright.sync_api import sync_playwright
import json

with sync_playwright() as p:
    browser = p.chromium.launch(headless=True)
    page = browser.new_page()
    
    # 抓取網站
    page.goto('https://example.com', wait_until='networkidle')
    
    # 獲取內容
    content = page.evaluate("""
        () => {
            const pre = document.querySelector('pre');
            return JSON.parse(pre.textContent);
        }
    """)
    
    print(json.dumps(content, indent=2, ensure_ascii=False))
    
    browser.close()
```

---

## 七、最佳實踐

1. **使用 venv 隔離環境**
   ```bash
   python3 -m venv /tmp/venv
   source /tmp/venv/bin/activate
   ```

2. **使用 headless 模式**
   - Playwright: `headless=True`
   - WebScraper: `--headless`

3. **處理異常**
   ```python
   try:
       with sync_playwright() as p:
           browser = p.chromium.launch(headless=True)
           page = browser.new_page()
           page.goto(url, wait_until='networkidle')
           result = page.evaluate("document.body.innerText")
   except Exception as e:
       print(f"Failed: {e}")
   ```

4. **增加等待時間**
   ```python
   page.goto(url, wait_until='networkidle', timeout=30000)
   ```

5. **使用無頭模式**
   ```bash
   /tmp/venv/bin/web-scraper --url https://example.com --headless
   ```

---

## 八、快速引用

### Playwright 快速啟動

```python
from playwright.sync_api import sync_playwright

with sync_playwright() as p:
    browser = p.chromium.launch(headless=True)
    page = browser.new_page()
    page.goto('https://example.com', wait_until='networkidle')
    print(page.content())
    browser.close()
```

### WebScraper 快速啟動

```bash
/tmp/venv/bin/web-scraper --url https://example.com --format json --headless --export
```

---

## 總結

當 `fetch()` 不順利時：
1. 先嘗試 **Playwright**（適合單頁、需要 JS 執行）
2. 再嘗試 **WebScraper**（適合批量、反爬嚴重）
3. 根據情境選擇合適工具

這兩個工具都能正確處理瀏覽器自動化任務，是 fetch() 的可靠替代方案。
