# Settings Configuration Guide

The `settings.json` file contains Claude Code configuration for permissions and hooks.

## Customization

### Permissions

The `permissions.allow` array lists commands Claude Code can execute without prompting:

```json
"allow": [
  "Bash(mkdir:*)",      // Keep - general file operations
  "Bash(uv:*)",         // OPTIONAL - remove if not using Python/uv
  "Bash(npm:*)",        // OPTIONAL - remove if not using npm/Node.js
  "Bash(find:*)",       // Keep - general file operations
  "Bash(mv:*)",         // Keep - general file operations
  "Bash(grep:*)",       // Keep - general file operations
  "Bash(ls:*)",         // Keep - general file operations
  "Bash(cp:*)",         // Keep - general file operations
  "Write",              // Keep - file writing
  "Bash(./scripts/copy_dot_env.sh:*)", // OPTIONAL - remove if not using .env pattern
  "Bash(chmod:*)",      // Keep - file permissions
  "Bash(touch:*)"       // Keep - file creation
]
```

### Add Permissions for Your Stack

Add technology-specific permissions as needed:

- **Go**: `"Bash(go:*)"`
- **Rust**: `"Bash(cargo:*)"`
- **.NET**: `"Bash(dotnet:*)"`
- **Java/Maven**: `"Bash(mvn:*)"`, `"Bash(gradle:*)"`
- **Ruby**: `"Bash(bundle:*)"`, `"Bash(ruby:*)"`
- **PHP**: `"Bash(composer:*)"`

### Hooks

The hooks are technology-agnostic Python scripts that run at various points:

- `PreToolUse`: Before each tool execution
- `PostToolUse`: After each tool execution
- `Notification`: For system notifications
- `Stop`: When chat session stops
- `SubagentStop`: When subagent stops
- `PreCompact`: Before context compaction
- `UserPromptSubmit`: When user submits a prompt

These hooks are generic and don't need customization for different tech stacks.

## Example Customizations

### Minimal (No build tools)
```json
"permissions": {
  "allow": [
    "Bash(mkdir:*)",
    "Bash(find:*)",
    "Bash(mv:*)",
    "Bash(grep:*)",
    "Bash(ls:*)",
    "Bash(cp:*)",
    "Write",
    "Bash(chmod:*)",
    "Bash(touch:*)"
  ]
}
```

### Python Project
Keep `uv:*`, remove `npm:*`

### Node.js Project
Keep `npm:*`, remove `uv:*`

### Multi-language Project
Keep all language tools you use
