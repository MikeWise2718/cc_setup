## GitIgnore Management

In addition to managing Claude Code artifacts, cc_setup can manage your project's `.gitignore` file using language-specific templates stored in `store/git/`.

### Available Operations

#### Compare (Default)
Shows a unified diff between your project's `.gitignore` and the template:

```bash
uv run cc_setup.py --target /path/to/project --gitignore python
```

Output shows:
- Lines that would be added (green, + prefix)
- Lines in your file but not in template (red, - prefix)
- Context lines for reference

#### Merge
Adds missing patterns from the template while preserving all existing entries:

```bash
# Preview what will be added (dry-run)
uv run cc_setup.py --target /path/to/project --gitignore python --gitignore_execute merge

# Execute merge
uv run cc_setup.py --target /path/to/project --gitignore python --gitignore_execute merge --execute
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
uv run cc_setup.py --target /path/to/project --gitignore csharp --gitignore_execute replace

# Execute replacement
uv run cc_setup.py --target /path/to/project --gitignore csharp --gitignore_execute replace --execute
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
uv run cc_setup.py --target /path/to/new-python-project --gitignore python --gitignore_execute replace --execute
```

#### Example 2: Update Existing Project
```bash
# First, see what's different
uv run cc_setup.py --target /path/to/existing-project --gitignore python

# Add missing patterns (keeps your custom rules)
uv run cc_setup.py --target /path/to/existing-project --gitignore python --gitignore_execute merge --execute
```

#### Example 3: Switch Languages
```bash
# Check current .gitignore against C# template
uv run cc_setup.py --target /path/to/project --gitignore csharp

# Replace with C# template
uv run cc_setup.py --target /path/to/project --gitignore csharp --gitignore_execute replace --execute
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
   uv run cc_setup.py --target /path/to/project --gitignore javascript
   ```
