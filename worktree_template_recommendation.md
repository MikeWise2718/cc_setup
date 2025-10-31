# Worktree Template Recommendation

**Last Updated:** 2025-10-31

## Overview

This recommendation provides a configuration for users who want to use **isolated worktree management** for parallel development workflows. This is more advanced than the basic template and enables running multiple AI agents in parallel, each in their own isolated git worktree.

## Recommended Source

**Primary Source:** `tac-7`

### Why tac-7?
- Full isolated worktree management system
- Complete set of `*_iso` ADW workflows
- Worktree utility commands and scripts
- Mature implementation without external dependencies
- Proven in production across multiple projects

### Why NOT tac-8?
- tac-8 sub-projects add specialized features (Notion, multi-agent task boards, etc.)
- Unless you need those specific integrations, tac-7 is cleaner

---

## Settings File

**Source:** `tac-7/.claude/settings.json` (Version 5)

**Features:**
- Permissions management for bash commands
- Hooks system with 4 automation points:
  - PreToolUse (dangerous command detection)
  - CompletionStreaming (TTS notifications)
  - PreCompact (context compaction logging)
  - UserPromptSubmit (prompt logging)
- All permissions needed for worktree operations

**File:** `.claude/settings.json`

---

## Hooks

**Source:** `tac-7/.claude/hooks/`

### Recommended Hooks (5 total)

1. **`dangerous_command.py`** (Version 5)
   - **Purpose:** Security - blocks dangerous commands
   - **Worktree relevance:** Critical when managing multiple worktrees

2. **`notification.py`** (Version 5)
   - **Purpose:** TTS notifications when agent completes
   - **Worktree relevance:** Essential for parallel workflows

3. **`env_protection.py`** (Version 5)
   - **Purpose:** Prevents committing .env files
   - **Worktree relevance:** Important across all worktrees

4. **`pre_compact.py`** (Version 5)
   - **Purpose:** Logs context compaction
   - **Worktree relevance:** Helps track agent context usage

5. **`user_prompt_submit.py`** (Version 5)
   - **Purpose:** Logs user prompts
   - **Worktree relevance:** Tracks which prompts went to which worktree

**Directory:** `.claude/hooks/`

---

## Slash Commands

**Source:** `tac-7/.claude/commands/`

### Essential Workflow Commands (7)

1. **`install.md`** (Version 5)
   - Install project dependencies

2. **`prime.md`** (Version 3)
   - Project initialization

3. **`bug.md`** (Version 4)
   - Bug fixing workflow

4. **`chore.md`** (Version 4)
   - Chore/maintenance workflow

5. **`feature.md`** (Version 3)
   - Feature development workflow

6. **`implement.md`** (Version 1)
   - General implementation

7. **`start.md`** (Version 3)
   - Start services

### Worktree Management Commands (4) ⭐ NEW

8. **`cleanup_worktrees.md`** (Version 1) ⭐
   - Clean up isolated ADW worktrees
   - Actions: all, specific, list
   - **Use case:** Maintenance and cleanup

9. **`install_worktree.md`** (Version 1) ⭐
   - Set up isolated worktree with custom ports
   - **Use case:** Initialize worktree environment

10. **`init_worktree.md`** (Version 1) ⭐
    - Create new git worktree with sparse checkout
    - **Use case:** Create isolated workspace

11. **`clean_worktree.md`** (Version 1) ⭐
    - Remove git worktree and branch
    - **Use case:** Delete single worktree

### Useful Utilities (6)

12. **`tools.md`** (Version 1)
    - List available tools

13. **`commit.md`** (Version 2)
    - Commit helper

14. **`pull_request.md`** (Version 2)
    - PR creation

15. **`review.md`** (Version 1)
    - Code review

16. **`document.md`** (Version 1)
    - Documentation generation

17. **`patch.md`** (Version 1)
    - Quick patches

### Development Commands (Optional but Useful)

18. **`test.md`** (Version 1)
    - Run tests

19. **`test_e2e.md`** (Version 3)
    - Run E2E tests

20. **`health_check.md`** (Version 1)
    - Check worktree health

21. **`track_agentic_kpis.md`** (Version 1)
    - Track agent performance metrics

### Commands to Skip
- Task management commands (only if you're using multi-agent task boards)
- Notion-specific commands
- Project-specific planning commands

**Total Commands:** ~17-21 commands

**Directory:** `.claude/commands/`

---

## Scripts

**Source:** `tac-7/scripts/`

### Essential Development Scripts (6)

1. **`start.sh`** (Version 2)
   - Start services with port management
   - Kills existing processes before starting

2. **`stop_apps.sh`** (Version 3) ⭐
   - Stop all services including isolated ADW services
   - Kills processes on ports 9100-9114 (backend), 9200-9214 (frontend)
   - **Worktree relevance:** Essential for managing parallel services

3. **`copy_dot_env.sh`** (Version 2)
   - Copy environment configuration

4. **`clear_issue_comments.sh`** (Version 2)
   - Clear GitHub issue comments

5. **`delete_pr.sh`** (Version 1)
   - Delete pull requests

6. **`reset_db.sh`** (Version 1)
   - Reset database

### Worktree-Specific Scripts (2) ⭐ NEW

7. **`check_ports.sh`** (Version 1) ⭐
   - Check which ports are in use
   - Shows main ports (5173, 8000, 8001)
   - Shows ADW backend ports (9100-9114)
   - Shows ADW frontend ports (9200-9214)
   - **Use case:** Debug port conflicts in parallel workflows

8. **`purge_tree.sh`** (Version 1) ⭐
   - Comprehensive worktree cleanup
   - Removes all worktrees, branches, and processes
   - **Use case:** Nuclear option to reset everything

### Scripts to Skip
- Webhook scripts (unless you use webhooks)
- System-specific scripts from tac-8

**Total Scripts:** 8 scripts

**Directory:** `scripts/`

---

## ADWs - Isolated Versions ⭐

**Source:** `tac-7/.claude/adws/`

### Core Isolated Workflows (4)

1. **`adw_plan_iso.py`** (Version 1) ⭐
   - 338 lines - Planning in isolated worktrees
   - Sparse checkout support
   - **Use case:** Plan features in isolation

2. **`adw_build_iso.py`** (Version 1) ⭐
   - 253 lines - Build in isolated worktrees
   - Custom port configuration
   - **Use case:** Build features in parallel

3. **`adw_test_iso.py`** (Version 1) ⭐
   - 882 lines - Testing in isolated worktrees
   - Comprehensive test suite
   - **Use case:** Run tests in isolation

4. **`adw_review_iso.py`** (Version 1) ⭐
   - 535 lines - Review in isolated worktrees
   - **Use case:** Review changes in isolation

### Compositional Isolated Workflows (6)

5. **`adw_plan_build_iso.py`** (Version 1) ⭐
   - 82 lines - Plan + Build workflow
   - **Use case:** Quick feature implementation

6. **`adw_plan_build_test_iso.py`** (Version 1) ⭐
   - 107 lines - Plan + Build + Test workflow
   - Optional: skip E2E tests
   - **Use case:** Complete feature with tests

7. **`adw_plan_build_review_iso.py`** (Version 1) ⭐
   - 107 lines - Plan + Build + Review workflow
   - Optional: skip resolution
   - **Use case:** Feature with review

8. **`adw_plan_build_test_review_iso.py`** (Version 1) ⭐
   - 132 lines - Complete SDLC workflow
   - **Use case:** Full development cycle

9. **`adw_plan_build_document_iso.py`** (Version 1) ⭐
   - 99 lines - Plan + Build + Document workflow
   - **Use case:** Feature with docs

10. **`adw_patch_iso.py`** (Version 1) ⭐
    - 432 lines - Quick patches in isolation
    - **Use case:** Bug fixes

### Advanced Workflows (3)

11. **`adw_sdlc_iso.py`** (Version 1) ⭐
    - 152 lines - Complete SDLC with isolation
    - **Use case:** Production-ready workflow

12. **`adw_sdlc_zte_iso.py`** (Version 1) ⭐
    - 238 lines - Zero Touch Execution SDLC
    - Automatic shipping
    - **Use case:** Fully automated deployment

13. **`adw_ship_iso.py`** (Version 1) ⭐
    - 317 lines - Ship (merge) to main
    - **Use case:** Deploy completed work

14. **`adw_document_iso.py`** (Version 1) ⭐
    - 519 lines - Documentation generation
    - **Use case:** Comprehensive docs

**Total ADWs:** 14 isolated workflows

**Directory:** `.claude/adws/`

---

## File Structure

```
project/
├── .claude/
│   ├── commands/           # 17-21 slash commands
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
│   │   ├── patch.md
│   │   ├── cleanup_worktrees.md    ⭐ Worktree
│   │   ├── install_worktree.md     ⭐ Worktree
│   │   ├── init_worktree.md        ⭐ Worktree
│   │   ├── clean_worktree.md       ⭐ Worktree
│   │   ├── test.md                 (optional)
│   │   ├── test_e2e.md             (optional)
│   │   ├── health_check.md         (optional)
│   │   └── track_agentic_kpis.md   (optional)
│   │
│   ├── hooks/              # 5 hooks
│   │   ├── dangerous_command.py
│   │   ├── notification.py
│   │   ├── env_protection.py
│   │   ├── pre_compact.py
│   │   └── user_prompt_submit.py
│   │
│   ├── adws/               # 14 isolated ADWs ⭐
│   │   ├── adw_plan_iso.py
│   │   ├── adw_build_iso.py
│   │   ├── adw_test_iso.py
│   │   ├── adw_review_iso.py
│   │   ├── adw_plan_build_iso.py
│   │   ├── adw_plan_build_test_iso.py
│   │   ├── adw_plan_build_review_iso.py
│   │   ├── adw_plan_build_test_review_iso.py
│   │   ├── adw_plan_build_document_iso.py
│   │   ├── adw_patch_iso.py
│   │   ├── adw_sdlc_iso.py
│   │   ├── adw_sdlc_zte_iso.py
│   │   ├── adw_ship_iso.py
│   │   └── adw_document_iso.py
│   │
│   └── settings.json       # Settings with hooks config
│
├── scripts/                # 8 utility scripts
│   ├── start.sh
│   ├── stop_apps.sh         ⭐ Enhanced for worktrees
│   ├── copy_dot_env.sh
│   ├── clear_issue_comments.sh
│   ├── delete_pr.sh
│   ├── reset_db.sh
│   ├── check_ports.sh       ⭐ Worktree
│   └── purge_tree.sh        ⭐ Worktree
│
└── trees/                  # Worktree directory (auto-created)
    ├── worktree-1/
    ├── worktree-2/
    └── ...
```

---

## Port Management

### Main Application Ports
- **5173** - Frontend (Vite)
- **8000** - Backend (main)
- **8001** - Webhook server (optional)

### Isolated ADW Backend Ports ⭐
- **9100-9114** - 15 isolated backend instances
- Each worktree gets a unique backend port

### Isolated ADW Frontend Ports ⭐
- **9200-9214** - 15 isolated frontend instances
- Each worktree gets a unique frontend port

**Total capacity:** 15 parallel isolated workflows

---

## Implementation Steps

### 1. Create Directory Structure

```bash
mkdir -p my-project/.claude/{commands,hooks,adws}
mkdir -p my-project/scripts
mkdir -p my-project/trees  # Worktree directory
```

### 2. Copy Settings

```bash
cp tac-7/.claude/settings.json my-project/.claude/
```

### 3. Copy Hooks

```bash
cd tac-7/.claude/hooks
cp dangerous_command.py notification.py env_protection.py \
   pre_compact.py user_prompt_submit.py \
   my-project/.claude/hooks/
```

### 4. Copy Commands (Core + Worktree)

```bash
cd tac-7/.claude/commands

# Core commands
cp install.md prime.md bug.md chore.md feature.md implement.md start.md \
   tools.md commit.md pull_request.md review.md document.md patch.md \
   my-project/.claude/commands/

# Worktree management commands ⭐
cp cleanup_worktrees.md install_worktree.md init_worktree.md clean_worktree.md \
   my-project/.claude/commands/

# Optional: testing and monitoring
cp test.md test_e2e.md health_check.md track_agentic_kpis.md \
   my-project/.claude/commands/
```

### 5. Copy Scripts (Core + Worktree)

```bash
cd tac-7/scripts

# Core scripts
cp start.sh stop_apps.sh copy_dot_env.sh clear_issue_comments.sh \
   delete_pr.sh reset_db.sh \
   my-project/scripts/

# Worktree scripts ⭐
cp check_ports.sh purge_tree.sh \
   my-project/scripts/

chmod +x my-project/scripts/*.sh
```

### 6. Copy Isolated ADWs ⭐

```bash
cd tac-7/.claude/adws

# Core isolated workflows
cp adw_plan_iso.py adw_build_iso.py adw_test_iso.py adw_review_iso.py \
   my-project/.claude/adws/

# Compositional workflows
cp adw_plan_build_iso.py adw_plan_build_test_iso.py \
   adw_plan_build_review_iso.py adw_plan_build_test_review_iso.py \
   adw_plan_build_document_iso.py adw_patch_iso.py \
   my-project/.claude/adws/

# Advanced workflows
cp adw_sdlc_iso.py adw_sdlc_zte_iso.py adw_ship_iso.py adw_document_iso.py \
   my-project/.claude/adws/
```

---

## Usage Patterns

### Basic Worktree Workflow

1. **Initialize a worktree:**
   ```
   /init_worktree feature-auth-system app/server
   ```

2. **Install dependencies in worktree:**
   ```
   /install_worktree trees/feature-auth-system 9100
   ```

3. **Run ADW workflow:**
   ```
   uv run .claude/adws/adw_plan_build_iso.py <issue-number>
   ```

4. **Clean up when done:**
   ```
   /clean_worktree feature-auth-system
   ```

### Parallel Development

1. **Create multiple worktrees:**
   ```
   /init_worktree feature-a app/client
   /init_worktree feature-b app/server
   /init_worktree bugfix-c app/utils
   ```

2. **Run parallel ADWs:**
   - Each gets isolated ports (9100/9200, 9101/9201, 9102/9202)
   - No conflicts between agents

3. **Monitor ports:**
   ```bash
   ./scripts/check_ports.sh
   ```

4. **Clean up all:**
   ```
   /cleanup_worktrees all
   ```

### Emergency Reset

If things get messy:
```bash
./scripts/purge_tree.sh
```

This will:
- Stop all processes on all ports
- Remove all worktrees
- Delete all worktree branches
- Clean git worktree list

---

## Customization Notes

### Port Configuration

Edit ADW files to adjust port ranges:
- Backend: `9100-9114` (15 slots)
- Frontend: `9200-9214` (15 slots)

If you need more parallel workflows, extend the ranges.

### Sparse Checkout

The `init_worktree` command uses sparse checkout to only include specific directories. Customize based on your monorepo structure:
- Full checkout: Remove sparse checkout logic
- Specific paths: Modify the paths in `init_worktree.md`

### ADW Customization

Each isolated ADW has configuration for:
- Issue tracking integration (GitHub)
- Port assignment logic
- Cleanup behavior
- Merge strategies

Review and customize based on your workflow.

---

## Key Differences from Basic Template

| Feature | Basic Template | Worktree Template |
|---------|---------------|-------------------|
| **Parallel workflows** | ❌ Single context | ✅ 15 parallel contexts |
| **Git worktrees** | ❌ Not used | ✅ Full support |
| **Port management** | ❌ Fixed ports | ✅ Dynamic port assignment |
| **ADW isolation** | ❌ Regular ADWs | ✅ Isolated ADWs |
| **Cleanup tools** | ❌ Basic | ✅ Comprehensive |
| **Commands** | 13 | 17-21 |
| **Scripts** | 6 | 8 |
| **ADWs** | 4 basic | 14 isolated |
| **Complexity** | Low | Medium-High |
| **Use case** | Single-agent | Multi-agent parallel |

---

## Prerequisites

### Required Tools
- **Git 2.5+** - For worktree support
- **uv** - Python package manager
- **gh** - GitHub CLI
- **lsof** - Port checking (usually pre-installed)

### Project Requirements
- Git repository
- GitHub integration
- Support for running on multiple ports

### Knowledge Requirements
- Understanding of git worktrees
- Comfortable with parallel development
- Able to debug port conflicts

---

## Advantages of Worktree Template

1. **Parallel Development:**
   - Run 15 AI agents simultaneously
   - Each in isolated environment
   - No context contamination

2. **Clean Separation:**
   - Each feature in own worktree
   - Independent git history
   - Separate process spaces

3. **Port Management:**
   - Automatic port assignment
   - Easy monitoring with `check_ports.sh`
   - Comprehensive cleanup

4. **Production-Ready:**
   - Proven across tac-7 projects
   - Battle-tested workflows
   - Comprehensive error handling

5. **Scalability:**
   - Handle complex projects
   - Multiple features in parallel
   - Team collaboration ready

---

## Disadvantages vs Basic Template

1. **Complexity:**
   - More moving parts
   - Requires git worktree knowledge
   - More things to debug

2. **Resource Usage:**
   - Multiple processes running
   - More disk space (multiple worktrees)
   - More memory consumption

3. **Learning Curve:**
   - Understanding worktree concepts
   - Managing multiple contexts
   - Cleanup procedures

4. **Overkill for Simple Projects:**
   - If you don't need parallel workflows
   - If project is small
   - If single-agent workflow is sufficient

---

## When to Use Worktree Template

✅ **Use this template if:**
- You need parallel development workflows
- You have a complex monorepo
- You want to run multiple AI agents simultaneously
- You need strict isolation between features
- You're building production applications

❌ **Use basic template if:**
- Simple project structure
- Single-developer workflow
- Don't need parallel execution
- Learning Claude Code basics
- Rapid prototyping

---

## Summary

This worktree template provides:
- ✅ Full isolated worktree management
- ✅ 15 parallel workflow capacity
- ✅ Dynamic port assignment (9100-9114, 9200-9214)
- ✅ Comprehensive cleanup tools
- ✅ 14 isolated ADW workflows
- ✅ Production-grade security and observability
- ✅ Battle-tested in tac-7 projects

**Total files:** ~38-42 files

**Source project:** `tac-7`

**Complexity:** Medium-High (requires understanding of git worktrees)

**Best for:** Complex projects with parallel development needs
