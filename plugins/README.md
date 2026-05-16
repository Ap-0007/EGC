# Plugins and Marketplaces

Plugins extend Gemini Code with new tools and capabilities. This guide covers installation and marketplace management.

---

## Marketplaces

Marketplaces are repositories of installable plugins.

### Adding a Marketplace

```bash
# Add official Anthropic marketplace
egc plugin marketplace add https://github.com/anthropics/egc-plugins-official

# Add community marketplaces (mgrep by @mixedbread-ai)
egc plugin marketplace add https://github.com/mixedbread-ai/mgrep
```

### Recommended Marketplaces

| Marketplace | Source |
|-------------|--------|
| egc-plugins-official | `anthropics/egc-plugins-official` |
| everything-gemini-plugins | `anthropics/everything-gemini` |
| Mixedbread-Grep (@mixedbread-ai) | `mixedbread-ai/mgrep` |

---

## Installing Plugins

```bash
# Open plugins browser
/plugins

# Or install directly
egc plugin install typescript-lsp@egc-plugins-official
```

### Recommended Plugins

**Development:**
- `typescript-lsp` - TypeScript intelligence
- `pyright-lsp` - Python type checking
- `hookify` - Create hooks conversationally
- `code-simplifier` - Refactor code

**Code Quality:**
- `code-review` - Code review
- `pr-review-toolkit` - PR automation
- `security-guidance` - Security checks

**Search:**
- `mgrep` - Enhanced search (better than ripgrep)
- `context7` - Live documentation lookup

**Workflow:**
- `commit-commands` - Git workflow
- `frontend-patterns` - UI patterns
- `feature-dev` - Feature development

---

## Quick Setup

```bash
# Add marketplaces
egc plugin marketplace add https://github.com/anthropics/egc-plugins-official
egc plugin marketplace add https://github.com/mixedbread-ai/mgrep

# Open /plugins and install what you need
```

---

## Plugin Files Location

```
~/.gemini/plugins/
|-- cache/                    # Downloaded plugins
|-- installed_plugins.json    # Installed list
|-- known_marketplaces.json   # Added marketplaces
|-- marketplaces/             # Marketplace data
```
