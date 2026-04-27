---
name: obscura
description: High-performance headless browser for AI agents and web scraping with built-in anti-detection and parallel concurrency
license: MIT
compatibility: opencode
metadata:
  author: opencode-agent
  version: 2.0
  last-tested: 2026-04-27
---

## 🌐 Obscura 技能

高性能無頭瀏覽器，具備反檢測機制、並發抓取能力和 AI 自動化功能，適合大規模資料爬取和網頁測試。

### 功能特點

- 🚀 **高並發抓取**：支援多作業並行處理，適合大規模資料蒐集
- 🛡️ **反檢測機制**：內建 Cloudflare 繞過和反 bot 技術
- 🎯 **AI 自動化**：可執行複雜的網頁互動和測試流程
- 📊 **PDF 下載支援**：自動識別並下載 PDF 文件，整合 pdf 技能進行處理
- 📸 **截圖功能**：自動抓取網頁快照和圖片
- 🌍 **多瀏覽器模式**：支援 Chrome、Firefox 等不同瀏覽器頭無模式

### PDF 下載與處理工作流

Obscura 具備完整的 PDF 下載功能，可自動識別 PDF 檔案並進行下載，同時可與 pdf 技能整合處理 PDF 內容。

#### 單頁 PDF 下載

```bash
# 下載 PDF 檔案
obscura "https://example.com/document.pdf" --download-pdf

# 同時執行 PDF 內容提取
obscura "https://example.com/document.pdf" --download-pdf --extract-text
```

#### 批量下載 PDF

```bash
# 下載多個 PDF 檔案
obscura "url1.pdf url2.pdf url3.pdf" --batch --download-pdf

# 從文件讀取 URL 列表
cat urls.txt | obscura --batch --download-pdf

# 指定並發數量
obscura "url1.pdf url2.pdf url3.pdf" --concurrency 10 --batch --download-pdf
```

#### 整合 PDF 技能處理下載內容

```bash
# 下載 PDF 並立即處理內容
obscura "https://example.com/document.pdf" \
  --download-pdf \
  --action "python3 process_pdf.py"

# 使用 bash 管道處理
obscura "https://example.com/document.pdf" \
  --download-pdf \
  --output "output.pdf" \
  --then "pdftotext output.pdf text.txt"
```

#### 網頁互動與 PDF 下載

```bash
# 點擊按鈕後下載 PDF
obscura "https://example.com/generate-pdf" \
  --action 'click("download-btn"); sleep(1); download_pdf()' \
  --download-pdf

# 填寫表單後下載 PDF
obscura "https://example.com/form-pdf" \
  --action 'fill("email", "user@example.com"); fill("file", "/path/to/file.pdf"); click("submit-btn")' \
  --download-pdf
```

#### 多瀏覽器並行下載 PDF

```bash
# 同時用不同瀏覽器下載多個 PDF
obscura "url1.pdf url2.pdf url3.pdf" \
  --batch --download-pdf \
  --browsers chrome,firefox \
  --concurrency 5
```

### 使用方式

#### 基本抓取

```bash
# 簡單抓取網頁內容
obscura "https://example.com"

# 抓取特定元素
obscura "https://example.com" --selector ".product-list"

# 抓取所有連結
obscura "https://example.com" --selector "a"
```

#### 批量抓取

```bash
# 從文件讀取 URL 列表
obscura --batch < urls.txt

# 指定並發數量
obscura --batch --concurrency 20 < urls.txt

# 同時抓取並保存截圖
obscura --batch < urls.txt --snapshot
```

#### 網頁測試

```bash
# 執行 JavaScript 測試
obscura "https://example.com" --action "console.log('test')"

# 自動填充表單
obscura "https://example.com/login" \
  --action 'fill("username", "admin"); fill("password", "123456"); click("login-btn")'

# 模擬用戶行為
obscura "https://example.com" --simulate-user "testuser"
```

#### 反檢測模式

```bash
# 啟用 Cloudflare 繞過
obscura "https://cloudflare-protected.com" --anti-detection

# 完整反檢測配置
obscura "https://example.com" \
  --anti-detection \
  --user-agent "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36" \
  --viewport 1920x1080
```

#### 截圖與快照

```bash
# 抓取網頁截圖
obscura "https://example.com" --screenshot "screenshot.png"

# 抓取多頁面快照
obscura "https://example.com" --pages 1-5 --snapshot "snapshots"

# 以特定寬度截取
obscura "https://example.com" --width 1920 --height 1080 --screenshot
```

### 進階選項

```bash
# 指定瀏覽器
obscura "https://example.com" --browser chrome

# 指定無頭模式
obscura "https://example.com" --headless

# 啟用開發者工具
obscura "https://example.com" --devtools

# 指定時區和語言
obscura "https://example.com" --locale "zh-TW" --timezone "Asia/Taipei"
```

### 技術參數

| 參數 | 預設值 | 說明 |
|------|--------|------|
| 並發數量 | 5 | 同時執行的作業數量 |
| 最大重試 | 3 | 失敗後的重試次數 |
| 請求超時 | 30s | 單個請求的最長等待時間 |
| 瀏覽器數量 | 1 | 使用的瀏覽器數量 |
| 反檢測模式 | false | 啟用反檢測功能 |

### PDF 整合說明

Obscura 與 pdf 技能的整合方式：

1. **Obscura 下載 PDF**：使用 `--download-pdf` 選項下載 PDF 文件
2. **自動識別類型**：Obscura 自動識別 PDF 並使用適當的瀏覽器渲染模式
3. **管道處理**：可透過 `--then` 參數直接連結 pdf 命令
4. **腳本自動化**：使用 `--action` 參數執行 Python 腳本進行 complex 處理

#### 完整工作流示例

```bash
# 下載、提取、轉換為 Excel
obscura "https://example.com/data.pdf" \
  --download-pdf \
  --then "pdftext data.pdf && python3 extract_tables.py data.pdf"

# 下載、轉換為文字、匯總
obscura "https://example.com/reports/*.pdf" \
  --batch --download-pdf \
  --then "for f in *.pdf; do pdftext \"$f\" \"${f%.pdf}.txt\"; done"
```

### 範例

```bash
# 下載 ONFI 規格 PDF
obscura "https://onfi.org/files/ONFI_5_2_Rev1.0.pdf" --download-pdf

# 批量下載技術文檔並處理
obscura "https://onfi.org/files/*.pdf" \
  --batch --download-pdf \
  --concurrency 10

# 網頁測試與截圖
obscura "https://example.com" --screenshot "test.png"

# 反檢測模式抓取
obscura "https://example.com" --anti-detection --batch < urls.txt
```

### 注意事項

1. 並發數量過高可能導致 IP 被封鎖
2. 大檔案建議減少並發數量
3. 請遵守目標網站的使用條款
4. PDF 下載後可自動使用 pdf 技能進行處理
5. 反檢測功能可能需要額外的瀏覽器配置
6. 某些網站可能限制並發下載次數

(End of file - total 174 lines)
