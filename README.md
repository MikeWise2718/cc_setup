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

### Option 1: Use with `uv run` (Recommended for Development)
No additional setup needed. Just run commands with `uv run cc_setup` from the project directory.

### Option 2: Install Globally (For System-Wide Access)
Install cc_setup as a global tool to use the `cc_setup` command from anywhere:

```bash
# Install globally
uv tool install .

# Now you can use 'cc_setup' from any directory
cc_setup --help

# To uninstall
uv tool uninstall cc_setup
```

**Note**: The `--force` flag may use cached builds. For guaranteed fresh installation, see the Updating Global Installation section below.

## Updating Global Installation

When you make changes to the code and want to update the globally installed version, follow these steps to ensure a clean rebuild:

### Step 1: Bump the Version
Edit `pyproject.toml` and increment the version number:

```toml
[project]
name = "cc_setup"
version = "0.3.0"  # Increment from 0.2.0
```

### Step 2: Uninstall and Reinstall
```bash
# Navigate to cc_setup directory
cd cc_setup

# Uninstall the old version
uv tool uninstall cc_setup

# Install the new version (this forces a fresh build)
uv tool install .

# Verify the new version is installed
cc_setup -h
```

### Why Version Bumping is Necessary

Using `uv tool install --force .` may use cached builds, causing your changes not to appear. Bumping the version ensures:
- A fresh build from source
- No cached artifacts are used
- All changes are properly reflected

### Development vs Production

**For Development (no installation needed):**
```bash
# Run directly from source - changes take effect immediately
uv run cc_setup -t /path/to/project -m basic
```

**For Production (global installation):**
```bash
# After bumping version and reinstalling
cc_setup -t /path/to/project -m basic
```

## Quick Start

### Dry Run (Analysis Only)
Preview what would be copied without making changes:

```bash
uv run cc_setup --target /path/to/project --mode basic
# Short form:
uv run cc_setup -t /path/to/project -m basic
```

### Execute Basic Setup
Copy artifacts for a standard single-worktree project:

```bash
uv run cc_setup --target /path/to/project --mode basic --execute
# Short form:
uv run cc_setup -t /path/to/project -m basic -ex
```

### Execute Isolated Worktree Setup
Copy artifacts for projects using isolated worktrees:

```bash
uv run cc_setup --target /path/to/project --mode iso --execute
# Short form:
uv run cc_setup -t /path/to/project -m iso -ex
```

### Overwrite Existing Files
Force overwrite of existing artifacts:

```bash
uv run cc_setup --target /path/to/project --mode basic --execute --overwrite
# Short form:
uv run cc_setup -t /path/to/project -m basic -ex -ov
```

### View Available Artifacts
See what artifacts are included in each mode:

```bash
uv run cc_setup --help-artifacts
# Short form:
uv run cc_setup -ha
```

### View Usage Examples
Display usage examples showing both long-form and short-form commands:

```bash
uv run cc_setup --help-examples
# Short form:
uv run cc_setup -hx
```

## Command-Line Options

| Option | Short | Description |
|--------|-------|-------------|
| `--target` | `-t` | Target directory path (required) |
| `--mode` | `-m` | Setup mode: `basic` or `iso` (required for artifact mode) |
| `--execute` | `-ex` | Actually perform operations (default: dry-run) |
| `--overwrite` | `-ov` | Overwrite existing files (default: skip) |
| `--gitignore` | `-gi` | Manage .gitignore for specified language (e.g., `python`, `csharp`) |
| `--gitignore_execute` | `-gix` | GitIgnore operation: `compare`, `merge`, or `replace` (default: compare) |
| `--gitignore_compare_mode` | `-gic` | Comparison mode: `diff` or `set` (default: diff) |
| `--help-artifacts` | `-ha` | Show available artifacts for each mode |
| `--help-examples` | `-hx` | Show usage examples with both long and short forms |
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

## GitIgnore Management

In addition to managing Claude Code artifacts, cc_setup can manage your project's `.gitignore` file using language-specific templates stored in `store/git/`.

### Available Operations

#### Compare (Default)
Compare your project's `.gitignore` with the template using two different modes:

**Diff Mode (default)** - Line-by-line unified diff:
```bash
uv run cc_setup --target /path/to/project --gitignore python
# Short form:
uv run cc_setup -t /path/to/project -gi python

# or explicitly:
uv run cc_setup --target /path/to/project --gitignore python --gitignore_compare_mode diff
# Short form:
uv run cc_setup -t /path/to/project -gi python -gic diff
```

Output shows:
- Lines that would be added (green, + prefix)
- Lines in your file but not in template (red, - prefix)
- Context lines for reference

**Set Mode** - Order-independent pattern comparison:
```bash
uv run cc_setup --target /path/to/project --gitignore python --gitignore_compare_mode set
# Short form:
uv run cc_setup -t /path/to/project -gi python -gic set
```

Output shows:
- **Missing from Target** (green): Patterns in template but not in your .gitignore
- **Extra in Target** (yellow): Custom patterns in your .gitignore but not in template
- **Common Patterns** (cyan): Patterns present in both files
- Statistics summary with pattern counts

**When to use each mode:**
- Use `diff` mode to see exact line-by-line changes including comments and order
- Use `set` mode for semantic comparison when you only care about which patterns are missing or extra (order-independent)

#### Merge
Adds missing patterns from the template while preserving all existing entries:

```bash
# Preview what will be added (dry-run)
uv run cc_setup --target /path/to/project --gitignore python --gitignore_execute merge
# Short form:
uv run cc_setup -t /path/to/project -gi python -gix merge

# Execute merge
uv run cc_setup --target /path/to/project --gitignore python --gitignore_execute merge --execute
# Short form:
uv run cc_setup -t /path/to/project -gi python -gix merge -ex
```

Features:
- **Preserves all existing patterns** - nothing is removed
- Creates `.gitignore.backup` before modifying
- Adds new patterns with a header comment
- Ideal for updating existing projects

#### Replace
Completely replaces your `.gitignore` with the template:

```bash
# Preview replacement (dry-run)
uv run cc_setup --target /path/to/project --gitignore csharp --gitignore_execute replace
# Short form:
uv run cc_setup -t /path/to/project -gi csharp -gix replace

# Execute replacement
uv run cc_setup --target /path/to/project --gitignore csharp --gitignore_execute replace --execute
# Short form:
uv run cc_setup -t /path/to/project -gi csharp -gix replace -ex
```

Features:
- Creates `.gitignore.backup` before replacing
- **Warning**: Removes all existing custom patterns
- Ideal for new projects or complete reset

### Available Templates

Currently supported languages:
- **python** - Python projects (virtual environments, pytest, build artifacts)
- **csharp** - C# / .NET projects (Visual Studio, build outputs, NuGet)

View available templates:
```bash
ls store/git/
```

### GitIgnore Examples

#### Example 1: New Python Project
```bash
# Create .gitignore for new Python project
uv run cc_setup --target /path/to/new-python-project --gitignore python --gitignore_execute replace --execute
# Short form:
uv run cc_setup -t /path/to/new-python-project -gi python -gix replace -ex
```

#### Example 2: Update Existing Project
```bash
# First, see what's different (set mode for cleaner output)
uv run cc_setup --target /path/to/existing-project --gitignore python --gitignore_compare_mode set
# Short form:
uv run cc_setup -t /path/to/existing-project -gi python -gic set

# Add missing patterns (keeps your custom rules)
uv run cc_setup --target /path/to/existing-project --gitignore python --gitignore_execute merge --execute
# Short form:
uv run cc_setup -t /path/to/existing-project -gi python -gix merge -ex
```

#### Example 3: Compare Reordered Files
```bash
# Set mode shows files are identical even if patterns are in different order
uv run cc_setup --target /path/to/project --gitignore python --gitignore_compare_mode set
# Short form:
uv run cc_setup -t /path/to/project -gi python -gic set

# Diff mode would show many differences due to order changes
uv run cc_setup --target /path/to/project --gitignore python --gitignore_compare_mode diff
# Short form:
uv run cc_setup -t /path/to/project -gi python -gic diff
```

#### Example 4: Switch Languages
```bash
# Check current .gitignore against C# template
uv run cc_setup --target /path/to/project --gitignore csharp
# Short form:
uv run cc_setup -t /path/to/project -gi csharp

# Replace with C# template
uv run cc_setup --target /path/to/project --gitignore csharp --gitignore_execute replace --execute
# Short form:
uv run cc_setup -t /path/to/project -gi csharp -gix replace -ex
```

#### Example 4: Restore from Backup
If you need to restore your original `.gitignore`:
```bash
cd /path/to/project
cp .gitignore.backup .gitignore
```

### Adding Custom Templates

To add your own language templates:

1. Create a new template file in `store/git/`:
   ```bash
   # Example: add JavaScript template
   touch store/git/.gitignore_javascript
   ```

2. Add ignore patterns to the file:
   ```gitignore
   # Node.js
   node_modules/
   npm-debug.log

   # Build output
   dist/
   build/
   ```

3. Use your new template:
   ```bash
   uv run cc_setup --target /path/to/project --gitignore javascript
   # Short form:
   uv run cc_setup -t /path/to/project -gi javascript
   ```


## Usage Examples

### Example 1: New Project Setup (Basic)

```bash
# First, do a dry run to see what will be copied
uv run cc_setup --target D:\projects\my-new-app --mode basic
# Short form:
uv run cc_setup -t D:\projects\my-new-app -m basic

# Review the output, then execute
uv run cc_setup --target D:\projects\my-new-app --mode basic --execute
# Short form:
uv run cc_setup -t D:\projects\my-new-app -m basic -ex
```

### Example 2: Upgrade to Isolated Worktrees

```bash
# Add isolated worktree support to an existing project
uv run cc_setup --target D:\projects\existing-app --mode iso --execute
# Short form:
uv run cc_setup -t D:\projects\existing-app -m iso -ex

# Use --overwrite if you want to replace existing artifacts
uv run cc_setup --target D:\projects\existing-app --mode iso --execute --overwrite
# Short form:
uv run cc_setup -t D:\projects\existing-app -m iso -ex -ov
```

### Example 3: Check Available Artifacts

```bash
# See detailed list of all artifacts
uv run cc_setup --help-artifacts
# Short form:
uv run cc_setup -ha
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

## Customizing Artifacts for Your Project

**IMPORTANT**: The artifacts in `store/basic/` and `store/iso/` are provided as **templates** that require customization for your specific project.

### After Deployment - Required Customization

Once you've deployed artifacts to your target project, you must customize them:

1. **Review `store/CUSTOMIZATION_GUIDE.md`** - Comprehensive guide with examples for different tech stacks
2. **Update Scripts** (`scripts/` directory):
   - `start.sh` - Set ports, directory paths, and start commands for your stack
   - `stop_apps.sh` - Configure ports to match your application
   - `reset_db.sh` - Customize for your database (or remove if not using a database)
   - `copy_dot_env.sh` - Update paths (or remove if not using .env files)
   - `expose_webhook.sh` - Configure tunnel provider (or remove if not needed)

3. **Update Commands** (`.claude/commands/` directory):
   - `install.md`, `start.md`, `prepare_app.md` - Update port numbers and paths
   - `bug.md`, `chore.md`, `feature.md`, `patch.md` - Set test commands for your stack
   - `test.md` - Replace example tests with your project's test suite
   - `test_e2e.md` - Update application URL
   - `conditional_docs.md` - Adjust paths to match your project structure

4. **Review Settings** (`.claude/settings.json`):
   - See `store/basic/SETTINGS_README.md` and `store/iso/SETTINGS_README.md`
   - Add/remove permissions for your technology stack
   - Keep: general tools (`mkdir`, `find`, `mv`, `cp`, `grep`, `ls`, `chmod`, `touch`, `Write`)
   - Optional: language-specific tools (`uv:*` for Python, `npm:*` for Node.js, `go:*`, `cargo:*`, `dotnet:*`, etc.)

### Common Customization Points

- **Directory Structure**: Replace `app/server`, `app/client` with your actual paths (e.g., `backend/`, `frontend/`, `src/`, etc.)
- **Port Numbers**: Update default ports (8000, 5173, 8001) to match your application
- **Technology Stack**: Replace example commands (Python/uv, TypeScript/Bun, npm) with your stack's commands
- **Database**: Customize database scripts or remove if not applicable
- **Environment Files**: Adjust .env patterns or remove if not using environment files
- **Webhooks**: Configure webhook infrastructure or remove if not needed

### Technology Stack Examples

The `store/CUSTOMIZATION_GUIDE.md` provides complete examples for:
- Python (FastAPI/Flask + React)
- Node.js (Express/NestJS)
- Go
- Rust
- C# / .NET
- Java/Maven
- Multi-language/Monorepo projects

### Managing Store Artifacts

The local store makes it easy to customize which artifacts are included:

**Adding Artifacts:**
1. Navigate to `store/basic/` or `store/iso/`
2. Add your file to the appropriate category folder (`hooks/`, `commands/`, `scripts/`, `adws/`)
3. The tool will automatically discover and include it

**Removing Artifacts:**
1. Delete the file from the store directory
2. The tool will no longer show or copy it

**Updating Artifacts:**
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
uv run cc_setup --help-artifacts
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
