# Agent Guidelines

- Create a `history/` directory in the project root
- Store ALL AI-generated planning/design docs in `history/`
- Keep the repository root clean and focused on permanent project files
- Only access `history/` when explicitly asked to review past planning

**Example .gitignore entry (optional):**

```
# AI planning documents (ephemeral)
history/
```

**Benefits:**

- ✅ Clean repository root
- ✅ Clear separation between ephemeral and permanent documentation
- ✅ Easy to exclude from version control if desired
- ✅ Preserves planning history for archeological research
- ✅ Reduces noise when browsing the project

### CLI Help

Run `bd <command> --help` to see all available flags for any command.
For example: `bd create --help` shows `--parent`, `--deps`, `--assignee`, etc.

### Important Rules

- ✅ Use bd for ALL task tracking
- ✅ Always use `--json` flag for programmatic use
- ✅ Link discovered work with `discovered-from` dependencies
- ✅ Check `bd ready` before asking "what should I work on?"
- ✅ Store AI planning docs in `history/` directory
- ✅ Run `bd <cmd> --help` to discover available flags
- ❌ Do NOT create markdown TODO lists
- ❌ Do NOT use external issue trackers
- ❌ Do NOT duplicate tracking systems
- ❌ Do NOT clutter repo root with planning documents







fix/system-prompt-normalization

Title:

fix(opencode): collapse system prompt fragments into a single system message

Body:

## Summary

This normalizes the final system prompt into a single system message before provider request construction.

## Problem

`LLM.stream()` builds a `system: string[]` from:
- provider/agent prompt
- `input.system`
- `user.system`
- plugin mutations via `experimental.chat.system.transform`

That array was then mapped to multiple separate `role: "system"` messages for most providers.

Some strict backends/templates are sensitive to this representation, and multiple system messages can cause prompt
handling failures.

## Fix

Collapse the final `system` fragments into a single newline-joined system string before building provider messages.

This keeps all system content while avoiding multiple system-message entries in the final request.

## Why this is safe

- No system content is removed
- Only the representation changes
- Plugin modifications still apply before normalization
- anomalyco/opencode#15059
