# cc_setup Command Usage

## Installation Complete!

The `cc_setup` command is now configured and ready to use.

## Usage Options

### Option 1: With `uv run` (No Installation Required)

From within the `cc_setup` directory, you can run:

```bash
# View help
uv run cc_setup --help

# View available artifacts
uv run cc_setup --help-artifacts

# Dry run (preview changes)
uv run cc_setup --target /path/to/project --mode basic

# Execute setup
uv run cc_setup --target /path/to/project --mode basic --execute

# GitIgnore management
uv run cc_setup --target /path/to/project --gitignore python
```

**Pros:**
- No installation needed
- Always uses the latest local version
- Good for development and testing

**Cons:**
- Must be run from the `cc_setup` directory
- Slightly longer command

### Option 2: Global Installation (Use from Anywhere)

Install `cc_setup` as a global tool:

```bash
# One-time installation
cd /path/to/cc_setup
uv tool install .

# Now use 'cc_setup' from any directory
cd ~
cc_setup --help
cc_setup --target /path/to/project --mode basic --execute
cc_setup --target /path/to/project --gitignore python
```

**Updating after changes:**
```bash
cd /path/to/cc_setup
uv tool install --force .
```

**Uninstall:**
```bash
uv tool uninstall cc_setup
```

**Pros:**
- Use from any directory
- Shorter command (`cc_setup` vs `uv run cc_setup`)
- System-wide availability

**Cons:**
- Requires manual update after code changes
- Uses a snapshot of the code at install time

## Quick Examples

### Setup a new project with basic mode
```bash
uv run cc_setup --target ../my-project --mode basic --execute
```

### Setup with isolated worktree support
```bash
uv run cc_setup --target ../my-project --mode iso --execute
```

### Manage Python project .gitignore
```bash
# Compare your .gitignore with template
uv run cc_setup --target ../my-project --gitignore python

# Merge missing patterns
uv run cc_setup --target ../my-project --gitignore python --gitignore_execute merge --execute
```

### View all available artifacts
```bash
uv run cc_setup --help-artifacts
```

## Recommendation

- **For development**: Use `uv run cc_setup` (Option 1)
- **For regular use**: Install globally with `uv tool install .` (Option 2)
