# Basic Template Recommendation

**Last Updated:** 2025-10-31

## Overview

This recommendation provides a basic, generally-useful set of Claude Code artifacts without over-specialized functionality for users who want a solid foundation for their projects.

## Recommended Source

**Primary Source:** `tac-6` or `tac-7`

### Why tac-6 or tac-7?
- Mature feature set without over-specialization
- tac-7 adds isolated worktree management (skip if you don't need it)
- tac-8 sub-projects are too specialized (Notion integration, multi-agent systems, etc.)
- tac-1 to tac-5 are too basic or still evolving

---

## Settings File

**Source:** `tac-6` or `tac-7/.claude/settings.json` (Version 5)

**Features:**
- Permissions management for bash commands
- Hooks system with 4 automation points:
  - PreToolUse (dangerous command detection)
  - CompletionStreaming (TTS notifications)
  - PreCompact (context compaction logging)
  - UserPromptSubmit (prompt logging)
- Good balance of automation without over-specialization

**File:** `.claude/settings.json`

---

## Hooks

**Source:** `tac-6` or `tac-7/.claude/hooks/`

### Recommended Hooks (5 total)

1. **`dangerous_command.py`** (Version 5)
   - **Purpose:** Security - blocks dangerous commands like `rm -rf`, force pushes
   - **When it runs:** PreToolUse hook
   - **Why include:** Essential security feature

2. **`notification.py`** (Version 5)
   - **Purpose:** UX - Text-to-speech completion notifications
   - **When it runs:** CompletionStreaming hook
   - **Why include:** Helpful for long-running tasks

3. **`env_protection.py`** (Version 5)
   - **Purpose:** Security - prevents committing .env files
   - **When it runs:** PreToolUse hook (git commits)
   - **Why include:** Prevents credential leaks

4. **`pre_compact.py`** (Version 5)
   - **Purpose:** Observability - logs when context compaction happens
   - **When it runs:** PreCompact hook
   - **Why include:** Useful for debugging context issues

5. **`user_prompt_submit.py`** (Version 5)
   - **Purpose:** Observability - logs user prompts
   - **When it runs:** UserPromptSubmit hook
   - **Why include:** Helps track what you asked Claude to do

### Hooks to Skip
- `session_start.py` - Too specialized
- `multi_agent_*.py` - Too specialized for multi-agent systems
- Notion-related hooks - Too specialized

**Directory:** `.claude/hooks/`

---

## Slash Commands

**Source:** `tac-6` or `tac-7/.claude/commands/`

### Essential Workflow Commands (7)

1. **`install.md`** (Version 5 from tac-6/7)
   - Install project dependencies
   - **Use case:** Initial setup

2. **`prime.md`** (Version 3 from tac-6/7)
   - Project initialization/setup
   - **Use case:** First-time project configuration

3. **`bug.md`** (Version 4 from tac-6/7)
   - Bug fixing workflow
   - **Use case:** Bug fixes

4. **`chore.md`** (Version 4 from tac-6/7)
   - Chore/maintenance workflow
   - **Use case:** Refactoring, dependency updates

5. **`feature.md`** (Version 3 from tac-6/7)
   - Feature development workflow
   - **Use case:** New features

6. **`implement.md`** (Version 1 from tac-6/7)
   - General implementation workflow
   - **Use case:** Implementing planned changes

7. **`start.md`** (Version 3 from tac-7)
   - Start development services
   - **Use case:** Daily development startup

### Useful Utilities (6)

8. **`tools.md`** (Version 1)
   - List available tools
   - **Use case:** Discovery

9. **`commit.md`** (Version 2 from tac-7)
   - Commit helper with best practices
   - **Use case:** Creating commits

10. **`pull_request.md`** (Version 2 from tac-7)
    - PR creation helper
    - **Use case:** Creating pull requests

11. **`review.md`** (Version 1 from tac-6)
    - Code review workflow
    - **Use case:** Reviewing code changes

12. **`document.md`** (Version 1 from tac-6)
    - Documentation generation
    - **Use case:** Generating/updating docs

13. **`patch.md`** (Version 1 from tac-6)
    - Quick patch workflow
    - **Use case:** Small fixes

### Commands to Skip
- `classify_adw.md` - Too specialized for ADW management
- `classify_issue.md` - Too specialized
- `cleanup_worktrees.md` - Only needed if using worktrees
- `install_worktree.md` - Only needed if using worktrees
- `health_check.md` - Too specialized
- `track_agentic_kpis.md` - Too specialized
- Test resolution commands - Can be added later if needed
- Multi-agent task commands - Too specialized

**Directory:** `.claude/commands/`

---

## Scripts

**Source:** `tac-6` or `tac-7/scripts/`

### Essential Utilities (6)

1. **`start.sh`** (Version 2 from tac-6/7)
   - Start development services with port management
   - Kills existing processes on ports before starting
   - **Use case:** Daily development

2. **`stop_apps.sh`** (Version 2 from tac-6)
   - Stop all running services
   - Kills webhook server and port processes
   - **Use case:** Clean shutdown

3. **`copy_dot_env.sh`** (Version 2 from tac-6/7)
   - Copy environment configuration from reference project
   - **Use case:** Environment setup

4. **`clear_issue_comments.sh`** (Version 2 from tac-6/7)
   - Clear all comments from a GitHub issue
   - Auto-confirms (no prompt)
   - **Use case:** GitHub cleanup

5. **`delete_pr.sh`** (Version 1 from tac-6/7)
   - Delete pull request with optional branch deletion
   - **Use case:** PR cleanup

6. **`reset_db.sh`** (Version 1 from tac-6/7)
   - Reset database to backup state
   - **Use case:** Database development

### Scripts to Skip
- `expose_webhook.sh` - Only if you use webhooks
- `kill_trigger_webhook.sh` - Only if you use webhooks
- `purge_tree.sh` - Worktree-specific
- `check_ports.sh` - Worktree-specific
- `prune_worktrees.sh` - Worktree-specific
- System-specific scripts (reset-system, start-system, etc.) - Too specialized

**Directory:** `scripts/`

---

## ADWs (Optional)

**Source:** `tac-6/.claude/adws/`

Only include if you want to use automated multi-agent workflows. Start with the basic (non-isolated) versions.

### Basic ADWs (4)

1. **`adw_plan.py`** (Version 1 from tac-6)
   - 274 lines - Planning workflow
   - **Use case:** Agentic planning

2. **`adw_build.py`** (Version 1 from tac-6)
   - 242 lines - Build workflow
   - **Use case:** Agentic building

3. **`adw_test.py`** (Version 1 from tac-6)
   - 1106 lines - Testing workflow
   - **Use case:** Comprehensive testing

4. **`adw_patch.py`** (Version 1 from tac-6)
   - 326 lines - Quick patch workflow
   - **Use case:** Single-issue patches

### ADWs to Skip
- All `*_iso.py` variants - Require isolated worktree setup
- SDLC workflows (`adw_sdlc.py`) - Too comprehensive for starting out
- Compositional workflows (`adw_plan_build.py`, etc.) - Can add later
- Notion-specific ADWs - Too specialized
- Task management ADWs - Too specialized

**Directory:** `.claude/adws/` (optional)

---

## File Structure

```
project/
├── .claude/
│   ├── commands/           # 13 slash commands
│   │   ├── install.md
│   │   ├── prime.md
│   │   ├── bug.md
│   │   ├── chore.md
│   │   ├── feature.md
│   │   ├── implement.md
│   │   ├── start.md
│   │   ├── tools.md
│   │   ├── commit.md
│   │   ├── pull_request.md
│   │   ├── review.md
│   │   ├── document.md
│   │   └── patch.md
│   │
│   ├── hooks/              # 5 hooks
│   │   ├── dangerous_command.py
│   │   ├── notification.py
│   │   ├── env_protection.py
│   │   ├── pre_compact.py
│   │   └── user_prompt_submit.py
│   │
│   ├── adws/               # Optional: 4 ADWs
│   │   ├── adw_plan.py
│   │   ├── adw_build.py
│   │   ├── adw_test.py
│   │   └── adw_patch.py
│   │
│   └── settings.json       # Settings with hooks config
│
└── scripts/                # 6 utility scripts
    ├── start.sh
    ├── stop_apps.sh
    ├── copy_dot_env.sh
    ├── clear_issue_comments.sh
    ├── delete_pr.sh
    └── reset_db.sh
```

---

## Implementation Steps

1. **Create directory structure:**
   ```bash
   mkdir -p my-project/.claude/{commands,hooks,adws}
   mkdir -p my-project/scripts
   ```

2. **Copy settings:**
   ```bash
   cp tac-6/.claude/settings.json my-project/.claude/
   ```

3. **Copy hooks:**
   ```bash
   cd tac-6/.claude/hooks
   cp dangerous_command.py notification.py env_protection.py pre_compact.py user_prompt_submit.py \
      my-project/.claude/hooks/
   ```

4. **Copy commands:**
   ```bash
   cd tac-6/.claude/commands
   cp install.md prime.md bug.md chore.md feature.md implement.md start.md \
      tools.md commit.md pull_request.md review.md document.md patch.md \
      my-project/.claude/commands/
   ```

5. **Copy scripts:**
   ```bash
   cd tac-6/scripts
   cp start.sh stop_apps.sh copy_dot_env.sh clear_issue_comments.sh delete_pr.sh reset_db.sh \
      my-project/scripts/
   chmod +x my-project/scripts/*.sh
   ```

6. **Copy ADWs (optional):**
   ```bash
   cd tac-6/.claude/adws
   cp adw_plan.py adw_build.py adw_test.py adw_patch.py \
      my-project/.claude/adws/
   ```

---

## Customization Notes

### After copying, customize for your project:

1. **Scripts:**
   - Update port numbers in `start.sh` and `stop_apps.sh`
   - Update paths in `copy_dot_env.sh`
   - Modify database paths in `reset_db.sh`

2. **Settings:**
   - Add/remove bash commands in permissions based on your needs
   - Adjust hook configurations

3. **Commands:**
   - Customize workflows to match your development process
   - Add project-specific instructions

4. **Hooks:**
   - Adjust notification settings (TTS voice, etc.)
   - Customize dangerous command patterns

---

## Next Steps

Once you have this basic template working:

1. **Add more as needed:**
   - Testing commands (`test.md`, `test_e2e.md`)
   - More specialized workflows
   - Project-specific commands

2. **Consider upgrading:**
   - Add isolated worktree management from tac-7
   - Add compositional ADWs for complex workflows
   - Add observability hooks for multi-agent scenarios

3. **Version control:**
   - Commit your `.claude/` directory
   - Document your customizations
   - Track what works for your team

---

## Summary

This basic template provides:
- ✅ Security features (dangerous command blocking, .env protection)
- ✅ Development workflows (bug, feature, chore, patch)
- ✅ Useful utilities (commit, PR, review, documentation)
- ✅ Observability (logging, notifications)
- ✅ Automation (optional ADWs)
- ❌ No over-specialized features
- ❌ No complex worktree management
- ❌ No external integrations (Notion, etc.)

**Total files:** ~24-28 files (depending on whether you include ADWs)

**Source projects:** Primarily `tac-6`, with some Version 2 files from `tac-7`
