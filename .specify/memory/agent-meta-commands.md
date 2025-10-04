# Agent Meta-Command Reference

Comparison of built-in slash commands available to Claude Code vs GitHub Copilot CLI.

---

## Claude Code (Agent 1 - Primary)

**Shell**: Bash  
**Access**: Diverse high-level user commands for leadership and delegation roles. 

### File & Directory Management
- `/add-dir` - Add new working directory
- `/agents` - Manage agent configurations
- `/bashes` - List and manage background tasks
- `/cwd [directory]` - Change working directory or show current

### Context & History
- `@` - Mention files, include contents in current context
- `/compact` - Clear conversation history but keep summary in context (optional: `/compact [instructions]`)
- `/context` - Visualize current context usage as colored grid
- `/cost` - Show total cost and duration of current session
- `/resume` - Resume a conversation/notes
- `/rewind` - Restore conversation to previous point

### Configuration & Setup
- `/config` - Open config panel
- `/doctor` - Diagnose and verify Claude Code installation and settings
- `/init` - Initialize new CLAUDE.md file with codebase documentation
- `/install-github-app` - Set up Claude GitHub Actions for repository

### Development Tools
- `/feedback` - Submit feedback about Claude Code/file/clipboard
- `/help` - Show help and available commands
- `/hooks` - Manage hook configurations for tool events
- `/ide` - Manage IDE integrations and show status
- `/login` - Sign in with Anthropic account
- `/logout` - Sign out from Anthropic account
- `/mcp` - Manage MCP servers
- `/migrate-installer` - Migrate from global npm installation to local
- `/model` - Set the AI model for Claude Code
- `/output-style` - Set output style directly or from menu
- `/output-style:new` - Create custom output style
- `/permissions` - Manage allow & deny tool permission rules
- `/pr-comments` - Get comments from GitHub pull request
- `/privacy-settings` - View and update privacy settings
- `/review` - Review a pull request
- `/security-review` - Complete security review of pending changes on current branch
- `/status` - Show Claude Code status (version, model, account, API connectivity, tool statuses)
- `/statusline` - Set up Claude Code's status line UI
- `/terminal-setup` - Install Shift+Enter key binding for newlines
- `/todos` - List current todo items
- `/upgrade` - Upgrade to Max for higher rate limits and more Opus
- `/usage` - Show plan usage limits
- `/vim` - Toggle between Vim and Normal editing modes

### Session Control
- `/exit` - Exit the REPL
- `Esc` - Cancel current operation
- `Ctrl+c` - Cancel operation if thinking, clear input if present, or exit
- `Ctrl+d` - Shutdown
- `Ctrl+l` - Clear the screen

### Keyboard Shortcuts
- `!` - Bash mode: double tap esc to clear input
- `/` - Command mode: alt + m to auto-accept edits
- `#` - Memorize: ctrl + t to show todos
- Backslash `\` + return `↵` for newLine

**Custom Commands**: No custom commands found in this installation

---

## GitHub Copilot CLI (Agent 2 - Specialist)

**Shell**: PowerShell  
**Access**: Built-in GitHub Copilot integration and limited user commands for targeted iterations.

### Directory & Session Management
- `/add-dir <directory>` - Add directory to allowed list for file access
- `/clear` - Clear the conversation history
- `/cwd [directory]` - Change working directory or show current directory
- `/exit` - Exit the CLI
- `/feedback` - Provide feedback about the CLI

### Help & Information
- `/help` - Show help for interactive commands
- `/list-dirs` - Display all allowed directories for file access
- `/login` - Log in to Copilot
- `/logout` - Log out of Copilot
- `/session` - Show information about current CLI session
- `/usage` - Display session usage metrics and statistics
- `/user [show|list|switch]` - Manage GitHub user list

### MCP & Model Management
- `/mcp [show|add|edit|delete|disable|enable] [server-name]` - Manage MCP server configuration
- `/model [model]` - Select AI model to use
- `/reset-allowed-tools` - Reset the list of allowed tools

### Theme & Configuration  
- `/theme [show|set|list] [auto|dark|light]` - View or configure terminal theme

**Instructions Sourcing**:
Copilot respects instructions from multiple locations:
- `.github/instructions/**/*.instructions.md`
- `.github/copilot-instructions.md`
- `**/.AGENTS.md`
- `CLAUDE.md`
- `GEMINI.md`
- `$HOME/.copilot/copilot-instructions.md`

---

## Key Differences

### Unique to Claude Code
- **Context visualization** (`/context`) - See token usage as colored grid
- **Cost tracking** (`/cost`) - Monitor session spending
- **Compact mode** (`/compact`) - Summarize history without full clear
- **Review tools** (`/review`, `/pr-comments`, `/security-review`) - PR and code review workflows
- **IDE integration** (`/ide`) - Direct IDE connections
- **Background tasks** (`/bashes`) - Manage async operations
- **Output styling** (`/output-style`) - Customize response format
- **Vim mode** (`/vim`) - Modal editing
- **Privacy controls** (`/privacy-settings`) - Granular privacy management

### Unique to Copilot CLI
- **User switching** (`/user`) - Multi-account GitHub management
- **Theme control** (`/theme`) - Terminal theme configuration
- **Session metrics** (`/usage`) - Detailed usage statistics

### Shared Commands
- Directory management (`/add-dir`, `/cwd`)
- Session control (`/exit`, `/clear`)
- Authentication (`/login`, `/logout`)
- MCP management (`/mcp`)
- Model selection (`/model`)
- Help system (`/help`)
- Feedback (`/feedback`)

---

## Usage Recommendations

### Use Claude Code For:
- Extended development sessions (cost/context tracking)
- PR reviews and code security analysis
- IDE-integrated workflows
- Complex multi-file refactoring (context grid helps manage tokens)
- Custom output styling preferences
- Background task management

### Use Copilot CLI For:
- Quick git operations (better git tooling)
- Multi-account GitHub workflows (user switching)
- Terminal theme-sensitive work
- Simple, focused tasks (less overhead)
- Cross-platform shell testing (PowerShell perspective)

### Git Operations (Per Protocol):
- **Copilot preferred** for: Branch creation, worktree management, complex git workflows
- **Both capable** of: Commits, pushes, basic git operations
- **Each handles**: Their own work independently

---

## Notes

**Context Limits**: Claude Code provides better visibility into context usage (`/context`, `/cost`)

**Multi-Agent**: Both tools support MCP servers and can coordinate through `collaboration/` docs

**Instructions**: Both respect `.github/copilot-instructions.md` and project-specific instruction files

**Shells**: Claude Code favors Bash, Copilot favors PowerShell (cross-platform compatibility benefit)
