# Implementation Plan: JSONL Execution Log for ADW Workflows

**Spec Reference:** `specs/jsonl_execution_log_spec.md`
**Target Scope:** `store/iso_v1/adws/` only (basic and iso remain unchanged)

## Overview

Add comprehensive JSONL execution logging to all iso_v1 ADW workflow scripts. Each workflow execution will generate start and end log entries containing execution metadata, performance metrics, token consumption, and file modification tracking.

## 1. New Module: `adw_modules/execution_log.py`

Create a new module in `store/iso_v1/adws/adw_modules/execution_log.py` that provides:

### 1.1 Core Data Types

```python
class ExecutionLogEntry(BaseModel):
    """Base execution log entry structure."""
    timestamp: str                    # ISO 8601 format
    event_type: Literal["start", "end"]
    script_name: str                  # e.g., "adw_plan_iso.py"
    adw_id: str                       # 8-char workflow ID
    project_directory: str            # Absolute path to project root
    worktree_path: Optional[str]      # Path to worktree if applicable

class StartLogEntry(ExecutionLogEntry):
    """Log entry at script startup."""
    event_type: Literal["start"] = "start"
    issue_number: Optional[str]
    command_args: List[str]           # sys.argv
    environment: Dict[str, str]       # Relevant env vars (sanitized)
    git_branch: Optional[str]
    git_commit_hash: Optional[str]    # HEAD at start
    python_version: str
    platform: str                     # e.g., "win32", "darwin", "linux"

class FileInfo(BaseModel):
    """Detailed file information for verbosity level 2."""
    path: str
    size_bytes: int
    lines_added: Optional[int] = None    # For modified files only
    lines_removed: Optional[int] = None  # For modified files only

class FilesSummary(BaseModel):
    """Summary counts for verbosity level 0."""
    created_count: int
    modified_count: int
    deleted_count: int

class SubprocessInvocation(BaseModel):
    """Tracks a subprocess invocation by an orchestrator script."""
    script_name: str
    invocation_time: str      # ISO 8601
    end_time: str             # ISO 8601
    duration_seconds: float
    return_code: int
    success: bool

class EndLogEntry(ExecutionLogEntry):
    """Log entry at script completion."""
    event_type: Literal["end"] = "end"
    execution_time_seconds: float
    exit_code: int
    success: bool

    # File tracking (format depends on verbosity setting)
    # Verbosity 0: Only files_summary populated
    # Verbosity 1: files_created/modified/deleted as List[str]
    # Verbosity 2: files_created/modified/deleted as List[FileInfo]
    files_summary: Optional[FilesSummary] = None  # Verbosity 0
    files_created: Optional[Union[List[str], List[FileInfo]]] = None  # Verbosity 1-2
    files_modified: Optional[Union[List[str], List[FileInfo]]] = None  # Verbosity 1-2
    files_deleted: Optional[Union[List[str], List[FileInfo]]] = None  # Verbosity 1-2

    # Token/cost consumption (aggregated from all agent calls)
    total_tokens_input: Optional[int]
    total_tokens_output: Optional[int]
    total_cost_usd: Optional[float]
    total_api_duration_ms: Optional[int]
    num_agent_calls: int

    # Licensing info
    claude_mode: Literal["apikey", "max", "unknown"]  # From config or auto-detected
    model_set_used: Optional[str]     # "base" or "heavy"
    models_used: List[str]            # e.g., ["sonnet", "opus"]

    # Subprocess tracking (for orchestrator scripts only)
    subprocesses: List[SubprocessInvocation] = []
    subprocess_count: int = 0
    subprocess_failures: int = 0

    # Error info (if failed)
    error_type: Optional[str]
    error_message: Optional[str]
```

### 1.2 Core Functions

```python
def get_log_file_path() -> Optional[str]:
    """Get log file path from ADW_LOGGING_DIR environment variable."""

def log_execution_start(
    script_name: str,
    adw_id: str,
    issue_number: Optional[str] = None,
    worktree_path: Optional[str] = None,
) -> StartLogEntry:
    """Log script startup. Returns entry for later reference."""

def log_execution_end(
    start_entry: StartLogEntry,
    exit_code: int = 0,
    success: bool = True,
    error_type: Optional[str] = None,
    error_message: Optional[str] = None,
) -> EndLogEntry:
    """Log script completion with aggregated metrics."""

def track_agent_execution(adw_id: str, output_file: str) -> None:
    """Track an agent execution for later aggregation in end log."""

def get_files_changed_since(start_commit: str, cwd: Optional[str] = None) -> tuple[List[str], List[str], List[str]]:
    """Get files created, modified, deleted since start_commit."""
```

### 1.3 Context Manager (Optional Convenience)

```python
@contextmanager
def execution_log_context(
    script_name: str,
    adw_id: str,
    issue_number: Optional[str] = None,
):
    """Context manager for automatic start/end logging."""
    start_entry = log_execution_start(...)
    try:
        yield start_entry
        log_execution_end(start_entry, success=True)
    except Exception as e:
        log_execution_end(start_entry, success=False, error=e)
        raise
```

## 2. Configuration System

### 2.1 Two-Stage Configuration

Configuration uses a **two-stage hierarchy** with local settings taking precedence over global:

| Priority | Location | Scope |
|----------|----------|-------|
| 1 (highest) | `.adw/settings.json` | Project-local (in working directory) |
| 2 (lowest) | `~/.adw/settings.json` | Global (user home directory) |

**Resolution Rules:**
- Settings are merged, with local values overriding global values
- If neither file exists, logging is disabled (scripts run normally)
- Missing individual settings use defaults

### 2.2 Settings Schema

Create `store/iso_v1/adw_settings_schema.json` for validation:

```json
{
  "$schema": "http://json-schema.org/draft-07/schema#",
  "type": "object",
  "properties": {
    "logging_directory": {
      "type": "string",
      "description": "Directory for JSONL log files. Absolute or relative path. Relative paths resolved from project root."
    },
    "verbosity": {
      "type": "integer",
      "enum": [0, 1, 2],
      "default": 1,
      "description": "Log verbosity level for file tracking"
    },
    "claude_mode": {
      "type": "string",
      "enum": ["apikey", "max", "default"],
      "default": "default",
      "description": "Claude licensing mode: apikey (API key), max (Claude Max subscription), or default (auto-detect)"
    }
  }
}
```

### 2.3 Settings Details

#### `logging_directory`
- **Type:** String (path)
- **Required:** Yes (for logging to be enabled)
- **Examples:**
  - Absolute: `"/var/log/adw"`
  - Relative: `"logs/adw"` (resolved from project root)
  - Home-relative: `"~/adw-logs"` (tilde expansion supported)
- **Log file name:** `adw_execution.log.jsonl` (fixed name within directory)

#### `verbosity`
Controls how much file detail is included in log entries:

| Level | File Counts | File Names | File Lengths | Diff Stats |
|-------|-------------|------------|--------------|------------|
| 0 | ✅ | ❌ | ❌ | ❌ |
| 1 | ✅ | ✅ | ❌ | ❌ |
| 2 | ✅ | ✅ | ✅ | ✅ |

**Log entry examples by verbosity:**

**Verbosity 0:**
```json
{
  "files_summary": {
    "created_count": 3,
    "modified_count": 2,
    "deleted_count": 0
  }
}
```

**Verbosity 1:**
```json
{
  "files_created": ["specs/plan.md", "src/feature.py", "tests/test_feature.py"],
  "files_modified": ["src/main.py", "README.md"],
  "files_deleted": []
}
```

**Verbosity 2:**
```json
{
  "files_created": [
    {"path": "specs/plan.md", "size_bytes": 2456},
    {"path": "src/feature.py", "size_bytes": 1823},
    {"path": "tests/test_feature.py", "size_bytes": 945}
  ],
  "files_modified": [
    {"path": "src/main.py", "size_bytes": 5678, "lines_added": 45, "lines_removed": 12},
    {"path": "README.md", "size_bytes": 3421, "lines_added": 8, "lines_removed": 2}
  ],
  "files_deleted": []
}
```

#### `claude_mode`
Specifies how Claude is being accessed:

| Value | Description |
|-------|-------------|
| `"apikey"` | Using ANTHROPIC_API_KEY for API access |
| `"max"` | Using Claude Max subscription |
| `"default"` | Auto-detect based on environment (checks for API key first) |

**Auto-detection logic (when `"default"`):**
1. If `ANTHROPIC_API_KEY` is set → `"apikey"`
2. Else if Claude Max session detected → `"max"`
3. Else → `"unknown"`

### 2.4 Example Configuration Files

**Global (`~/.adw/settings.json`):**
```json
{
  "logging_directory": "~/adw-logs",
  "verbosity": 1,
  "claude_mode": "default"
}
```

**Local (`.adw/settings.json`):**
```json
{
  "logging_directory": "logs/adw",
  "verbosity": 2
}
```

**Merged result:** Local `logging_directory` and `verbosity` override global; `claude_mode` inherited from global.

### 2.5 Configuration Loading Functions

```python
def load_adw_settings() -> Optional[Dict[str, Any]]:
    """Load and merge ADW settings from global and local config files.

    Returns:
        Merged settings dict, or None if no config files exist.
    """

def get_logging_directory() -> Optional[str]:
    """Get resolved logging directory path, or None if logging disabled."""

def get_verbosity() -> int:
    """Get verbosity level (default: 1)."""

def get_claude_mode() -> Literal["apikey", "max", "default"]:
    """Get configured Claude mode (default: "default")."""
```

## 3. Subprocess Tracking

When an orchestrator script (like `adw_sdlc_iso.py`) calls other ADW scripts, it must track those invocations.

### 3.1 Subprocess Tracking Data

Each subprocess invocation captures:

| Field | Type | Description |
|-------|------|-------------|
| `script_name` | string | Name of invoked script (e.g., `"adw_plan_iso.py"`) |
| `invocation_time` | string | ISO 8601 timestamp when subprocess started |
| `end_time` | string | ISO 8601 timestamp when subprocess completed |
| `duration_seconds` | float | Execution duration |
| `return_code` | int | Process exit code (0 = success) |
| `success` | bool | Whether subprocess succeeded |

### 3.2 Updated EndLogEntry for Orchestrators

```python
class SubprocessInvocation(BaseModel):
    """Tracks a subprocess invocation by an orchestrator script."""
    script_name: str
    invocation_time: str      # ISO 8601
    end_time: str             # ISO 8601
    duration_seconds: float
    return_code: int
    success: bool

class EndLogEntry(ExecutionLogEntry):
    # ... existing fields ...

    # Subprocess tracking (for orchestrator scripts)
    subprocesses: List[SubprocessInvocation] = []
    subprocess_count: int = 0
    subprocess_failures: int = 0
```

### 3.3 Subprocess Tracking Functions

```python
def track_subprocess_start(script_name: str) -> SubprocessInvocation:
    """Record start of a subprocess invocation. Returns partial entry."""

def track_subprocess_end(
    invocation: SubprocessInvocation,
    return_code: int
) -> SubprocessInvocation:
    """Complete subprocess tracking with end time and return code."""

def get_tracked_subprocesses() -> List[SubprocessInvocation]:
    """Get all tracked subprocesses for current execution."""
```

### 3.4 Orchestrator Integration Pattern

```python
from adw_modules.execution_log import (
    log_execution_start,
    log_execution_end,
    track_subprocess_start,
    track_subprocess_end,
)

def main():
    start_entry = log_execution_start(
        script_name="adw_sdlc_iso.py",
        adw_id=adw_id,
        issue_number=issue_number,
    )

    subprocesses = []

    # Track each subprocess
    plan_invoc = track_subprocess_start("adw_plan_iso.py")
    plan_result = subprocess.run(["uv", "run", "adw_plan_iso.py", ...])
    plan_invoc = track_subprocess_end(plan_invoc, plan_result.returncode)
    subprocesses.append(plan_invoc)

    build_invoc = track_subprocess_start("adw_build_iso.py")
    build_result = subprocess.run(["uv", "run", "adw_build_iso.py", ...])
    build_invoc = track_subprocess_end(build_invoc, build_result.returncode)
    subprocesses.append(build_invoc)

    # ... more subprocesses ...

    log_execution_end(
        start_entry=start_entry,
        subprocesses=subprocesses,
        # ... other fields ...
    )
```

### 3.5 Sample Orchestrator End Entry

```json
{
  "timestamp": "2025-12-04T11:45:00.000+00:00",
  "event_type": "end",
  "level": "info",
  "message": "SDLC workflow completed: 5/5 phases succeeded",
  "script_name": "adw_sdlc_iso.py",
  "adw_id": "a1b2c3d4",
  "issue_number": "123",
  "execution_time_seconds": 1842.5,
  "exit_code": 0,
  "success": true,
  "subprocess_count": 5,
  "subprocess_failures": 0,
  "subprocesses": [
    {
      "script_name": "adw_plan_iso.py",
      "invocation_time": "2025-12-04T11:15:00.000+00:00",
      "end_time": "2025-12-04T11:20:42.000+00:00",
      "duration_seconds": 342.0,
      "return_code": 0,
      "success": true
    },
    {
      "script_name": "adw_build_iso.py",
      "invocation_time": "2025-12-04T11:20:43.000+00:00",
      "end_time": "2025-12-04T11:32:15.000+00:00",
      "duration_seconds": 692.0,
      "return_code": 0,
      "success": true
    },
    {
      "script_name": "adw_test_iso.py",
      "invocation_time": "2025-12-04T11:32:16.000+00:00",
      "end_time": "2025-12-04T11:38:45.000+00:00",
      "duration_seconds": 389.0,
      "return_code": 0,
      "success": true
    },
    {
      "script_name": "adw_review_iso.py",
      "invocation_time": "2025-12-04T11:38:46.000+00:00",
      "end_time": "2025-12-04T11:42:30.000+00:00",
      "duration_seconds": 224.0,
      "return_code": 0,
      "success": true
    },
    {
      "script_name": "adw_document_iso.py",
      "invocation_time": "2025-12-04T11:42:31.000+00:00",
      "end_time": "2025-12-04T11:45:00.000+00:00",
      "duration_seconds": 149.0,
      "return_code": 0,
      "success": true
    }
  ],
  "total_cost_usd": 0.2345,
  "num_agent_calls": 12,
  "licensing_mode": "apikey"
}
```

### 3.6 Note on Nested Logging

**Important:** Both orchestrator AND individual scripts write to the same log file. This means:
- `adw_sdlc_iso.py` writes a start entry
- `adw_plan_iso.py` writes its own start/end entries (invoked as subprocess)
- `adw_build_iso.py` writes its own start/end entries
- ... and so on
- `adw_sdlc_iso.py` writes its end entry (with subprocess summary)

This provides both detailed per-phase logs AND an aggregated orchestrator view. Use `adw_id` (the lnav `opid-field`) to correlate all entries for a single workflow.

## 4. Token Consumption Tracking

### 4.1 Source of Token Data

Token consumption data comes from Claude Code's JSONL output. The last line of each `raw_output.jsonl` contains a result message with:

```json
{
  "type": "result",
  "subtype": "success",
  "duration_ms": 45000,
  "duration_api_ms": 38000,
  "num_turns": 5,
  "total_cost_usd": 0.0234,
  "session_id": "abc123"
}
```

### 3.2 Enhanced `ClaudeCodeResultMessage`

Update `data_types.py` to add optional token fields if Claude Code provides them:

```python
class ClaudeCodeResultMessage(BaseModel):
    # Existing fields...
    total_cost_usd: float
    duration_ms: int
    duration_api_ms: int
    num_turns: int
    # New optional fields (may not be present in all versions)
    input_tokens: Optional[int] = None
    output_tokens: Optional[int] = None
```

### 3.3 Aggregation Strategy

After each `execute_template()` or `prompt_claude_code()` call, parse the output file and accumulate:
- Total cost across all agent invocations
- Total API duration
- Number of agent calls
- Models used

Store in a module-level or thread-local accumulator that `log_execution_end()` reads.

## 4. File Modification Tracking

### 4.1 Git-Based Tracking

At script start:
1. Record current HEAD commit hash
2. Record list of tracked and untracked files

At script end:
1. Use `git status --porcelain` to find changes
2. Use `git diff --name-status HEAD~n` or compare to start commit
3. Categorize as created/modified/deleted

### 4.2 Worktree Considerations

For iso workflows, file tracking should be relative to the worktree path, not the main repository.

```python
def get_files_changed_since(start_commit: str, cwd: Optional[str] = None):
    """
    Returns (created, modified, deleted) file lists.
    cwd should be worktree_path for iso workflows.
    """
```

## 5. Scripts to Modify

All 14 ADW workflow scripts in `store/iso_v1/adws/`:

| Script | Type | Notes |
|--------|------|-------|
| `adw_plan_iso.py` | Individual | Entry point, creates worktree |
| `adw_build_iso.py` | Individual | Implementation phase |
| `adw_test_iso.py` | Individual | Testing phase |
| `adw_review_iso.py` | Individual | Review phase |
| `adw_document_iso.py` | Individual | Documentation phase |
| `adw_patch_iso.py` | Individual | Direct patch workflow |
| `adw_ship_iso.py` | Individual | Deployment workflow |
| `adw_plan_build_iso.py` | Orchestrator | Calls plan + build |
| `adw_plan_build_test_iso.py` | Orchestrator | Calls plan + build + test |
| `adw_plan_build_review_iso.py` | Orchestrator | Calls plan + build + review |
| `adw_plan_build_test_review_iso.py` | Orchestrator | Full pipeline |
| `adw_plan_build_document_iso.py` | Orchestrator | Calls plan + build + document |
| `adw_sdlc_iso.py` | Orchestrator | Complete SDLC |
| `adw_sdlc_zte_iso.py` | Orchestrator | Zero-touch execution |

### 5.1 Modification Pattern for Individual Scripts

```python
# At the top of main()
from adw_modules.execution_log import log_execution_start, log_execution_end, get_log_file_path

def main():
    # Early initialization
    adw_id = sys.argv[2] if len(sys.argv) > 2 else None
    issue_number = sys.argv[1] if len(sys.argv) > 1 else None

    # Log start (if logging enabled)
    start_entry = None
    if get_log_file_path():
        start_entry = log_execution_start(
            script_name="adw_plan_iso.py",
            adw_id=adw_id or "unknown",
            issue_number=issue_number,
        )

    exit_code = 0
    success = True
    error_info = None

    try:
        # ... existing main() logic ...

    except Exception as e:
        exit_code = 1
        success = False
        error_info = (type(e).__name__, str(e))
        raise
    finally:
        # Log end (if logging enabled)
        if start_entry:
            log_execution_end(
                start_entry=start_entry,
                exit_code=exit_code,
                success=success,
                error_type=error_info[0] if error_info else None,
                error_message=error_info[1] if error_info else None,
            )
```

### 5.2 Modification Pattern for Orchestrator Scripts

Orchestrators should log their own execution (not sub-script executions, which log themselves):

```python
def main():
    # Log orchestrator start
    start_entry = log_execution_start(
        script_name="adw_sdlc_iso.py",
        adw_id=adw_id,
        issue_number=issue_number,
    )

    # Subprocess calls (each logs itself)
    subprocess.run(["uv", "run", "adw_plan_iso.py", ...])
    subprocess.run(["uv", "run", "adw_build_iso.py", ...])
    # ...

    # Log orchestrator end (aggregated view)
    log_execution_end(start_entry, ...)
```

## 6. Integration with Existing Agent Module

### 6.1 Modify `agent.py`

After each successful agent execution, call the tracking function:

```python
def prompt_claude_code(request: AgentPromptRequest) -> AgentPromptResponse:
    # ... existing logic ...

    if result.returncode == 0:
        # Track execution for logging
        from .execution_log import track_agent_execution
        track_agent_execution(request.adw_id, request.output_file)

        # ... rest of existing logic ...
```

## 7. Sample Log Output

### 7.1 Start Entry

```json
{
  "timestamp": "2025-12-04T10:30:00.000Z",
  "event_type": "start",
  "script_name": "adw_plan_iso.py",
  "adw_id": "a1b2c3d4",
  "project_directory": "/home/user/myproject",
  "worktree_path": "/home/user/myproject/trees/a1b2c3d4",
  "issue_number": "123",
  "command_args": ["adw_plan_iso.py", "123", "a1b2c3d4"],
  "environment": {
    "ANTHROPIC_API_KEY": "sk-ant-***",
    "ADW_LOGGING_DIR": "/var/log/adw"
  },
  "git_branch": "feat-123-a1b2c3d4-add-feature",
  "git_commit_hash": "abc123def456",
  "python_version": "3.13.0",
  "platform": "linux"
}
```

### 7.2 End Entry (Verbosity 1)

```json
{
  "timestamp": "2025-12-04T10:35:42.000Z",
  "event_type": "end",
  "level": "info",
  "message": "Workflow completed successfully in 342.5s ($0.06)",
  "script_name": "adw_plan_iso.py",
  "adw_id": "a1b2c3d4",
  "project_directory": "/home/user/myproject",
  "worktree_path": "/home/user/myproject/trees/a1b2c3d4",
  "execution_time_seconds": 342.5,
  "exit_code": 0,
  "success": true,
  "files_created": ["specs/a1b2c3d4_plan_spec.md"],
  "files_modified": [],
  "files_deleted": [],
  "total_tokens_input": 15420,
  "total_tokens_output": 3256,
  "total_cost_usd": 0.0567,
  "total_api_duration_ms": 298000,
  "num_agent_calls": 4,
  "claude_mode": "apikey",
  "model_set_used": "base",
  "models_used": ["sonnet"],
  "error_type": null,
  "error_message": null
}
```

### 7.3 End Entry (Verbosity 0 - Summary Only)

```json
{
  "timestamp": "2025-12-04T10:35:42.000Z",
  "event_type": "end",
  "level": "info",
  "message": "Workflow completed successfully in 342.5s ($0.06)",
  "script_name": "adw_plan_iso.py",
  "adw_id": "a1b2c3d4",
  "project_directory": "/home/user/myproject",
  "execution_time_seconds": 342.5,
  "exit_code": 0,
  "success": true,
  "files_summary": {
    "created_count": 1,
    "modified_count": 0,
    "deleted_count": 0
  },
  "total_cost_usd": 0.0567,
  "num_agent_calls": 4,
  "claude_mode": "apikey"
}
```

### 7.4 End Entry (Verbosity 2 - Detailed)

```json
{
  "timestamp": "2025-12-04T10:35:42.000Z",
  "event_type": "end",
  "level": "info",
  "message": "Workflow completed successfully in 342.5s ($0.06)",
  "script_name": "adw_plan_iso.py",
  "adw_id": "a1b2c3d4",
  "project_directory": "/home/user/myproject",
  "execution_time_seconds": 342.5,
  "exit_code": 0,
  "success": true,
  "files_created": [
    {"path": "specs/a1b2c3d4_plan_spec.md", "size_bytes": 2456}
  ],
  "files_modified": [
    {"path": "src/main.py", "size_bytes": 5678, "lines_added": 45, "lines_removed": 12}
  ],
  "files_deleted": [],
  "total_tokens_input": 15420,
  "total_tokens_output": 3256,
  "total_cost_usd": 0.0567,
  "total_api_duration_ms": 298000,
  "num_agent_calls": 4,
  "claude_mode": "apikey",
  "model_set_used": "base",
  "models_used": ["sonnet"]
}
```

## 8. Implementation Order

1. **Create `adw_config.py` module** for two-stage configuration loading
   - Settings schema validation
   - Global/local config merging
   - Path resolution (absolute, relative, tilde expansion)

2. **Create `execution_log.py` module** with data types and core functions
   - Log entry data types (StartLogEntry, EndLogEntry, SubprocessInvocation, FileInfo)
   - Verbosity-aware file tracking
   - Subprocess tracking for orchestrators

3. **Update `data_types.py`** to include optional token fields in `ClaudeCodeResultMessage`

4. **Integrate tracking into `agent.py`** after agent executions

5. **Modify individual phase scripts** (plan, build, test, review, document, patch, ship)
   - Add start/end logging
   - File change tracking

6. **Modify orchestrator scripts** (plan_build, plan_build_test, sdlc, etc.)
   - Add start/end logging
   - Subprocess invocation tracking

7. **Create lnav format file** (`store/iso_v1/lnav/adw_execution_log.json`)

8. **Create installation script** (`scripts/install_lnav_format.sh`)

9. **Add tests** in `adw_tests/test_execution_log.py` and `adw_tests/test_adw_config.py`

10. **Update documentation** in `adws/README.md`

## 9. Testing Strategy

### 9.1 Unit Tests

- Test log entry serialization/deserialization
- Test file change detection
- Test token aggregation logic
- Test licensing mode detection

### 9.2 Integration Tests

- Run a workflow with `ADW_LOGGING_DIR` set
- Verify start and end entries are written
- Verify file lists are accurate
- Verify token consumption is aggregated correctly

### 9.3 Edge Cases

- `ADW_LOGGING_DIR` not set (no-op)
- Log directory doesn't exist (create it)
- Log file permissions error (log warning, continue execution)
- Script crashes mid-execution (ensure end entry still written via finally block)
- Orchestrator with failing sub-script (still log orchestrator end)

## 10. Risks and Mitigations

| Risk | Mitigation |
|------|------------|
| Logging overhead affects performance | Keep logging minimal; use async writes if needed |
| Log file grows unbounded | Document rotation strategy; user responsibility |
| Token data unavailable in some Claude versions | Make token fields optional; log "unknown" |
| Git operations slow in large repos | Use `--quiet` flags; limit diff scope |
| Secrets in environment logged | Sanitize sensitive values (mask API keys) |

## 11. lnav Compatibility

The log format is designed to be compatible with [lnav (Log File Navigator)](https://lnav.org/), a powerful terminal-based log viewer that supports JSON Lines format natively.

### 11.1 lnav Format File

Create `adw_execution_log.json` format file to be installed in `~/.lnav/formats/adw/`:

```json
{
    "$schema": "https://lnav.org/schemas/format-v1.schema.json",
    "adw_execution_log": {
        "title": "ADW Execution Log",
        "description": "AI Developer Workflow execution logs from iso_v1 scripts",
        "url": "https://github.com/your-org/cc_setup",
        "file-type": "json",
        "json": true,
        "hide-extra": false,
        "ordered-by-time": true,
        "timestamp-field": "timestamp",
        "timestamp-format": ["%Y-%m-%dT%H:%M:%S.%f%z", "%Y-%m-%dT%H:%M:%S%z"],
        "level-field": "level",
        "level": {
            "info": "info",
            "warning": "warning",
            "error": "error",
            "fatal": "fatal"
        },
        "opid-field": "adw_id",
        "line-format": [
            {"field": "event_type", "min-width": 5, "max-width": 5},
            " ",
            {"field": "adw_id", "min-width": 8, "max-width": 8},
            " ",
            {"field": "script_name", "min-width": 25, "max-width": 35, "overflow": "truncate"},
            " ",
            {"field": "issue_number", "min-width": 5, "default-value": "-"},
            " ",
            {"field": "message", "overflow": "truncate"}
        ],
        "value": {
            "timestamp": {"kind": "string"},
            "event_type": {"kind": "string", "identifier": true},
            "level": {"kind": "string"},
            "script_name": {"kind": "string", "identifier": true},
            "adw_id": {"kind": "string", "identifier": true, "foreign-key": true},
            "issue_number": {"kind": "string", "identifier": true},
            "project_directory": {"kind": "string"},
            "worktree_path": {"kind": "string"},
            "message": {"kind": "string"},
            "execution_time_seconds": {"kind": "float"},
            "exit_code": {"kind": "integer"},
            "success": {"kind": "json"},
            "total_cost_usd": {"kind": "float"},
            "total_api_duration_ms": {"kind": "integer"},
            "num_agent_calls": {"kind": "integer"},
            "claude_mode": {"kind": "string"},
            "model_set_used": {"kind": "string"},
            "models_used": {"kind": "json"},
            "files_summary": {"kind": "json"},
            "files_created": {"kind": "json", "hidden": true},
            "files_modified": {"kind": "json", "hidden": true},
            "files_deleted": {"kind": "json", "hidden": true},
            "command_args": {"kind": "json", "hidden": true},
            "environment": {"kind": "json", "hidden": true},
            "git_branch": {"kind": "string"},
            "git_commit_hash": {"kind": "string"},
            "python_version": {"kind": "string", "hidden": true},
            "platform": {"kind": "string"},
            "error_type": {"kind": "string"},
            "error_message": {"kind": "string"},
            "total_tokens_input": {"kind": "integer"},
            "total_tokens_output": {"kind": "integer"},
            "subprocess_count": {"kind": "integer"},
            "subprocess_failures": {"kind": "integer"},
            "subprocesses": {"kind": "json", "hidden": true}
        },
        "sample": [
            {
                "line": "{\"timestamp\":\"2025-12-04T10:30:00.000+00:00\",\"event_type\":\"start\",\"level\":\"info\",\"script_name\":\"adw_plan_iso.py\",\"adw_id\":\"a1b2c3d4\",\"issue_number\":\"123\",\"message\":\"Starting workflow\",\"project_directory\":\"/home/user/project\"}"
            },
            {
                "line": "{\"timestamp\":\"2025-12-04T10:35:42.000+00:00\",\"event_type\":\"end\",\"level\":\"info\",\"script_name\":\"adw_plan_iso.py\",\"adw_id\":\"a1b2c3d4\",\"issue_number\":\"123\",\"message\":\"Workflow completed successfully\",\"success\":true,\"execution_time_seconds\":342.5,\"total_cost_usd\":0.0567}"
            },
            {
                "line": "{\"timestamp\":\"2025-12-04T11:00:00.000+00:00\",\"event_type\":\"end\",\"level\":\"error\",\"script_name\":\"adw_build_iso.py\",\"adw_id\":\"e5f6g7h8\",\"issue_number\":\"456\",\"message\":\"Workflow failed\",\"success\":false,\"error_type\":\"RuntimeError\",\"error_message\":\"Build failed\"}"
            }
        ]
    }
}
```

### 11.2 Required Log Entry Adjustments

To ensure lnav compatibility, add these fields to all log entries:

| Field | Purpose | Example |
|-------|---------|---------|
| `level` | Log level for filtering/coloring | `"info"`, `"warning"`, `"error"`, `"fatal"` |
| `message` | Human-readable summary | `"Starting workflow"`, `"Workflow completed"` |

**Level Mapping:**
- `start` events → `"info"`
- `end` with `success=true` → `"info"`
- `end` with `success=false` and non-zero exit → `"error"`
- `end` with `success=false` and exit=0 (warnings) → `"warning"`

### 11.3 Updated Sample Log Entries

**Start Entry (lnav-compatible):**
```json
{
  "timestamp": "2025-12-04T10:30:00.000+00:00",
  "event_type": "start",
  "level": "info",
  "message": "Starting adw_plan_iso workflow for issue #123",
  "script_name": "adw_plan_iso.py",
  "adw_id": "a1b2c3d4",
  "project_directory": "/home/user/myproject",
  "worktree_path": "/home/user/myproject/trees/a1b2c3d4",
  "issue_number": "123",
  "command_args": ["adw_plan_iso.py", "123", "a1b2c3d4"],
  "environment": {"ADW_LOGGING_DIR": "/var/log/adw"},
  "git_branch": "feat-123-a1b2c3d4-add-feature",
  "git_commit_hash": "abc123def456",
  "python_version": "3.13.0",
  "platform": "linux"
}
```

**End Entry (success, lnav-compatible):**
```json
{
  "timestamp": "2025-12-04T10:35:42.000+00:00",
  "event_type": "end",
  "level": "info",
  "message": "Workflow completed successfully in 342.5s ($0.06)",
  "script_name": "adw_plan_iso.py",
  "adw_id": "a1b2c3d4",
  "project_directory": "/home/user/myproject",
  "worktree_path": "/home/user/myproject/trees/a1b2c3d4",
  "issue_number": "123",
  "execution_time_seconds": 342.5,
  "exit_code": 0,
  "success": true,
  "files_created": ["specs/a1b2c3d4_plan_spec.md"],
  "files_modified": [],
  "files_deleted": [],
  "total_tokens_input": 15420,
  "total_tokens_output": 3256,
  "total_cost_usd": 0.0567,
  "total_api_duration_ms": 298000,
  "num_agent_calls": 4,
  "claude_mode": "apikey",
  "model_set_used": "base",
  "models_used": ["sonnet"],
  "error_type": null,
  "error_message": null
}
```

**End Entry (failure, lnav-compatible):**
```json
{
  "timestamp": "2025-12-04T11:00:00.000+00:00",
  "event_type": "end",
  "level": "error",
  "message": "Workflow failed: RuntimeError - Build compilation failed",
  "script_name": "adw_build_iso.py",
  "adw_id": "e5f6g7h8",
  "project_directory": "/home/user/myproject",
  "worktree_path": "/home/user/myproject/trees/e5f6g7h8",
  "issue_number": "456",
  "execution_time_seconds": 45.2,
  "exit_code": 1,
  "success": false,
  "files_created": [],
  "files_modified": ["src/main.py"],
  "files_deleted": [],
  "total_cost_usd": 0.0123,
  "num_agent_calls": 2,
  "claude_mode": "apikey",
  "error_type": "RuntimeError",
  "error_message": "Build compilation failed"
}
```

**Orchestrator End Entry (with subprocesses):**
```json
{
  "timestamp": "2025-12-04T11:45:00.000+00:00",
  "event_type": "end",
  "level": "info",
  "message": "SDLC workflow completed: 5/5 phases succeeded in 30.7m ($0.23)",
  "script_name": "adw_sdlc_iso.py",
  "adw_id": "a1b2c3d4",
  "issue_number": "123",
  "execution_time_seconds": 1842.5,
  "exit_code": 0,
  "success": true,
  "subprocess_count": 5,
  "subprocess_failures": 0,
  "subprocesses": [
    {"script_name": "adw_plan_iso.py", "invocation_time": "2025-12-04T11:15:00.000+00:00", "end_time": "2025-12-04T11:20:42.000+00:00", "duration_seconds": 342.0, "return_code": 0, "success": true},
    {"script_name": "adw_build_iso.py", "invocation_time": "2025-12-04T11:20:43.000+00:00", "end_time": "2025-12-04T11:32:15.000+00:00", "duration_seconds": 692.0, "return_code": 0, "success": true}
  ],
  "total_cost_usd": 0.2345,
  "num_agent_calls": 12,
  "claude_mode": "apikey"
}
```

### 11.4 lnav Usage

**Install format file:**
```bash
mkdir -p ~/.lnav/formats/adw
cp adw_execution_log.json ~/.lnav/formats/adw/
```

**View logs:**
```bash
# View log file
lnav /var/log/adw/adw_execution.log.jsonl

# Filter by ADW ID (using opid)
lnav /var/log/adw/adw_execution.log.jsonl -c ':filter-in adw_id = "a1b2c3d4"'

# Show only errors
lnav /var/log/adw/adw_execution.log.jsonl -c ':set-min-log-level error'

# Follow log in real-time
lnav -f /var/log/adw/adw_execution.log.jsonl
```

**Useful lnav features for ADW logs:**
- Press `i` to view log histogram
- Press `p` to pretty-print current JSON line
- Use `:filter-in script_name = "adw_sdlc_iso.py"` to filter by script
- Use SQL queries: `:SELECT adw_id, SUM(total_cost_usd) FROM adw_execution_log GROUP BY adw_id`

### 11.5 Format File Distribution

The lnav format file should be:
1. Included in `store/iso_v1/` for deployment with cc_setup
2. Optionally auto-installed by a setup script
3. Documented in `adws/README.md`

**Suggested location:** `store/iso_v1/lnav/adw_execution_log.json`

**Installation script snippet:**
```bash
# Add to scripts/install_lnav_format.sh
LNAV_FORMAT_DIR="${HOME}/.lnav/formats/adw"
mkdir -p "${LNAV_FORMAT_DIR}"
cp "$(dirname "$0")/../lnav/adw_execution_log.json" "${LNAV_FORMAT_DIR}/"
echo "lnav format installed to ${LNAV_FORMAT_DIR}"
```

## 12. Future Enhancements

- Log rotation and compression
- Structured log aggregation (e.g., to Loki, CloudWatch)
- Dashboard for workflow analytics
- Cost tracking and alerting thresholds
- Correlation of logs across orchestrator + sub-scripts
- lnav format file auto-installation during cc_setup execution
