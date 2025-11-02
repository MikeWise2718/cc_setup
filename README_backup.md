# cc_setup - Claude Code Setup Tool

A Python utility for copying Claude Code artifacts from a local store into target projects. Supports both basic and isolated worktree configurations with dynamic artifact discovery.

## Features

- **Two Setup Modes**: Basic and Isolated (worktree-capable)
- **Local Artifact Store**: Self-contained with all artifacts included
- **Dynamic Discovery**: Automatically detects available artifacts
- **Dry-Run Analysis**: Preview changes before executing
- **Rich Terminal Output**: Beautiful, color-coded displays with tables and progress bars
- **Smart Overwrite Control**: Optionally skip or overwrite existing files
- **Comprehensive Logging**: Detailed logs of all operations
- **No External Dependencies**: All artifacts stored locally

## Installation

This project uses [uv](https://github.com/astral-sh/uv) for dependency management.

```bash
# Clone or navigate to the cc_setup directory
cd cc_setup

# Install dependencies (uv will handle this automatically when running)
uv sync
```

## Quick Start

### Dry Run (Analysis Only)
Preview what would be copied without making changes:

```bash
uv run cc_setup.py --target /path/to/project --mode basic
```

### Execute Basic Setup
Copy artifacts for a standard single-worktree project:

```bash
uv run cc_setup.py --target /path/to/project --mode basic --execute
```

### Execute Isolated Worktree Setup
Copy artifacts for projects using isolated worktrees:

```bash
uv run cc_setup.py --target /path/to/project --mode iso --execute
```

### Overwrite Existing Files
Force overwrite of existing artifacts:

```bash
uv run cc_setup.py --target /path/to/project --mode basic --execute --overwrite
```

### View Available Artifacts
See what artifacts are included in each mode:

```bash
uv run cc_setup.py --help-artifacts
```

## Command-Line Options

| Option | Short | Description |
|--------|-------|-------------|
| `--target` | `-t` | Target directory path (required) |
| `--mode` | `-m` | Setup mode: `basic` or `iso` (required) |
| `--execute` | `-e` | Actually copy files (default: dry-run) |
| `--overwrite` | `-o` | Overwrite existing files (default: skip) |
| `--help-artifacts` | | Show available artifacts for each mode |
| `--help` | `-h` | Show help message |

## Project Structure

```
cc_setup/
├── cc_setup.py             # Main script
├── migrate_to_store.py     # Migration tool (one-time use)
├── pyproject.toml          # Project configuration
├── README.md               # This file
├── implement_local_store.md # Implementation plan for local store
├── logs/                   # Runtime log files
└── store/                  # Local artifact storage
    ├── migration_log.txt   # Log from initial migration
    ├── basic/              # Basic mode artifacts
    │   ├── settings.json
    │   ├── hooks/
    │   ├── commands/
    │   ├── scripts/
    │   └── adws/
    └── iso/                # Isolated worktree mode
        ├── settings.json
        ├── hooks/
        ├── commands/
        ├── scripts/
        └── adws/
```

## Setup Modes

### Basic Mode (51 artifacts)

Installs standard Claude Code artifacts for single-worktree projects:

- **Settings**: 1 file (`settings.json`)
- **Hooks**: 7 files (notification, post_tool_use, pre_compact, pre_tool_use, stop, subagent_stop, user_prompt_submit)
- **Commands**: 22 slash commands (bug, chore, commit, document, feature, implement, install, patch, prime, pull_request, review, start, test, tools, and more)
- **Scripts**: 8 utility scripts (start, stop_apps, copy_dot_env, delete_pr, reset_db, and more)
- **ADWs**: 13 Agent Developer Workflow files (plan, build, test, review, and combinations)

**Directory Structure:**
```
target-project/
├── .claude/
│   ├── commands/           # 22 slash commands
│   ├── hooks/              # 7 hooks
│   ├── adws/               # 13 ADWs
│   └── settings.json
└── scripts/                # 8 utility scripts
```

### Isolated Worktree Mode (60 artifacts)

Installs enhanced artifacts with worktree support:

- **Settings**: 1 file (worktree-configured `settings.json`)
- **Hooks**: 7 files (same as basic)
- **Commands**: 27 slash commands (basic + cleanup_worktrees, install_worktree, health_check, track_agentic_kpis, in_loop_review)
- **Scripts**: 10 utility scripts (basic + check_ports, purge_tree)
- **ADWs**: 15 isolated Agent Developer Workflow files for parallel development

**Directory Structure:**
```
target-project/
├── .claude/
│   ├── commands/           # 27 slash commands
│   ├── hooks/              # 7 hooks
│   ├── adws/               # 15 isolated ADWs
│   └── settings.json
├── scripts/                # 10 utility scripts
└── trees/                  # Worktree directory (created by commands)
```

## Usage Examples

### Example 1: New Project Setup (Basic)

```bash
# First, do a dry run to see what will be copied
uv run cc_setup.py --target D:\projects\my-new-app --mode basic

# Review the output, then execute
uv run cc_setup.py --target D:\projects\my-new-app --mode basic --execute
```

### Example 2: Upgrade to Isolated Worktrees

```bash
# Add isolated worktree support to an existing project
uv run cc_setup.py --target D:\projects\existing-app --mode iso --execute

# Use --overwrite if you want to replace existing artifacts
uv run cc_setup.py --target D:\projects\existing-app --mode iso --execute --overwrite
```

### Example 3: Check Available Artifacts

```bash
# See detailed list of all artifacts
uv run cc_setup.py --help-artifacts
```

## Output Explained

### Dry-Run Output

When you run without `--execute`, you'll see:

1. **Header Panel**: Configuration summary (target, mode, store location)
2. **Store Validation**: Confirms local artifact store is valid
3. **Directory Tree**: Structure to be created
4. **Artifacts Table**: Detailed list of all files with:
   - Category (Settings, Hooks, Commands, Scripts, ADWs)
   - Filename
   - Status (✓ New, ⚠ Exists)
   - Action (Will copy, Skip, etc.)
5. **Summary Panel**: Statistics (files to copy, existing files, overwrites)
6. **Warning**: Reminder that this is a dry run

### Execute Output

When you run with `--execute`, you'll see:

1. Same analysis as dry-run
2. **Progress Bar**: Real-time copy progress
3. **Success Message**: Confirmation of completion
4. **Final Summary**: Files copied and skipped

### File Status Indicators

The tool compares existing files with source files to determine their status:

- **✓ New** (Green): File doesn't exist in target, will be copied
- **✓ Identical** (Cyan): File exists and matches source exactly (already up-to-date)
- **⚠ Different** (Yellow): File exists but differs from source (will skip unless --overwrite)
- **⚠ Overwrite** (Red): File exists and will be overwritten (--overwrite flag)
- **✗ Missing** (Red Dim): Source file not found

This helps you understand which files are current vs. which may need updating.

### Color Coding

- **Green**: Success, new files, normal operations
- **Cyan**: Identical files (already up-to-date)
- **Yellow**: Warnings, different files that will be skipped
- **Red**: Errors, files that will be overwritten
- **Cyan**: Informational text, headers
- **Dim**: Secondary information (store path)

## Logging

Every run creates a timestamped log file in the `logs/` directory:

```
logs/cc_setup_20251031_172600.log
```

The log contains:
- Command-line arguments
- Store location
- Each file operation (copy/skip/overwrite)
- Warnings and errors
- Summary statistics

## File Handling

### Default Behavior (No Overwrite)

- **New files**: Copied to target
- **Identical files**: Skipped (already up-to-date)
- **Different files**: Skipped (not modified)
- **Missing source files**: N/A (dynamic discovery only shows existing files)

### With `--overwrite` Flag

- **New files**: Copied to target
- **Identical files**: Skipped (no need to overwrite)
- **Different files**: Overwritten with source version

### Executable Permissions

Shell scripts (`.sh` files) are automatically made executable on Unix-like systems.

## Customizing Artifacts

The local store makes it easy to customize which artifacts are included:

### Adding Artifacts

1. Navigate to `store/basic/` or `store/iso/`
2. Add your file to the appropriate category folder:
   - `hooks/` for hook scripts
   - `commands/` for slash commands
   - `scripts/` for utility scripts
   - `adws/` for Agent Developer Workflows
3. The tool will automatically discover and include it

### Removing Artifacts

1. Simply delete the file from the store directory
2. The tool will no longer show or copy it

### Updating Artifacts

1. Replace the file in the store directory
2. Use `--overwrite` flag to update existing installations

## Migrating Artifacts

The project includes a one-time migration script (`migrate_to_store.py`) that was used to populate the store from external repositories. For most users, this is not needed as the store is already populated.

If you need to refresh artifacts from source repositories:

```bash
python migrate_to_store.py
```

This will copy artifacts from `d:\tac\tac-6` and `d:\tac\tac-7` into the local store and create a detailed migration log at `store/migration_log.txt`.

## Requirements

- Python 3.13+
- rich library (for terminal output)
- uv package manager

## Troubleshooting

### "Store directory not found"

The tool cannot find the `store/` directory. Ensure you're running the script from the correct directory:

```bash
cd /path/to/cc_setup
uv run cc_setup.py --help-artifacts
```

### "No artifacts found"

The store directory exists but is empty. Check that `store/basic/` or `store/iso/` contains artifact files.

### Permission Errors

On Unix systems, ensure you have write permissions to the target directory. You may need to run with appropriate permissions or change the target directory owner.

## Version History

### Version 2.0 (Local Store Architecture)
- **Breaking Change**: Moved from external repository dependencies to local store
- Dynamic artifact discovery (no hard-coded lists)
- Removed `--source-dir` parameter
- No more "missing file" warnings
- Self-contained and portable

### Version 1.0 (External Repository)
- Initial release with external `d:\tac` dependency
- Hard-coded artifact lists
- Required specific directory structure

## Benefits of Local Store

### For Users
1. **No External Dependencies**: No need for `d:\tac` directory
2. **Predictable**: Always shows what actually exists
3. **Customizable**: Easy to add/remove artifacts
4. **Portable**: Entire project can be shared or version controlled
5. **Fast**: No external file access needed

### For Developers
1. **Simpler Code**: Dynamic discovery vs hard-coding
2. **Easier Testing**: Test artifacts right in the project
3. **Better Separation**: Clear separation between code and data
4. **Easier Updates**: Update artifacts without code changes

## Support

For issues or questions, check the log files in the `logs/` directory for detailed error information.

## License

This tool is designed for internal use with Claude Code projects.
