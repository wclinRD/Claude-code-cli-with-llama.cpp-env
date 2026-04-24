# Claude-code-cli-with-llama.cpp-env
Claude code cli with llama.cpp environment configuration



## opencode.json
.config/opencode/opencode.json 
```
{  
  "$schema": "https://opencode.ai/config.json",
  "plugin": [
    "file:///Users/wclin/opencode/StockTime/improved-webtools/src/index.ts",
    "opencode-working-memory",
    "opencode-agent-skills"
  ]                                                                                                                
   
}
```

---

OpenCode 會先讀取 AGENTS.md（以前稱作 agent.md，現在標準名稱是 AGENTS.md）來做為配置標準。

載入優先順序：

本地端 - 從目前目錄向上尋找 (AGENTS.md → CLAUDE.md → CONTEXT.md)
全局 - ~/.config/opencode/AGENTS.md
Claude Code - ~/.claude/CLAUDE.md（除非停用）
每個類別中，第一個找到的檔案會勝出。

例如：若有 AGENTS.md 和 CLAUDE.md，只會用 AGENTS.md。同樣地，~/.config/opencode/AGENTS.md 優先於 ~/.claude/CLAUDE.md。

Sources:

OpenCode Docs - Rules
OpenCode Docs - Config
