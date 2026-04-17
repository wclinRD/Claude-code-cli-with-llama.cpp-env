# Run Qwen 3.5 Locally with Claude Code — Zero API Bills, Full Agentic Coding

Your Mac has a GPU. Your Mac has RAM. Why are you paying someone else to think?

This guide gets you a fully local agentic coding setup: **Claude Code** talking to **Qwen 3.5-35B-A3B** via **llama.cpp**, all running on your Apple Silicon Mac. No API keys. No cloud. No surprise invoices. Just you, your M-series chip, and 35 billion parameters doing your bidding on `localhost`.

Based on [this article](https://medium.com/coding-nexus/how-to-run-qwen3-5-locally-with-claude-code-no-api-bills-full-agentic-coding-3350606f866d).

---

## TL;DR — Just Run the Scripts

```sh
./install.sh   # one-time setup: Homebrew, Node, llama.cpp, Claude Code, settings.json, .zshrc
source ~/.zshrc
./run.sh       # start the model server, then open a new terminal and type: claude
```

Both scripts are idempotent — run them as many times as you want, they won't break anything or duplicate `.zshrc` entries or overwrite existing `settings.json`.

---

## How It Works

```
You  -->  Claude Code  -->  llama-server (localhost:8131)  -->  Qwen 3.5-35B-A3B (GGUF on Metal)
```

Claude Code thinks it's talking to Anthropic's API. It's actually talking to a quantized open-weight model running on your Mac's GPU. Same agentic workflow, same tool use, zero egress. It's beautiful.

---

## Prerequisites

You're self-hosting a 35B parameter model. You'll need some hardware.

| What | Minimum | Ideal |
|---|---|---|
| Mac | Apple Silicon (M1 / M2 / M3 / M4) | Any Pro / Max variant |
| Unified Memory | 24 GB | 64 GB |
| Free Disk | ~25 GB | ~40 GB (room to try other models) |
| macOS | 13.0+ (Ventura) | Latest |
| Node.js | 18+ | 22+ |
| Homebrew | Installed | You're self-hosting LLMs, of course you have Homebrew |
| Patience | First model download is ~20 GB | Go make coffee |

> **16 GB RAM?** You can still play — just use `-c 32768` instead of `-c 131072` in the server command. It works, just with less context. More on that below.

---

## Step 1 — Install llama.cpp

This is the engine. It serves your model as an OpenAI/Anthropic-compatible API over HTTP. Metal GPU acceleration is enabled by default on Apple Silicon — no flags needed.

**Option A — Homebrew (recommended, you already have it):**

```sh
brew install llama.cpp
```

**Option B — Build from source** (for the "I compile my own kernels" crowd):

```sh
brew install cmake ninja git
```

```sh
git clone https://github.com/ggml-org/llama.cpp ~/llama.cpp
```

```sh
cd ~/llama.cpp && cmake -B build -G Ninja -DGGML_METAL=ON && cmake --build build --config Release -j 8
```

If you built from source, add `llama-server` to your PATH:

```sh
echo 'export PATH="$HOME/llama.cpp/build/bin:$PATH"' >> ~/.zshrc && source ~/.zshrc
```

Verify it's working:

```sh
llama-server --version
```

---

## Step 2 — Start the Model Server

This downloads Qwen 3.5-35B-A3B (~20 GB, Q4_K_M quantization) from HuggingFace on first run. Subsequent starts use the cached model.

```sh
llama-server \
  -hf unsloth/Qwen3.5-35B-A3B-GGUF:Q4_K_M \
  --port 8131 \
  -ngl 999 \
  -t 4 \
  -c 131072 \
  -b 512 \
  -ub 1024 \
  --parallel 1 \
  -fa on \
  --jinja \
  --keep 1024 \
  --cache-type-k q8_0 \
  --cache-type-v q8_0 \
  --swa-full \
  --no-context-shift \
  --chat-template-kwargs '{"enable_thinking": false}' \
  --mlock \
  --no-mmap
```

**Leave this terminal open.** First startup takes 10–30 seconds. Go stare at Activity Monitor if you want — watching 20 GB of model weights load into unified memory is oddly satisfying.

### Tune `-t` for your chip

The `-t` flag sets CPU threads for non-GPU work. Match it to your performance cores:

| Your Mac | Set `-t` to |
|---|---|
| M1 / M2 / M3 / M4 (base) | `4` |
| M1 / M2 / M3 / M4 Pro / Max | `8` |
| M2 / M3 Ultra | `16` |

### On 16 GB RAM

Swap the context size flag. Everything else stays the same:

```sh
# use this instead of -c 131072
-c 32768
```

You lose long-context capability but the model still works great for normal coding tasks.

### What all these flags do

| Flag | Why it matters |
|---|---|
| `-ngl 999` | Offload every layer to Metal GPU. This is the single biggest speedup. Without it, your CPU does all the work and your GPU sits there looking pretty. |
| `-t 4` | CPU threads for non-offloaded work. Match to your P-core count (table above). |
| `-b 512` | Prompt batch size. 512 beats 2048 on M2 base in benchmarks. Counterintuitive, but true. |
| `--swa-full` | **The hidden performance flag.** Qwen 3.5 uses sliding window attention. Without this, every follow-up request reprocesses the entire prompt from scratch. With it, prompt caching works. The difference is ~10x on follow-up latency. |
| `--no-context-shift` | Required when using `--swa-full`. Context shifting is incompatible with SWA. |
| `--chat-template-kwargs '{"enable_thinking": false}'` | Disables the model's internal chain-of-thought. In agentic workflows, those thinking tokens are wasted — Claude Code manages its own reasoning. |
| `--cache-type-k/v q8_0` | Quantize the KV cache. Near-zero quality loss, measurable throughput improvement. Free lunch. |
| `--keep 1024` | Pin the system prompt in cache. Claude Code sends a chunky system prompt — no point re-processing it every turn. |
| `--mlock` | Lock the model in RAM. Prevents macOS from deciding your model weights are a great candidate for swap. |
| `--no-mmap` | Don't memory-map the model file. More stable on macOS, especially under memory pressure. |
| `-fa on` | Flash attention. Faster prompt evaluation. |

---

## Step 3 — Verify the Server

Open a **new terminal tab** (the other one is busy serving a 35B model) and poke the API:

```sh
curl http://localhost:8131/v1/models
```

You should see JSON with the model ID. If you get `connection refused`, the model is still loading — give it another 10 seconds.

---

## Step 4 — Install Claude Code

You probably already have this. If not:

**Option A — Native installer (auto-updates):**

```sh
curl -fsSL https://claude.ai/install.sh | bash
```

**Option B — npm:**

```sh
npm install -g @anthropic-ai/claude-code
```

**Option C — Homebrew:**

```sh
brew install --cask claude-code
```

> **Homebrew conflict?** If you see `Error: It seems there is already a Binary at '/opt/homebrew/bin/claude'`, run `rm /opt/homebrew/bin/claude` first, then reinstall.

Verify:

```sh
claude --version
```

---

## Step 5 — Configure `~/.claude/settings.json`

This is the proper way to configure Claude Code. The `env` block sets environment variables for every session (no `.zshrc` needed), `permissions` pre-approves common tools so the model doesn't ask for confirmation on every `ls`, and a few flags disable telemetry and features that don't make sense for local inference.

```sh
mkdir -p ~/.claude
```

```sh
cat << 'SETTINGS' > ~/.claude/settings.json
{
  "$schema": "https://json.schemastore.org/claude-code-settings.json",
  "env": {
    "ANTHROPIC_BASE_URL": "http://127.0.0.1:8131",
    "ANTHROPIC_AUTH_TOKEN": "local",
    "ANTHROPIC_MODEL": "unsloth/qwen3.5-35b-a3b",
    "ANTHROPIC_DEFAULT_OPUS_MODEL": "unsloth/qwen3.5-35b-a3b",
    "ANTHROPIC_DEFAULT_SONNET_MODEL": "unsloth/qwen3.5-35b-a3b",
    "ANTHROPIC_DEFAULT_HAIKU_MODEL": "unsloth/qwen3.5-35b-a3b",
    "CLAUDE_CODE_SUBAGENT_MODEL": "unsloth/qwen3.5-35b-a3b",
    "CLAUDE_CODE_MAX_OUTPUT_TOKENS": "128000",
    "DISABLE_PROMPT_CACHING": "1",
    "DISABLE_AUTOUPDATER": "1",
    "DISABLE_TELEMETRY": "1",
    "DISABLE_ERROR_REPORTING": "1",
    "DISABLE_NON_ESSENTIAL_MODEL_CALLS": "1"
  },
  "permissions": {
    "allow": [
      "Bash(git *)", "Bash(npm *)", "Bash(npx *)", "Bash(node *)",
      "Bash(python *)", "Bash(python3 *)", "Bash(pip *)", "Bash(pip3 *)",
      "Bash(brew *)", "Bash(ls *)", "Bash(cat *)", "Bash(head *)",
      "Bash(tail *)", "Bash(find *)", "Bash(grep *)", "Bash(rg *)",
      "Bash(mkdir *)", "Bash(cp *)", "Bash(mv *)", "Bash(rm *)",
      "Bash(echo *)", "Bash(curl *)", "Bash(which *)", "Bash(env *)",
      "Bash(cd *)", "Bash(pwd)", "Bash(wc *)", "Bash(sort *)",
      "Bash(uniq *)", "Bash(diff *)", "Bash(chmod *)", "Bash(touch *)",
      "Bash(sed *)", "Bash(awk *)", "Bash(xargs *)", "Bash(tee *)",
      "Read", "Edit", "Write", "Glob", "Grep",
      "WebFetch", "WebSearch"
    ],
    "deny": [
      "Read(./.env)", "Read(./.env.*)", "Read(./secrets/**)"
    ]
  }
}
SETTINGS
```

### What these settings do

| Setting | Why |
|---|---|
| `env.ANTHROPIC_BASE_URL` | Points Claude Code at your local llama-server instead of Anthropic's cloud. |
| `env.ANTHROPIC_AUTH_TOKEN` | Any non-empty string. Satisfies the auth check without a real API key. |
| `env.*_MODEL` | Maps every model tier (Opus, Sonnet, Haiku, subagents) to your local Qwen 3.5. |
| `env.CLAUDE_CODE_MAX_OUTPUT_TOKENS` | Allows longer responses. Default is 32K — local models have no billing, so crank it. |
| `env.DISABLE_PROMPT_CACHING` | Prompt caching is an Anthropic API feature. Your local server handles its own caching via `--swa-full`. |
| `env.DISABLE_AUTOUPDATER` | You're running local. Auto-updates would just add network calls you don't need. |
| `env.DISABLE_TELEMETRY` | Running local to keep things private? Then don't phone home. |
| `env.DISABLE_ERROR_REPORTING` | Same reasoning. Your errors, your business. |
| `env.DISABLE_NON_ESSENTIAL_MODEL_CALLS` | Stops Claude Code from making extra model calls for things like spinner text. Every token counts on local inference. |
| `permissions.allow` | Pre-approves common shell commands and all file tools. Without this, Claude Code asks for permission on every single tool call. Gets old fast. |
| `permissions.deny` | Keeps `.env` and secrets off-limits, because even local models shouldn't read your credentials. |

> **Already have a `settings.json`?** The `install.sh` script detects existing content and backs it up before writing. Or just merge the `env` and `permissions` blocks into your existing file manually.

---

## Step 6 — Shell configuration (backup + `cclocal` helper)

The `settings.json` above handles everything Claude Code needs. But having the env vars in `.zshrc` too gives you a fallback and lets the `cclocal` helper function work:

```sh
cat << 'EOF' >> ~/.zshrc

# Claude Code + Local Qwen 3.5 — because localhost > cloud
export LM_MODEL="unsloth/qwen3.5-35b-a3b"
export ANTHROPIC_BASE_URL="http://127.0.0.1:8131"
export ANTHROPIC_AUTH_TOKEN="local"
export CLAUDE_CODE_MAX_OUTPUT_TOKENS=128000
export ANTHROPIC_MODEL="$LM_MODEL"
export ANTHROPIC_DEFAULT_OPUS_MODEL="$LM_MODEL"
export ANTHROPIC_DEFAULT_SONNET_MODEL="$LM_MODEL"
export ANTHROPIC_DEFAULT_HAIKU_MODEL="$LM_MODEL"
export CLAUDE_CODE_SUBAGENT_MODEL="$LM_MODEL"
EOF
```

```sh
source ~/.zshrc
```

---

## Step 7 — Launch Claude Code

```sh
claude
```

Or, if you prefer a no-config one-liner (works even without `settings.json` or `.zshrc` changes):

```sh
ANTHROPIC_BASE_URL=http://127.0.0.1:8131 ANTHROPIC_AUTH_TOKEN=local claude
```

You should see `unsloth/qwen3.5-35b-a3b` as the active model. Type something. Watch your llama-server terminal light up with inference logs. Smile.

---

## Daily Driver: Quick Start Script

Once everything is installed, this is your daily workflow. One command, two services:

```sh
llama-server \
  -hf unsloth/Qwen3.5-35B-A3B-GGUF:Q4_K_M \
  --port 8131 \
  -ngl 999 \
  -t 4 \
  -c 131072 \
  -b 512 \
  -ub 1024 \
  --parallel 1 \
  -fa on \
  --jinja \
  --keep 1024 \
  --cache-type-k q8_0 \
  --cache-type-v q8_0 \
  --swa-full \
  --no-context-shift \
  --chat-template-kwargs '{"enable_thinking": false}' \
  --mlock \
  --no-mmap &

sleep 15 && ANTHROPIC_BASE_URL=http://127.0.0.1:8131 ANTHROPIC_AUTH_TOKEN=local claude
```

---

## Shell Helper: `cclocal`

For the refined developer who wants a clean command:

```sh
cat << 'FUNC' >> ~/.zshrc

cclocal() {
    local port=8131
    if [[ "$1" =~ ^[0-9]+$ ]]; then
        port="$1"
        shift
    fi
    ANTHROPIC_BASE_URL="http://127.0.0.1:${port}" \
    ANTHROPIC_AUTH_TOKEN="local" \
    claude "$@"
}
FUNC
```

```sh
source ~/.zshrc
```

Now you can:

```sh
cclocal              # Qwen 3.5 on port 8131
cclocal 8127         # Qwen3-Coder on port 8127
cclocal 8129         # GLM-4.7-Flash on port 8129
```

---

## Other Models Worth Trying

Already running Qwen 3.5 and want more? You can run multiple models on different ports and switch with `cclocal <port>`.

| Model | Port | Size | Good For | Command |
|---|---|---|---|---|
| **Qwen3-Coder-30B-A3B** | 8127 | ~30 GB | Pure coding. If you only write code, this might be better than Qwen 3.5. | `llama-server --fim-qwen-30b-default --port 8127` |
| **GLM-4.7-Flash** | 8129 | ~18 GB | Lighter weight, still capable. Good if you're on 24 GB. | `llama-server -hf unsloth/GLM-4.7-Flash-GGUF:UD-Q4_K_XL --port 8129 -c 131072 -b 2048 -ub 1024 --parallel 1 -fa on --jinja --chat-template-file ~/llama.cpp/models/templates/glm-4.jinja` |
| **GPT-OSS-20B** | 8123 | ~20 GB | Fast baseline. 17–38 tok/s on M1 Max. | `llama-server --gpt-oss-20b-default --port 8123` |
| **Qwen3-Coder-Next-80B-A3B** | 8130 | ~46 GB | SOTA coder. Needs 64 GB RAM. Worth it if you have the metal. | `llama-server -hf unsloth/Qwen3-Coder-Next-GGUF:UD-Q4_K_XL --port 8130 -c 131072 -b 2048 -ub 1024 --parallel 1 -fa on --jinja` |

---

## Troubleshooting

Things that might go wrong and how to fix them without rage-quitting.

| Symptom | Likely Cause | Fix |
|---|---|---|
| `connection refused` on curl | Server still loading | Wait 30s, retry. First load is slow. |
| Painfully slow responses | Missing `--swa-full` or `-ngl 999` | Restart llama-server with both flags. This is the #1 gotcha. |
| Claude Code uses the cloud model | Env vars not set | Re-export them in the terminal you're using. Check with `echo $ANTHROPIC_BASE_URL`. |
| `failed to find a memory slot` | Context too large for available RAM | Use `--parallel 1` and/or reduce `-c` to `32768`. |
| Auth errors from Claude Code | Missing auth token | `export ANTHROPIC_AUTH_TOKEN=local` — any non-empty string works. |
| Wrong model responding | Model ID mismatch | Run `curl localhost:8131/v1/models` and compare with `echo $LM_MODEL`. |
| First request takes forever | Cold start, model loading into memory | Normal. 10–30 seconds. Subsequent requests are fast. |
| System swapping / beachball | Model doesn't fit in RAM | Reduce `-c`, or try a smaller model like GLM-4.7-Flash (~18 GB). |
| Homebrew binary conflict | Previous install left `/opt/homebrew/bin/claude` | `rm /opt/homebrew/bin/claude && brew reinstall --cask claude-code` |

---

## Stopping

```sh
pkill llama-server
```

Or `Ctrl+C` in the llama-server terminal. Your model weights aren't going anywhere — next launch picks up the cached GGUF instantly.

---

## Credits

- [Tattva Tarang's original article](https://medium.com/coding-nexus/how-to-run-qwen3-5-locally-with-claude-code-no-api-bills-full-agentic-coding-3350606f866d) for the core setup
- [Konstantinos' LM Studio walkthrough](https://konstantinos.top/blog/36/) for environment variable details
- [claude-code-tools docs](https://pchalasani.github.io/claude-code-tools/integrations/local-llms/) for the flag reference and model catalog
- [llama.cpp](https://github.com/ggml-org/llama.cpp) for making all of this possible on consumer hardware
- Your Mac, for being a surprisingly good inference box
