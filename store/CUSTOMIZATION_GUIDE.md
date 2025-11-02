# Claude Code Artifacts Customization Guide

This guide explains how to customize the Claude Code artifacts for your specific project structure, technology stack, and requirements.

## Overview

The artifacts in `store/basic/` and `store/iso/` are provided as **templates** that need to be customized for your project. They contain placeholder values, example commands, and optional features that you should adapt to match your project's needs.

## Quick Customization Checklist

After deploying artifacts to your project, review and customize these key areas:

- [ ] **Scripts**: Update paths, ports, and commands in `scripts/` directory
- [ ] **Commands**: Customize test commands and directory paths in `.claude/commands/`
- [ ] **Settings**: Review and adjust permissions in `.claude/settings.json`
- [ ] **Environment**: Set up environment variables and configuration files

## Common Customization Points

### 1. Directory Structure

**Default placeholders used in artifacts:**
- Backend: `app/server/`, `backend/`, `src/server/`, `api/`
- Frontend: `app/client/`, `frontend/`, `src/client/`, `ui/`
- Database: `db/`, `database/`, `data/`

**How to customize:**
1. Search for directory path references in deployed artifacts
2. Replace with your actual project structure
3. Common locations to update:
   - `.claude/commands/bug.md`, `chore.md`, `feature.md`, `patch.md`
   - `.claude/commands/test.md`, `test_e2e.md`
   - `scripts/start.sh`, `scripts/reset_db.sh`

### 2. Port Numbers

**Default ports in templates:**
- Server: `8000` (configurable via `SERVER_PORT` variable)
- Client: `5173` (configurable via `CLIENT_PORT` variable)
- Webhook: `8001` (configurable via `WEBHOOK_PORT` variable)

**How to customize:**
1. Edit `scripts/start.sh` - update port variables at the top
2. Edit `scripts/stop_apps.sh` - update port list
3. Edit `.claude/commands/start.md` - update `PORT` variable
4. Edit `.claude/commands/test_e2e.md` - update `application_url` default

### 3. Technology Stack Commands

**Template provides examples for:**
- **Python**: `uv run pytest`, `uv run python -m py_compile`, `uv run ruff check`
- **JavaScript/Node.js**: `npm test`, `npm run dev`, `npm run build`
- **TypeScript/Bun**: `bun tsc --noEmit`, `bun run build`
- **Go**: `go test ./...`, `go build`
- **Rust**: `cargo test`, `cargo build`
- **C#/.NET**: `dotnet test`, `dotnet build`

**How to customize:**
1. Review `.claude/commands/test.md` - replace example commands with your stack
2. Update `.claude/commands/bug.md`, `chore.md`, `feature.md` - set test commands
3. Edit `scripts/start.sh` - replace backend/frontend start commands

**Example customization for a Node.js + React project:**

```bash
# In scripts/start.sh, replace:
# Backend start command
cd "$PROJECT_ROOT/backend"
npm start &  # Instead of: uv run python server.py

# Frontend start command
cd "$PROJECT_ROOT/frontend"
npm start &  # Instead of: npm run dev
```

### 4. Environment Files

**Default .env patterns:**
- Root `.env` file
- Backend `.env` at `app/server/.env`
- `.env.sample` templates

**How to customize:**
1. Edit `scripts/copy_dot_env.sh` - update source and destination paths
2. Update `.claude/commands/install.md` - document your .env structure
3. Adjust `.claude/settings.json` permissions if not using .env pattern

**If not using .env files:**
- Remove or skip `scripts/copy_dot_env.sh`
- Remove references from `.claude/commands/install.md`
- Remove `Bash(./scripts/copy_dot_env.sh:*)` from `.claude/settings.json`

### 5. Database Scripts (Optional)

**Default database setup:**
- SQLite database at `app/server/db/`
- Backup/restore via `scripts/reset_db.sh`

**How to customize:**
1. Edit `scripts/reset_db.sh` - update database paths and commands
2. Update backup/restore logic for your database (PostgreSQL, MySQL, MongoDB, etc.)
3. Modify `.claude/commands/prepare_app.md` - adjust database setup steps

**If not using a database:**
- Remove `scripts/reset_db.sh`
- Remove database references from `.claude/commands/install.md`
- Remove database reset from `.claude/commands/prepare_app.md`

### 6. Webhook Infrastructure (Optional)

**Default webhook setup:**
- Cloudflare tunnel via `scripts/expose_webhook.sh`
- Webhook server on port 8001
- GitHub webhook integration

**How to customize:**
1. Edit `scripts/expose_webhook.sh` - configure your tunnel provider (ngrok, Cloudflare, etc.)
2. Update environment variables in `.env`
3. Adjust `scripts/stop_apps.sh` - update webhook process names

**If not using webhooks:**
- Remove `scripts/expose_webhook.sh`
- Remove `scripts/kill_trigger_webhook.sh`
- Remove webhook references from `scripts/stop_apps.sh`
- Remove webhook mentions from `.claude/commands/install.md`

### 7. Test Commands

**How to customize test execution:**

Edit `.claude/commands/test.md` and replace the test sequence with your project's tests:

```markdown
## Test Execution Sequence

### Backend Tests

1. **Syntax Check**
   - Command: `<your-syntax-check-command>`
   - test_name: "backend_syntax_check"

2. **Code Quality**
   - Command: `<your-linting-command>`
   - test_name: "backend_linting"

3. **Unit Tests**
   - Command: `<your-test-command>`
   - test_name: "backend_tests"

### Frontend Tests (if applicable)

4. **Type Check**
   - Command: `<your-type-check-command>`
   - test_name: "frontend_type_check"

5. **Build**
   - Command: `<your-build-command>`
   - test_name: "frontend_build"
```

### 8. End-to-End Tests (Optional)

**Default E2E setup:**
- Playwright browser automation
- Application URL: `http://localhost:5173`
- Test files with step-by-step instructions

**How to customize:**
1. Edit `.claude/commands/test_e2e.md` - update `application_url` variable
2. Create test files matching your application's features
3. Adjust screenshot paths and test structure

**If not using E2E tests:**
- Remove or skip `.claude/commands/test_e2e.md`
- Remove `.claude/commands/resolve_failed_e2e_test.md`

## Technology Stack Examples

### Python Web Application (FastAPI/Flask + React)

**Directory structure:**
```
project/
├── backend/          # Python API
├── frontend/         # React app
├── scripts/          # Utility scripts
└── .claude/          # Claude Code config
```

**Key customizations:**
1. `scripts/start.sh`:
   ```bash
   SERVER_PORT=8000
   CLIENT_PORT=3000
   BACKEND_DIR="backend"
   FRONTEND_DIR="frontend"
   BACKEND_CMD="uvicorn main:app --reload"
   FRONTEND_CMD="npm start"
   ```

2. `.claude/commands/test.md`:
   ```bash
   # Backend: cd backend && pytest
   # Frontend: cd frontend && npm test
   ```

### Node.js Microservices

**Directory structure:**
```
project/
├── services/
│   ├── auth/
│   ├── api/
│   └── worker/
└── .claude/
```

**Key customizations:**
1. `scripts/start.sh`:
   ```bash
   # Start multiple services
   cd services/auth && npm start &
   cd services/api && npm start &
   cd services/worker && npm start &
   ```

2. `.claude/commands/test.md`:
   ```bash
   # Test all services: npm test --workspaces
   ```

### Go Application

**Directory structure:**
```
project/
├── cmd/
├── internal/
├── pkg/
└── .claude/
```

**Key customizations:**
1. `scripts/start.sh`:
   ```bash
   # Build and run Go application
   go build -o bin/app ./cmd/server
   ./bin/app &
   ```

2. `.claude/commands/test.md`:
   ```bash
   # Syntax: go build ./...
   # Tests: go test ./...
   # Lint: golangci-lint run
   ```

### Rust Project

**Directory structure:**
```
project/
├── src/
├── tests/
├── Cargo.toml
└── .claude/
```

**Key customizations:**
1. `scripts/start.sh`:
   ```bash
   # Build and run Rust application
   cargo run --release &
   ```

2. `.claude/commands/test.md`:
   ```bash
   # Syntax: cargo check
   # Tests: cargo test
   # Lint: cargo clippy
   ```

### C# / .NET Application

**Directory structure:**
```
project/
├── src/
├── tests/
├── Project.sln
└── .claude/
```

**Key customizations:**
1. `scripts/start.sh`:
   ```bash
   # Run .NET application
   cd src/WebApi
   dotnet run &
   ```

2. `.claude/commands/test.md`:
   ```bash
   # Build: dotnet build
   # Tests: dotnet test
   # Lint: dotnet format --verify-no-changes
   ```

## Settings Customization

### Permissions

Review `.claude/settings.json` permissions and adjust for your needs:

```json
{
  "permissions": {
    "allow": [
      "Bash(mkdir:*)",           // Keep for general use
      "Bash(uv:*)",              // Remove if not using Python/uv
      "Bash(npm:*)",             // Remove if not using npm
      "Bash(find:*)",            // Keep for general use
      "Bash(mv:*)",              // Keep for general use
      "Bash(grep:*)",            // Keep for general use
      "Bash(ls:*)",              // Keep for general use
      "Bash(cp:*)",              // Keep for general use
      "Write",                   // Keep for general use
      "Bash(chmod:*)",           // Keep for general use
      "Bash(touch:*)"            // Keep for general use
    ]
  }
}
```

**Add permissions for your stack:**
- Go: `"Bash(go:*)"`
- Rust: `"Bash(cargo:*)"`
- .NET: `"Bash(dotnet:*)"`
- Java: `"Bash(mvn:*)"`, `"Bash(gradle:*)"`

## ADW Customization

If using AI Developer Workflows (ADWs), review `.claude/adws/README.md` for:
- Environment variable requirements
- GitHub integration setup
- Workflow customization options

## Troubleshooting

### Scripts not executing
- Check file permissions: `chmod +x scripts/*.sh`
- Verify shebang line: `#!/bin/bash`
- Validate syntax: `bash -n scripts/script-name.sh`

### Commands not working
- Verify paths match your project structure
- Check that referenced files exist
- Update port numbers if conflicts occur

### Tests failing
- Ensure test commands match your project's test runner
- Verify dependencies are installed
- Check that paths to test directories are correct

## Best Practices

1. **Document your changes**: Add comments explaining customizations
2. **Keep templates**: Save original artifacts before heavy modification
3. **Version control**: Commit `.claude/` directory to track changes
4. **Test thoroughly**: Validate all scripts and commands after customization
5. **Iterate**: Start with basic customization, refine as needed

## Getting Help

- Review artifact comments for inline customization hints
- Check main README.md for deployment and usage guidance
- Consult Claude Code documentation for advanced features

## Next Steps

After customizing:
1. Test all scripts: `./scripts/start.sh`, `./scripts/stop_apps.sh`
2. Run commands: Try `/start`, `/test`, `/bug`, etc.
3. Validate tests: Ensure test suite runs correctly
4. Commit changes: Save your customized artifacts to version control
