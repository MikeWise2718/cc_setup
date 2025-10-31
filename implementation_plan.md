# Implementation Plan for cc_setup.py

## Overview

A Python script that copies Claude Code artifacts from source repositories (tac-6, tac-7) into a target project, supporting both basic and isolated worktree configurations.

---

## Project Structure

```
cc_setup/
├── pyproject.toml          # uv project configuration (Python 3.13)
├── README.md               # Usage instructions with examples
├── implementation_plan.md  # This file
├── cc_setup.py             # Main script
└── logs/                   # Created at runtime for log files
```

---

## Core Components

### 1. Command-Line Interface (argparse)

**Required Arguments:**
- `--target` or `-t`: Target directory path (required)
- `--mode` or `-m`: Either "basic" or "iso" (required)

**Optional Flags:**
- `--execute` or `-e`: Flag to actually copy files (default: False for dry-run)
- `--overwrite` or `-o`: Flag to overwrite existing files (default: False)
- `--help-artifacts`: Show what artifacts are installed in each mode
- `--source-dir`: Source directory for tac repos (default: d:\tac)

### 2. Artifact Mapping System

**Basic mode artifacts** (from tac-6 or tac-7):
- 1 settings.json file
- 5 hooks files:
  - dangerous_command.py
  - notification.py
  - env_protection.py
  - pre_compact.py
  - user_prompt_submit.py
- 13 command files:
  - install.md, prime.md, bug.md, chore.md, feature.md
  - implement.md, start.md, tools.md, commit.md
  - pull_request.md, review.md, document.md, patch.md
- 6 script files:
  - start.sh, stop_apps.sh, copy_dot_env.sh
  - clear_issue_comments.sh, delete_pr.sh, reset_db.sh
- 4 optional ADW files:
  - adw_plan.py, adw_build.py, adw_test.py, adw_patch.py

**Iso mode artifacts** (from tac-7):
- 1 settings.json file
- 5 hooks files (same as basic)
- 17-21 command files (basic 13 + worktree commands):
  - cleanup_worktrees.md, install_worktree.md
  - init_worktree.md, clean_worktree.md
  - test.md, test_e2e.md, health_check.md, track_agentic_kpis.md (optional)
- 8 script files (basic 6 + worktree scripts):
  - check_ports.sh, purge_tree.sh
- 14 ADW files (isolated versions):
  - adw_plan_iso.py, adw_build_iso.py, adw_test_iso.py, adw_review_iso.py
  - adw_plan_build_iso.py, adw_plan_build_test_iso.py
  - adw_plan_build_review_iso.py, adw_plan_build_test_review_iso.py
  - adw_plan_build_document_iso.py, adw_patch_iso.py
  - adw_sdlc_iso.py, adw_sdlc_zte_iso.py
  - adw_ship_iso.py, adw_document_iso.py

### 3. File Operations Module

**Functions:**
- Directory structure validation - Check if target has proper structure
- File existence checking - Detect which files would be overwritten
- Safe copying - Copy files without overwriting (unless --overwrite flag)
- Permission setting - Make scripts executable on Unix systems

### 4. Logging System

- Create timestamped log files in `logs/` directory
- Log format: `cc_setup_YYYYMMDD_HHMMSS.log`
- Content: all parameters, decisions, warnings, actions taken/skipped

### 5. Rich Output System

Using Rich library features:

**Panels & Layout:**
- Header panel showing configuration (target, mode, dry-run/execute)
- Summary panel at end with statistics

**Tables:**
- File listing with columns: Category | File | Status | Action
- Status indicators: ✓ (green), ⚠ (yellow), ✗ (red)
- Color-coded rows based on action

**Progress:**
- Progress bars for file copy operations
- Live updating status during execution

**Console Markup:**
- `[green]` for success messages
- `[yellow]` for warnings
- `[red]` for errors
- `[bold]` for emphasis

**Tree View:**
- Show target directory structure to be created
- Display artifact organization

**Example Output:**
```
╭─────────────────────────────────────────────────────╮
│ Claude Code Setup Tool                              │
│ Target: D:\projects\my-app                          │
│ Mode: Basic | DRY RUN                               │
╰─────────────────────────────────────────────────────╯

📁 Directory Structure to Create:
.claude/
├── commands/
├── hooks/
├── adws/
└── settings.json
scripts/

📋 Artifacts Analysis:

┏━━━━━━━━━━━━━┳━━━━━━━━━━━━━━━━━━━━━━━━━┳━━━━━━━━━━━━┳━━━━━━━━━━━━┓
┃ Category    ┃ File                     ┃ Status     ┃ Action     ┃
┡━━━━━━━━━━━━━╇━━━━━━━━━━━━━━━━━━━━━━━━━╇━━━━━━━━━━━━╇━━━━━━━━━━━━┩
│ Settings    │ settings.json            │ ✓ New      │ Will copy  │
│ Hooks       │ dangerous_command.py     │ ⚠ Exists   │ Skip       │
│ Hooks       │ notification.py          │ ✓ New      │ Will copy  │
│ Commands    │ install.md               │ ✓ New      │ Will copy  │
└─────────────┴──────────────────────────┴────────────┴────────────┘

╭─────────────────────────────────────────────────────╮
│ Summary                                              │
│ • 24 files to copy                                   │
│ • 1 file exists (will skip)                          │
│ • 0 files will be overwritten                        │
╰─────────────────────────────────────────────────────╯

⚠ This is a DRY RUN. Use --execute to perform actual copy.
```

### 6. Validation System

**Checks:**
- Target directory exists (or can be created)
- Source tac directories exist (d:\tac\tac-6, d:\tac\tac-7)
- Required source files are present
- Proper directory structure in target

### 7. Help Artifacts Display

When `--help-artifacts` is used:
- Panel 1: Basic Mode artifacts with descriptions
- Panel 2: Iso Mode artifacts with descriptions
- Use tables within panels for organized display

---

## Implementation Steps

### Phase 1: Project Setup
1. Initialize uv project with pyproject.toml (Python 3.13)
2. Add rich dependency
3. Set up basic directory structure

### Phase 2: Data Structures
4. Create artifact mapping dictionaries for both modes
5. Define artifact metadata (source repo, description, category)
6. Build file path resolution system

### Phase 3: CLI & Validation
7. Implement argument parser with all required flags
8. Add target/source directory validation
9. Implement --help-artifacts display with Rich panels

### Phase 4: Analysis Mode
10. Implement dry-run analysis (scan, detect conflicts)
11. Build Rich table for file listing
12. Create summary statistics
13. Display directory tree structure

### Phase 5: Execution Mode
14. Implement directory creation
15. Add file copying with Rich progress bars
16. Handle overwrite logic
17. Set executable permissions for shell scripts

### Phase 6: Output & Logging
18. Create Rich console output system
19. Implement logging infrastructure
20. Add header/footer panels
21. Create status indicators and color coding

### Phase 7: Error Handling & Documentation
22. Add comprehensive error handling with Rich tracebacks
23. Create detailed README with usage examples
24. Add inline code documentation
25. Test both basic and iso modes thoroughly

---

## Key Features

### Dry-Run Mode (default)
- Displays header panel with configuration
- Shows directory tree to be created
- Lists all files in organized table
- Highlights conflicts/warnings in yellow
- Summary panel with statistics
- No actual file operations

### Execute Mode (--execute flag)
- Same analysis display as dry-run
- Live progress bars for each category (hooks, commands, scripts, ADWs)
- Real-time status updates
- Success confirmation with Rich panel
- Log file creation

### Help Artifacts (--help-artifacts)
- Two-column layout for basic vs iso comparison
- Tables showing all artifacts per mode
- Descriptions and purposes
- File counts and categories

---

## Dependencies

- **Python 3.13**
- **rich** - Enhanced terminal output
- **Standard library**: argparse, pathlib, shutil, logging, datetime

---

## Rich-Specific Features Used

- `Console` - main output handler
- `Table` - file listings
- `Panel` - headers, summaries, help display
- `Tree` - directory structure visualization
- `Progress` - file copy progress bars
- `Syntax` - code examples in help
- `Markdown` - rendering help text
- `Live` - real-time updates during execution

---

## Target Directory Structure

### Basic Mode
```
target-project/
├── .claude/
│   ├── commands/           # 13 slash commands
│   ├── hooks/              # 5 hooks
│   ├── adws/               # 4 ADWs (optional)
│   └── settings.json
└── scripts/                # 6 utility scripts
```

### Iso Mode
```
target-project/
├── .claude/
│   ├── commands/           # 17-21 slash commands
│   ├── hooks/              # 5 hooks
│   ├── adws/               # 14 isolated ADWs
│   └── settings.json
├── scripts/                # 8 utility scripts
└── trees/                  # Worktree directory (created by worktree commands)
```

---

## Usage Examples

### Dry-Run (Analysis Only)
```bash
uv run cc_setup.py --target /path/to/project --mode basic
```

### Execute Basic Mode
```bash
uv run cc_setup.py --target /path/to/project --mode basic --execute
```

### Execute Iso Mode with Overwrite
```bash
uv run cc_setup.py --target /path/to/project --mode iso --execute --overwrite
```

### Show Artifacts Help
```bash
uv run cc_setup.py --help-artifacts
```

---

## Error Handling

- Missing source directories - Clear error message with path
- Missing source files - List which files are missing
- Target directory issues - Validation with helpful messages
- Permission errors - Catch and report with context
- Invalid mode - Show valid options

---

## Logging

Each run creates a log file with:
- Timestamp and command-line arguments
- Source and target directories
- Mode selection
- Each file operation (copy/skip/overwrite)
- Any errors or warnings
- Summary statistics

Log location: `logs/cc_setup_YYYYMMDD_HHMMSS.log`

---

## Testing Strategy

1. Test with non-existent target directory
2. Test with existing target directory (empty)
3. Test with partial existing artifacts
4. Test with all artifacts already present
5. Test overwrite flag functionality
6. Test both basic and iso modes
7. Test with missing source files
8. Test dry-run vs execute mode consistency
9. Test on Windows (primary) and Unix systems
10. Verify log file creation and content
