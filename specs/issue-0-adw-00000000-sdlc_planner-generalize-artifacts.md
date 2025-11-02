# Chore: Generalize Claude Code Artifacts to Support All Project Types

## Metadata
issue_number: `N/A`
adw_id: `00000000`
issue_json: `{"title": "Make artifacts more general", "body": "Implement the recommendations of the preceding analysis that identified over-specialization in store/basic and store/iso artifacts"}`

## Chore Description

The Claude Code artifacts stored in `store/basic/` and `store/iso/` are currently over-specialized for a specific client-server web application architecture (Python backend + TypeScript/Bun frontend + SQLite database). This chore will refactor these artifacts to be generic and applicable to any coding project, removing hardcoded assumptions about:

- Project structure (app/server, app/client)
- Technology stack (Python/uv, Bun/TypeScript, npm)
- External dependencies (tac-5, tac-6 directories)
- Application-specific naming ("Natural Language SQL Interface")
- Infrastructure assumptions (Cloudflare, specific ports, databases)

## Relevant Files

### Scripts (8 files in basic, 10 in iso)

**store/basic/scripts/copy_dot_env.sh**
- Lines 4-18: Hardcoded paths to external `../tac-5/.env` and `app/server/.env`
- Action: Remove or make generic with configurable paths

**store/basic/scripts/reset_db.sh**
- Line 7: Hardcoded `app/server/db/backup.db` → `app/server/db/database.db`
- Action: Remove or make generic with configurable database paths

**store/basic/scripts/start.sh**
- Line 14: Application-specific name "Natural Language SQL Interface"
- Lines 4-5: Hardcoded ports 8000, 5173
- Line 41-48: Hardcoded `.env` path at `app/server/.env`
- Lines 69, 85: Hardcoded `app/server/` and `app/client/` directories
- Line 70: Python/uv-specific command `uv run python server.py`
- Line 86: npm-specific command `npm run dev`
- Action: Generalize or provide template/placeholder approach

**store/basic/scripts/stop_apps.sh**
- Line 9: Application-specific name
- Line 21: Hardcoded ports 5173, 8000, 8001
- Line 17: References specific `trigger_webhook.py`
- Action: Make port discovery dynamic or configurable

**store/basic/scripts/expose_webhook.sh**
- Lines 3-11: Cloudflare-specific infrastructure
- Action: Remove or make optional/generic

**store/basic/scripts/clear_issue_comments.sh**, **delete_pr.sh**, **kill_trigger_webhook.sh**
- Review for GitHub/webhook assumptions
- Action: Keep if generic, document requirements

**store/iso/scripts/** (same issues plus check_ports.sh, purge_tree.sh)
- Same issues as basic plus iso-specific scripts
- Action: Apply same generalizations

### Commands (22 in basic, 27 in iso)

**store/basic/commands/install.md**
- Lines 4-5: References `.env.sample`, `app/server/.env.sample`
- Line 14: Assumes FE/BE dependencies
- Line 15: External `tac-2` dependency
- Line 16: Database with `reset_db.sh`
- Line 25: "AFK Agent" mention
- Line 30: Cloudflare infrastructure
- Action: Remove technology-specific assumptions, make generic

**store/basic/commands/start.md**
- Line 5: Hardcoded port 5173
- Lines 15-17: Assumes `scripts/start.sh`
- Action: Use variables/placeholders

**store/basic/commands/prepare_app.md**
- Line 7: Hardcoded port 5173
- Lines 11-12: Database and client-server assumptions
- Action: Make conditional/generic

**store/basic/commands/bug.md**, **chore.md**, **feature.md**, **patch.md**
- Multiple references to `app/server/**` and `app/client/**`
- Technology-specific commands: `cd app/server && uv run pytest`
- Frontend commands: `cd app/client && bun tsc --noEmit`, `bun run build`
- Action: Replace with generic test command placeholders

**store/basic/commands/test.md**
- Lines 44, 50, 56: `app/server/` with Python/uv/pytest
- Lines 64, 70: `app/client/` with Bun/TypeScript
- Action: Provide template structure with placeholders

**store/basic/commands/test_e2e.md**
- Line 10: Hardcoded `http://localhost:5173`
- Line 32: References `prepare_app.md`
- Action: Use configurable URL variable

**store/basic/commands/resolve_failed_e2e_test.md**
- Dependencies on test_e2e.md
- Action: Ensure consistency with e2e generalization

**store/basic/commands/conditional_docs.md**
- Lines 20, 25-26: References `app/server`, `app/client`, `app/client/src/style.css`
- Action: Update to use generic path examples

**store/iso/commands/** (5 additional commands)
- cleanup_worktrees.md, install_worktree.md, health_check.md, track_agentic_kpis.md, in_loop_review.md
- Action: Review and generalize any architecture assumptions

### Settings Files

**store/basic/settings.json** and **store/iso/settings.json**
- Line 9: `Bash(npm:*)` - JavaScript-specific
- Line 13: `Bash(./scripts/copy_dot_env.sh:*)` - assumes .env pattern
- Action: Keep but document that these are examples

### ADWs (13 in basic, 15 in iso)

**store/basic/adws/adw_*.py**
- Review for hardcoded paths or technology assumptions
- Action: Ensure generalized or well-documented

## Step by Step Tasks

### Step 1: Create Generic Template Documentation
- Create a new file `store/CUSTOMIZATION_GUIDE.md` that explains:
  - How to customize scripts for different project structures
  - Placeholder variables users should replace
  - Common patterns for different tech stacks
  - Examples for Python, JavaScript, C#, Go, Rust projects

### Step 2: Generalize Scripts - Phase 1 (Environment Setup)
- **copy_dot_env.sh**:
  - Remove hardcoded `tac-5`/`tac-6` references
  - Add comments indicating where users should customize paths
  - Provide template structure with `# TODO: Customize these paths` markers
- **expose_webhook.sh**:
  - Add header comment explaining Cloudflare requirement
  - Note that this is optional infrastructure
  - Provide generic webhook tunnel alternative examples

### Step 3: Generalize Scripts - Phase 2 (Application Control)
- **start.sh**:
  - Replace "Natural Language SQL Interface" with generic "Application"
  - Replace hardcoded ports with variables at top of file (SERVER_PORT, CLIENT_PORT)
  - Replace hardcoded paths (`app/server`, `app/client`) with variables
  - Replace `uv run python server.py` with comment: `# TODO: Add your backend start command`
  - Replace `npm run dev` with comment: `# TODO: Add your frontend start command`
  - Add header documentation explaining customization points
- **stop_apps.sh**:
  - Replace application name with generic
  - Replace hardcoded ports with variables
  - Make webhook killing conditional/documented
- **reset_db.sh**:
  - Add header explaining this is for database-backed projects
  - Replace hardcoded paths with variables
  - Add comment: `# This script is for projects using databases. Customize or remove if not applicable.`

### Step 4: Generalize Commands - Phase 1 (Workflow Commands)
- **install.md**:
  - Remove references to external `tac-*` directories
  - Make .env setup conditional/generic
  - Replace FE/BE language with "dependencies"
  - Remove specific "AFK Agent" mentions or make generic
  - Make Cloudflare section optional/generic
- **start.md**, **prepare_app.md**:
  - Replace hardcoded port with variable `PORT` or `APPLICATION_PORT`
  - Make database reset conditional with note about database projects
  - Generalize server/client language

### Step 5: Generalize Commands - Phase 2 (Development Commands)
- **bug.md**, **chore.md**, **feature.md**, **patch.md**:
  - Replace `app/server/**` with `<backend_directory>/**` or generic `src/**`
  - Replace `app/client/**` with `<frontend_directory>/**` or generic `ui/**`
  - Replace specific test commands with generic templates:
    - `# Backend tests: <insert your backend test command>`
    - `# Frontend tests: <insert your frontend test command>`
  - Provide examples in comments for common stacks:
    ```
    # Examples:
    # Python: cd backend && uv run pytest
    # Node.js: cd backend && npm test
    # Go: go test ./...
    # Rust: cargo test
    ```

### Step 6: Generalize Commands - Phase 3 (Testing)
- **test.md**:
  - Replace hardcoded directory paths with placeholders
  - Replace technology-specific commands with generic test structure:
    - Syntax/compilation checks → `<language_syntax_check>`
    - Linting → `<code_quality_check>`
    - Unit tests → `<run_tests>`
  - Add commented examples for multiple tech stacks
  - Update JSON output structure to be technology-agnostic
- **test_e2e.md**:
  - Replace hardcoded `http://localhost:5173` with variable `application_url: $4 if provided, otherwise use <YOUR_APP_URL>`
  - Make `prepare_app.md` dependency conditional
  - Add note about Playwright being optional

### Step 7: Generalize Settings Files
- **settings.json** (both basic and iso):
  - Add comment header explaining customization
  - Note that `npm:*` permission is optional (remove if not using npm)
  - Note that `copy_dot_env.sh` is a template (customize or remove)
  - Keep structure but document flexibility

### Step 8: Review and Update ADWs
- Review all `adw_*.py` files in both basic and iso
- Check for hardcoded paths, technology assumptions
- If found, replace with configurable variables or environment checks
- Ensure ADW documentation (adws/README.md) explains customization

### Step 9: Update Conditional Documentation
- **conditional_docs.md**:
  - Replace `app/server` and `app/client` examples with generic examples:
    - `backend/`, `src/server/`, `api/`
    - `frontend/`, `src/client/`, `ui/`
  - Add note that paths are project-specific

### Step 10: Update Main README
- Add new section "Customizing Artifacts for Your Project"
- Explain that artifacts come with generic templates
- Point to `store/CUSTOMIZATION_GUIDE.md`
- List common customization points:
  - Directory structure variables
  - Port numbers
  - Technology-specific commands
  - Optional infrastructure (databases, webhooks, etc.)

### Step 11: Apply Changes to ISO Store
- Repeat Steps 2-9 for `store/iso/` directory
- Address iso-specific scripts (check_ports.sh, purge_tree.sh)
- Address iso-specific commands (cleanup_worktrees.md, etc.)
- Ensure worktree-specific features remain intact while being generalized

### Step 12: Validation
- Run validation commands to ensure no syntax errors introduced
- Test that template artifacts are still valid files
- Verify documentation is clear and actionable

## Validation Commands

Execute every command to validate the chore is complete with zero regressions.

- `find store/basic -type f -name "*.sh" -exec bash -n {} \;` - Validate all basic shell scripts have correct syntax
- `find store/iso -type f -name "*.sh" -exec bash -n {} \;` - Validate all iso shell scripts have correct syntax
- `find store/basic -type f -name "*.md" -exec wc -l {} \;` - Verify all basic markdown files exist and have content
- `find store/iso -type f -name "*.md" -exec wc -l {} \;` - Verify all iso markdown files exist and have content
- `python -m json.tool store/basic/settings.json > /dev/null` - Validate basic settings.json is valid JSON
- `python -m json.tool store/iso/settings.json > /dev/null` - Validate iso settings.json is valid JSON
- `grep -r "tac-[0-9]" store/basic/ store/iso/ || echo "No tac references found (good!)"` - Confirm no external tac directory references remain
- `grep -r "Natural Language SQL" store/basic/ store/iso/ || echo "No app-specific names found (good!)"` - Confirm application name removed
- `grep -ri "app/server\|app/client" store/basic/scripts/ store/iso/scripts/ || echo "No hardcoded paths in scripts (good!)"` - Confirm scripts are generalized
- `ls -la store/CUSTOMIZATION_GUIDE.md` - Verify customization guide was created

## Notes

### Key Principles for Generalization

1. **Use Variables Instead of Hardcoded Values**
   - Ports, paths, URLs should be defined as variables at the top of files
   - Makes customization obvious and centralized

2. **Provide Examples, Not Requirements**
   - Show examples for common tech stacks in comments
   - Don't assume any particular language or framework

3. **Make Infrastructure Optional**
   - Database scripts, webhooks, cloud services should be clearly marked as optional
   - Provide clear "remove if not applicable" guidance

4. **Use Placeholders for Project-Specific Values**
   - `<backend_directory>`, `<frontend_directory>`, `<YOUR_APP_URL>`
   - Makes it obvious what needs customization

5. **Document Customization Points**
   - Every artifact should have clear comments about what to customize
   - Main guide should provide comprehensive customization roadmap

### Backwards Compatibility

- Users who have already deployed these artifacts won't be affected
- New deployments will get generalized templates that require customization
- Consider creating a "quickstart" example that shows a complete setup for one tech stack

### Future Improvements

- Could create multiple "flavor" directories (python-web, node-web, go-api, etc.)
- Could add a configuration wizard to cc_setup.py that prompts for project details
- Could provide project type detection based on files present (package.json, requirements.txt, etc.)
