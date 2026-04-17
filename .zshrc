# Enable Powerlevel10k instant prompt. Should stay close to the top of ~/.zshrc.
# Initialization code that may require console input (password prompts, [y/n]
# confirmations, etc.) must go above this block; everything else may go below.
if [[ -r "${XDG_CACHE_HOME:-$HOME/.cache}/p10k-instant-prompt-${(%):-%n}.zsh" ]]; then
  source "${XDG_CACHE_HOME:-$HOME/.cache}/p10k-instant-prompt-${(%):-%n}.zsh"
fi

# If you come from bash you might have to change your $PATH.
# export PATH=$HOME/bin:$HOME/.local/bin:/usr/local/bin:$PATH

# Path to your Oh My Zsh installation.
export ZSH="$HOME/.oh-my-zsh"

# Set name of the theme to load --- if set to "random", it will
# load a random theme each time Oh My Zsh is loaded, in which case,
# to know which specific one was loaded, run: echo $RANDOM_THEME
# See https://github.com/ohmyzsh/ohmyzsh/wiki/Themes
####ZSH_THEME="robbyrussell"
ZSH_THEME="agnoster"
ZSH_THEME="powerlevel10k/powerlevel10k"
# Set list of themes to pick from when loading at random
# Setting this variable when ZSH_THEME=random will cause zsh to load
# a theme from this variable instead of looking in $ZSH/themes/
# If set to an empty array, this variable will have no effect.
# ZSH_THEME_RANDOM_CANDIDATES=( "robbyrussell" "agnoster" )

# Uncomment the following line to use case-sensitive completion.
# CASE_SENSITIVE="true"

# Uncomment the following line to use hyphen-insensitive completion.
# Case-sensitive completion must be off. _ and - will be interchangeable.
# HYPHEN_INSENSITIVE="true"

# Uncomment one of the following lines to change the auto-update behavior
# zstyle ':omz:update' mode disabled  # disable automatic updates
# zstyle ':omz:update' mode auto      # update automatically without asking
# zstyle ':omz:update' mode reminder  # just remind me to update when it's time

# Uncomment the following line to change how often to auto-update (in days).
# zstyle ':omz:update' frequency 13

# Uncomment the following line if pasting URLs and other text is messed up.
# DISABLE_MAGIC_FUNCTIONS="true"

# Uncomment the following line to disable colors in ls.
# DISABLE_LS_COLORS="true"

# Uncomment the following line to disable auto-setting terminal title.
# DISABLE_AUTO_TITLE="true"

# Uncomment the following line to enable command auto-correction.
# ENABLE_CORRECTION="true"

# Uncomment the following line to display red dots whilst waiting for completion.
# You can also set it to another string to have that shown instead of the default red dots.
# e.g. COMPLETION_WAITING_DOTS="%F{yellow}waiting...%f"
# Caution: this setting can cause issues with multiline prompts in zsh < 5.7.1 (see #5765)
# COMPLETION_WAITING_DOTS="true"

# Uncomment the following line if you want to disable marking untracked files
# under VCS as dirty. This makes repository status check for large repositories
# much, much faster.
# DISABLE_UNTRACKED_FILES_DIRTY="true"

# Uncomment the following line if you want to change the command execution time
# stamp shown in the history command output.
# You can set one of the optional three formats:
# "mm/dd/yyyy"|"dd.mm.yyyy"|"yyyy-mm-dd"
# or set a custom format using the strftime function format specifications,
# see 'man strftime' for details.
# HIST_STAMPS="mm/dd/yyyy"

# Would you like to use another custom folder than $ZSH/custom?
# ZSH_CUSTOM=/path/to/new-custom-folder

# Which plugins would you like to load?
# Standard plugins can be found in $ZSH/plugins/
# Custom plugins may be added to $ZSH_CUSTOM/plugins/
# Example format: plugins=(rails git textmate ruby lighthouse)
# Add wisely, as too many plugins slow down shell startup.
plugins=(git)

source $ZSH/oh-my-zsh.sh

# User configuration

# export MANPATH="/usr/local/man:$MANPATH"

# You may need to manually set your language environment
# export LANG=en_US.UTF-8

# Preferred editor for local and remote sessions
# if [[ -n $SSH_CONNECTION ]]; then
#   export EDITOR='vim'
# else
#   export EDITOR='nvim'
# fi

# Compilation flags
# export ARCHFLAGS="-arch $(uname -m)"

# Set personal aliases, overriding those provided by Oh My Zsh libs,
# plugins, and themes. Aliases can be placed here, though Oh My Zsh
# users are encouraged to define aliases within a top-level file in
# the $ZSH_CUSTOM folder, with .zsh extension. Examples:
# - $ZSH_CUSTOM/aliases.zsh
# - $ZSH_CUSTOM/macos.zsh
# For a full list of active aliases, run `alias`.
#
# Example aliases
# alias zshconfig="mate ~/.zshrc"
# alias ohmyzsh="mate ~/.oh-my-zsh"

export PATH=$PATH:/Users/wclin/.spicetify

# To customize prompt, run `p10k configure` or edit ~/.p10k.zsh.
[[ ! -f ~/.p10k.zsh ]] || source ~/.p10k.zsh



export NVM_DIR="$HOME/.nvm"
[ -s "$NVM_DIR/nvm.sh" ] && \. "$NVM_DIR/nvm.sh"  # This loads nvm
[ -s "$NVM_DIR/bash_completion" ] && \. "$NVM_DIR/bash_completion"  # This loads nvm bash_completion

# Created by `pipx` on 2025-10-14 02:01:10
export PATH="$PATH:/Users/wclin/.local/bin"

# Added by Antigravity
export PATH="/Users/wclin/.antigravity/antigravity/bin:$PATH"

# opencode
export PATH=/Users/wclin/.opencode/bin:$PATH

alias olc='cd ~/claude; ollama launch claude'

# bun completions
[ -s "/Users/wclin/.bun/_bun" ] && source "/Users/wclin/.bun/_bun"

# bun
export BUN_INSTALL="$HOME/.bun"
export PATH="$BUN_INSTALL/bin:$PATH"


#alias clu='claude --model qwen3.5:4b-nvfp4 --dangerously-skip-permissions'
#alias clu9='claude --model qwen3.5:9b-nvfp4 --dangerously-skip-permissions'
#alias clu35='claude --model qwen3.5:35b-a3b-coding-nvfp4 --dangerously-skip-permissions'

alias claude-mem='bun "/Users/wclin/.claude/plugins/marketplaces/thedotmack/plugin/scripts/worker-service.cjs"'


##### 先強制取消 alias，預防萬一
####unalias clu 2>/dev/null
####
####clu() {
####    local target_dir="$HOME/claude"
####
####    # 檢查當前目錄是否在 ~/claude 之下
####    if [[ "$PWD" != "$target_dir"* ]]; then
####        cd "$target_dir" || return
####    fi
####
####    # 執行指令
####    command claude --model qwen3.5:4b-nvfp4 --dangerously-skip-permissions "$@"
####}
####
####
#### clu35() {
####    local target_dir="$HOME/claude"
####
####    # 檢查當前目錄是否在 ~/claude 之下
####    if [[ "$PWD" != "$target_dir"* ]]; then
####        cd "$target_dir" || return
####    fi
####
####    # 執行指令
####    command claude --model qwen3.5:35b-a3b-coding-nvfp4 --dangerously-skip-permissions "$@"
####}
####
#### clue() {
####    local target_dir="$HOME/claude"
####
####    # 檢查當前目錄是否在 ~/claude 之下
####    if [[ "$PWD" != "$target_dir"* ]]; then
####        cd "$target_dir" || return
####    fi
####
####    # 執行指令
####    command claude --model gemma4:e4b-nvfp4 --dangerously-skip-permissions "$@"
####}
####
####
####
####
####export ANTHROPIC_DEFAULT_SONNET_MODEL=qwen3.5:4b-nvfp4
####export ANTHROPIC_DEFAULT_HAIKU_MODEL=qwen3.5:4b-nvfp4
####export ANTHROPIC_DEFAULT_OPUS_MODEL=qwen3.5:4b-nvfp4
####

## pyright env
export ENABLE_LSP_TOOLS=1






########################3
#alias opencode='cd llama; opencode'




# Claude Code + Local Qwen 3.5 — because localhost > cloud
export LM_MODEL="unsloth/Qwen3.5-9B-GGUF"
export ANTHROPIC_BASE_URL="http://127.0.0.1:8080"
export ANTHROPIC_AUTH_TOKEN="local"
export CLAUDE_CODE_MAX_OUTPUT_TOKENS=128000
export ANTHROPIC_MODEL="$LM_MODEL"
export ANTHROPIC_DEFAULT_OPUS_MODEL="$LM_MODEL"
export ANTHROPIC_DEFAULT_SONNET_MODEL="$LM_MODEL"
export ANTHROPIC_DEFAULT_HAIKU_MODEL="$LM_MODEL"
export CLAUDE_CODE_SUBAGENT_MODEL="$LM_MODEL"
