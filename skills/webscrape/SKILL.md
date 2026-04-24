---
name: webscrape
description: 批量網頁抓取工具，使用 WebScraperToolkit CLI 支援單頁/批量抓取、CSS selector 提取、抗 bot 繞過
license: MIT
compatibility: opencode
---

# WebScrape Skill

使用 WebScraperToolkit CLI 進行網頁抓取。

## 安裝說明

### 前置需求

1. **安裝 WebScraperToolkit**
   ```bash
   pipx install web-scraper-toolkit
   ```

2. **安裝 Playwright 瀏覽器**
   ```bash
   pipx run web-scraper-toolkit playwright install chromium
   ```
   或
   ```bash
   ~/.local/pipx/venvs/web-scraper-toolkit/bin/playwright install chromium
   ```

3. **驗證安裝**
   ```bash
   web-scraper --help
   ```

### 常見問題

- 若 `web-scraper` 命令找不到，嘗試：
  ```bash
  ~/.local/bin/web-scraper --help
  ```
- 若權限不足，使用 pipx 安裝

---

## 觸發條件

當用戶輸入包含以下關鍵字時觸發：
- 「抓取」
- 「爬蟲」
- 「scrape」
- 「scraping」
- URL + 「抓取」/「爬取」
- 「批量」抓取

---

## 使用方式

### 單頁抓取

```bash
web-scraper --url <url> --format markdown --export
```

**範例：**
```bash
web-scraper --url https://example.com --format markdown --export
```

### 批量抓取

使用 `--input` 指定檔案路徑（一行一個 URL）：

```bash
web-scraper --input urls.txt --format markdown --workers 5 --export
```

### 指定輸出格式

- `--format markdown` - Markdown 格式（預設）
- `--format text` - 純文字
- `--format html` - HTML
- `--format json` - JSON
- `--format csv` - CSV

### 完整參數

| 參數 | 簡寫 | 說明 |
|------|------|------|
| `--url` | `-u` | 目標 URL |
| `--input` | `-i` | URL 列表檔案 |
| `--format` | `-f` | 輸出格式：markdown/text/html/json/xml/csv |
| `--export` | `-e` | 匯出到檔案 |
| `--workers` | `-w` | 並發數量（預設：auto） |
| `--delay` | - | 請求間隔（秒） |
| `--output-dir` | - | 輸出目錄 |
| `--headless` | - | 無頭模式執行 |
| `--merge` | - | 合併輸出 |

---

## 實作流程

### Step 1: 解析用戶輸入

從用戶訊息中提取：
1. **URL** - 使用正規表達式匹配 http/https 開頭的 URL
2. **格式** - 從訊息中識別所需格式（預設：markdown）
3. **額外參數** - 如有指定

### Step 2: 執行抓取

使用 Bash 工具執行 CLI 命令：

```bash
# 單頁抓取
cd /tmp && web-scraper --url <url> --format <format> --export

# 批量抓取
cd /tmp && web-scraper --input <file> --format <format> --workers <n> --export --merge
```

### Step 3: 讀取結果

抓取完成後，讀取輸出檔案：
- 檔案位置：`/tmp/{domain}_{hash}.{format}`
- 使用 Read 工具讀取內容

### Step 4: 返回結果

將抓取結果以 Markdown 格式返回給用戶。

---

## 輸出範例

抓取 `https://example.com` 的輸出：

```
=== SCRAPED FROM: https://example.com/ (MARKDOWN) ===

# Example Domain

This domain is for use in documentation examples without needing permission.

[Learn more](https://iana.org/domains/example)

(End of file - total 7 lines)
```

---

## 注意事項

1. 輸出檔案預設存在 `/tmp/` 目錄
2. 批量抓取建議設定 `--workers` 避免被封禁
3. 遇到 Cloudflare 等 anti-bot 頁面時，工具會自動嘗試繞過
4. 檔案名稱格式：`{domain}_{hash}.{format}`
5. 使用 `--headless` 可在無頭模式執行避免彈出瀏覽器

---

## 錯誤處理

| 錯誤 | 解決方案 |
|------|----------|
| `command not found: web-scraper` | 使用完整路徑 `~/.local/bin/web-scraper` 或重新安裝 |
| 無法抓取 | 檢查 URL 是否正確，嘗試��� `--headless` |
| 被封禁 | 減少 `--workers`，增加 `--delay` |