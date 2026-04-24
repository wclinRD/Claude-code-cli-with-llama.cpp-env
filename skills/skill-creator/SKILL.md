---
name: skill-creator
description: 引導使用者建立新的 OpenCode Skill，確保遵循正確的命名規範、目錄結構和 YAML frontmatter 格式
compatibility: opencode
---

# Skill Creator

當使用者請求建立新的 OpenCode Skill 時，請遵循以下規範：

## 1. 存放位置

### Global Skill (全域)
Skill 會從以下位置被發現，在 TUI 中使用 `/<skill-name>` 呼叫：
- `~/.config/opencode/skills/<skill-name>/SKILL.md`
- `~/.claude/skills/<skill-name>/SKILL.md`
- `~/.agents/skills/<skill-name>/SKILL.md`

### Project Skill (專案)
- `<project>/.opencode/skills/<skill-name>/SKILL.md`
- `<project>/.claude/skills/<skill-name>/SKILL.md`

### TUI 使用方式
在 TUI 中輸入 `/<skill-name>` 即可啟動對應的 Skill，例如：`/skill-creator`

## 2. 目錄結構

每個 Skill 需要一個独立的資料夾，資料夾名稱必須與 skill 名稱完全一致：

```
skills/
└── my-new-skill/
    └── SKILL.md
```

## 3. SKILL.md 格式

### YAML Frontmatter (必要)

```yaml
---
name: <skill-name>
description: <功能描述，1-1024 字元>
license: <可選>
compatibility: opencode
metadata:
  <可選的鍵值對>
---
```

### 內容區塊

在 frontmatter 之後，可以加入詳細的 Skill 說明和使用指南。

## 4. 命名規範

- **名稱長度**: 1-64 字元
- **字元限制**: 僅使用小寫字母、數字、單一連字符號 (-)
- **禁止**:
  - 以連字符號開頭或結尾
  - 連續的連字符號 (--)
  - 名稱與資料夾名稱不一致

## 5. 必要欄位

| 欄位 | 必要 | 說明 |
|------|------|------|
| name | 是 | 必須與資料夾名稱完全相同 |
| description | 是 | 1-1024 字元，用于 agent 選擇 |

## 6. 驗證清單

建立新 Skill 前，請確認：
- [ ] SKILL.md 檔案名稱為全大寫
- [ ] frontmatter 包含 name 和 description
- [ ] 名稱符合命名規範
- [ ] 存放於正確的目錄位置

## 7. 詢問使用者

建立新 Skill 前，請先詢問使用者：
1. 這個 Skill 是要給 **全域使用** 還是 **僅限此專案**？
2. Skill 的名稱是什麼？
3. 這個 Skill 的功能描述為何？