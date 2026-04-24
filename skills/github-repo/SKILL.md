---
name: github-repo
description: 當發現 GitHub 網址時，自動將 URL 改為 .git 格式並克隆到 tmp 區，提供後續研究使用
license: MIT
compatibility: opencode
trigger:
  pattern: "https://github.com"
metadata:
  tool: python
  dependency: git
---

# GitHub 代碼克隆技能

這個技能會自動檢測並下載 GitHub 代碼到 tmp 區。

## 功能特點

- 自動檢測 URL 是否以 `github.com` 開頭
- 自動將 GitHub URL 轉換為 `.git` 格式
- 使用 `git clone` 下載代碼到 tmp 目錄
- 自動執行克隆，無需手動輸入
- 適合快速研究 GitHub 項目

## 自動檢測與執行

技能會自動檢測以下情況並執行克隆：

1. **URL 開頭檢測**：當輸入的 URL 以 `https://github.com/` 或 `http://github.com/` 開頭時
2. **自動執行**：無需手動輸入 `/github-repo` 命令
3. **自動轉換**：自動將 URL 轉換為 `.git` 格式
4. **自動下載**：克隆到 `/tmp/<repository-name>` 目錄

## 範例 - 基本模式

**自動克隆並保留**（預設）：

輸入：`https://github.com/jshsakura/awesome-opencode-skills`

自動執行並克隆：
- 轉換為：`https://github.com/jshsakura/awesome-opencode-skills.git`
- 下載到：`/tmp/awesome-opencode-skills`
- 研究完後**保留**在 tmp 目錄中

## 範例 - 自動清理模式

**自動克隆並研究完後自動清理**：

輸入：`https://github.com/jshsakura/awesome-opencode-skills?cleanup=true`

自動執行並克隆：
- 轉換為：`https://github.com/jshsakura/awesome-opencode-skills.git`
- 下載到：`/tmp/awesome-opencode-skills`
- 研究完後**自動刪除**tmp 目錄

## 注意事項

- 技能會自動檢測輸入是否為 GitHub URL
- 自動執行克隆，無需手動輸入命令
- 研究完後可選擇是否自動清理 tmp 目錄（使用 `?cleanup=true` 參數）
- 克隆失敗時會顯示錯誤信息
