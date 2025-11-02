#!/usr/bin/env python3
"""Update README.md with gitignore documentation"""

# Read README
with open('README.md', 'r', encoding='utf-8') as f:
    content = f.read()

# Read gitignore section
with open('README_gitignore_section.md', 'r', encoding='utf-8') as f:
    gitignore_section = f.read()

# Insert GitIgnore section before 'Usage Examples'
if '## GitIgnore Management' not in content:
    content = content.replace('## Usage Examples', gitignore_section + '\n\n## Usage Examples')
    print("Added GitIgnore Management section")
else:
    print("GitIgnore Management section already exists")

# Update command-line options table
old_line = '| `--mode` | `-m` | Setup mode: `basic` or `iso` (required) |'
new_line = '| `--mode` | `-m` | Setup mode: `basic` or `iso` (required for artifact mode) |'
content = content.replace(old_line, new_line)

old_execute = '| `--execute` | `-e` | Actually copy files (default: dry-run) |'
new_execute = '| `--execute` | `-e` | Actually perform operations (default: dry-run) |'
content = content.replace(old_execute, new_execute)

# Add gitignore options after overwrite
overwrite_line = '| `--overwrite` | `-o` | Overwrite existing files (default: skip) |'
if '| `--gitignore`' not in content:
    gitignore_lines = '''| `--overwrite` | `-o` | Overwrite existing files (default: skip) |
| `--gitignore` | | Manage .gitignore for specified language (e.g., `python`, `csharp`) |
| `--gitignore_execute` | | GitIgnore operation: `compare`, `merge`, or `replace` (default: compare) |'''
    content = content.replace(overwrite_line, gitignore_lines)
    print("Added gitignore options to command-line table")
else:
    print("Gitignore options already in table")

# Write back
with open('README.md', 'w', encoding='utf-8') as f:
    f.write(content)

print('README.md updated successfully')
