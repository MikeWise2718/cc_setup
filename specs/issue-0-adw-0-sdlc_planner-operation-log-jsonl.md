# Feature: Operation Log in JSONL Format

## Metadata
issue_number: `0`
adw_id: `0`
issue_json: `{"title": "Add JSONL operation log for applied operations", "body": "I would like cc_setup to leave a log in each repo that it is applied to so that it is easy to tell what has been done there. The log should be saved in jsonl format."}`

## Feature Description
Add functionality to cc_setup that creates a persistent JSONL (JSON Lines) formatted log file in each target repository where cc_setup operations are executed. This log will provide a machine-readable and human-readable record of what artifacts were installed, when they were installed, and with what configuration. Each operation (whether dry-run or execute) will append a new JSON object to the log file, making it easy to track the history of cc_setup operations applied to a repository.

The log will be stored in `.claude/cc_setup.log.jsonl` in the target repository, allowing users and tools to easily query what has been done to a repository, when it was done, and what artifacts are currently installed.

## User Story
As a developer using cc_setup across multiple repositories
I want to see a persistent log of all cc_setup operations applied to each repository
So that I can easily understand what artifacts are installed, when they were installed, and track the history of setup changes

## Problem Statement
Currently, cc_setup creates detailed log files in its own `logs/` directory with timestamped filenames (`cc_setup_20251031_135854.log`), but these logs:
1. Are stored in the cc_setup tool directory, not in the target repositories
2. Are not in a machine-readable structured format (they use plain text logging)
3. Don't provide an easy way to determine what was done to a specific target repository
4. Require manual inspection to understand the current state of a repository
5. Don't accumulate history in the target repository itself

This makes it difficult to:
- Quickly determine if cc_setup has been run on a repository
- See what mode (basic/iso) was used
- Track changes over time to a repository's setup
- Programmatically query the setup state of a repository

## Solution Statement
Implement a JSONL-based operation log that is written to each target repository at `.claude/cc_setup.log.jsonl`. Each time cc_setup runs (whether in dry-run or execute mode), it will append a JSON object containing:

- Timestamp of the operation
- Operation mode (dry-run vs execute)
- Setup mode (basic, iso, or gitignore operation type)
- Target directory path
- Overwrite flag status
- Statistics about the operation (files copied, skipped, overwritten, etc.)
- List of artifacts processed with their status
- cc_setup version
- Operation result (success/failure/cancelled)

This approach:
- Keeps the log with the repository it affects
- Provides structured data for easy querying
- Maintains a complete history of operations
- Is human-readable and machine-parsable
- Follows the JSONL standard (one JSON object per line)

## Relevant Files
Use these files to implement the feature:

- [cc_setup.py](cc_setup.py) - Main script that orchestrates all operations. This is where we'll add the JSONL logging functionality. Relevant sections:
  - `CCSetup` class - Main orchestrator, already has logging setup in `_setup_logging()` around line 215
  - `run()` method (line 938) - Main entry point where we need to add JSONL logging for artifact operations
  - `run_gitignore_operations()` method (line 885) - Entry point for gitignore operations where we need to add JSONL logging
  - `execute_operations()` method (line 538) - Where file operations occur, need to collect artifact data
  - `FileOperation` class (line 161) - Contains operation details that need to be logged
  - `SetupConfig` class (line 129) - Contains configuration and statistics that need to be logged

- [pyproject.toml](pyproject.toml) - Project metadata including version number (line 3) that should be included in logs

- [README.md](README.md) - Project documentation that should be updated to describe the new JSONL log feature

### New Files

- `.claude/cc_setup.log.jsonl` - Will be created in each target repository (not in the cc_setup tool directory itself)

## Implementation Plan

### Phase 1: Foundation
Create the core infrastructure for JSONL logging:
- Add a new `OperationLogger` class to handle JSONL file operations
- Define the JSON schema for log entries
- Add version detection from pyproject.toml
- Ensure the logger can append to existing JSONL files and create new ones

### Phase 2: Core Implementation
Integrate JSONL logging into the execution flow:
- Collect operation data throughout the execution process
- Generate structured log entries with all relevant metadata
- Write log entries to `.claude/cc_setup.log.jsonl` in the target directory
- Handle both artifact management and gitignore operations
- Handle both dry-run and execute modes appropriately

### Phase 3: Integration
Ensure the feature works seamlessly with existing functionality:
- Test with basic mode operations
- Test with iso mode operations
- Test with gitignore operations
- Verify logs accumulate correctly over multiple runs
- Update documentation to describe the new log file

## Step by Step Tasks

### 1. Design JSONL Log Schema
- Define the JSON structure for log entries including:
  - `timestamp`: ISO 8601 formatted timestamp
  - `version`: cc_setup version from pyproject.toml
  - `operation_type`: "artifact" or "gitignore"
  - `mode`: "basic", "iso", or gitignore language
  - `target_dir`: absolute path to target directory
  - `execute`: boolean indicating if changes were applied
  - `overwrite`: boolean indicating if overwrite was enabled
  - `result`: "success", "error", or "cancelled"
  - `statistics`: object containing operation counts
  - `artifacts`: array of processed artifacts with their status
  - `error_message`: optional error message if result is "error"

### 2. Implement OperationLogger Class
- Create a new `OperationLogger` class in cc_setup.py that:
  - Reads the version from pyproject.toml
  - Accepts operation data and formats it as JSON
  - Appends JSON objects to `.claude/cc_setup.log.jsonl` in the target directory
  - Handles file creation if the log doesn't exist
  - Properly handles JSON serialization of Path objects and other non-standard types
  - Ensures each JSON object is written on a single line (JSONL format)

### 3. Integrate Logger into CCSetup Class
- Add `operation_logger` as an instance variable in `CCSetup.__init__()`
- Create a method `_collect_operation_data()` to gather all relevant operation information
- Modify `run()` method to call the logger after operation completion
- Modify `run_gitignore_operations()` to call the logger after operation completion
- Ensure logging happens for both successful and failed operations

### 4. Handle Artifact Operations Logging
- In the `run()` method, collect data about:
  - All file operations performed
  - Statistics from `self.config`
  - Operation result (success/error/cancelled)
- Format artifact data from `self.operations` list
- Write log entry before the final return statement

### 5. Handle GitIgnore Operations Logging
- In the `run_gitignore_operations()` method, collect data about:
  - GitIgnore operation type (compare/merge/replace)
  - Comparison mode if applicable (diff/set)
  - Lines added/removed statistics
  - Operation result
- Write log entry before the final return statement

### 6. Add Error Handling
- Wrap JSONL logging in try-except to prevent logging failures from breaking operations
- Log any JSONL logging errors to the existing file-based logger
- Display warnings to console if JSONL logging fails, but don't fail the overall operation

### 7. Write Unit Tests
- Create test functions to validate:
  - JSON schema is correctly formatted
  - JSONL file is created if it doesn't exist
  - JSONL entries are appended correctly
  - Multiple operations accumulate in the log
  - Path objects are serialized correctly
  - Error cases are handled gracefully

### 8. Update Documentation
- Update README.md to document the new `.claude/cc_setup.log.jsonl` file
- Add a section explaining the JSONL log format
- Provide examples of querying the log using jq or Python
- Document the JSON schema with examples

### 9. Test End-to-End Scenarios
- Test basic mode execution with JSONL logging
- Test iso mode execution with JSONL logging
- Test gitignore operations with JSONL logging
- Test multiple sequential operations to verify log accumulation
- Test dry-run mode to verify it also logs
- Verify log entries contain accurate data
- Test with both new and existing target repositories

### 10. Run Validation Commands
- Execute all validation commands to ensure no regressions
- Verify the feature works correctly across all operation types

## Testing Strategy

### Unit Tests
Since this is a Python CLI tool without an existing test suite, create focused test scenarios:

1. **JSONL Formatting Tests**:
   - Verify each log entry is valid JSON
   - Verify log entries are single-line (JSONL format)
   - Verify all required fields are present
   - Verify Path objects serialize correctly

2. **File Operations Tests**:
   - Verify log file is created if it doesn't exist
   - Verify entries are appended to existing logs
   - Verify file permissions are appropriate

3. **Data Collection Tests**:
   - Verify statistics are accurately captured
   - Verify artifact lists are complete
   - Verify timestamps are in ISO 8601 format
   - Verify version is read correctly from pyproject.toml

4. **Error Handling Tests**:
   - Verify logging errors don't break operations
   - Verify error messages are logged appropriately

### Edge Cases
- Target directory doesn't exist yet (should create .claude/ directory)
- `.claude/` directory exists but `cc_setup.log.jsonl` doesn't
- Existing `cc_setup.log.jsonl` file with valid entries
- Existing `cc_setup.log.jsonl` file with invalid JSON (corrupted)
- Write permissions denied for target directory
- Very large number of artifacts (ensure performance is acceptable)
- Concurrent cc_setup runs (JSONL append should be atomic per write)
- Operations that are cancelled (Ctrl+C)
- Operations that fail with errors

## Acceptance Criteria
- [ ] Each cc_setup operation (artifact or gitignore) creates/appends to `.claude/cc_setup.log.jsonl` in the target directory
- [ ] Log entries are valid JSONL format (one JSON object per line)
- [ ] Log entries include all required fields: timestamp, version, operation_type, mode, target_dir, execute, result
- [ ] Statistics are accurately recorded: files copied, skipped, overwritten, etc.
- [ ] Artifact details are recorded with their status and action
- [ ] Both dry-run and execute modes are logged
- [ ] Failed operations are logged with error messages
- [ ] Cancelled operations (Ctrl+C) are logged with result="cancelled"
- [ ] The log accumulates entries over multiple runs
- [ ] Logging failures don't break cc_setup operations
- [ ] Documentation explains the JSONL log format with examples
- [ ] All existing functionality continues to work without regressions

## Validation Commands
Execute every command to validate the feature works correctly with zero regressions.

### Manual Testing Commands

```bash
# Test 1: Basic mode execution and verify JSONL log creation
uv run cc_setup -t test_target_jsonl -m basic -ex
cat test_target_jsonl/.claude/cc_setup.log.jsonl
python -m json.tool test_target_jsonl/.claude/cc_setup.log.jsonl

# Test 2: Run again to verify log accumulation
uv run cc_setup -t test_target_jsonl -m basic -ex -ov
cat test_target_jsonl/.claude/cc_setup.log.jsonl | wc -l  # Should be 2 lines

# Test 3: ISO mode execution
uv run cc_setup -t test_target_jsonl -m iso -ex -ov
cat test_target_jsonl/.claude/cc_setup.log.jsonl | wc -l  # Should be 3 lines

# Test 4: GitIgnore operation
uv run cc_setup -t test_target_jsonl -gi python -gix compare
cat test_target_jsonl/.claude/cc_setup.log.jsonl | wc -l  # Should be 4 lines

# Test 5: Verify JSON is valid for each line
cat test_target_jsonl/.claude/cc_setup.log.jsonl | while read line; do echo "$line" | python -m json.tool > /dev/null || echo "Invalid JSON"; done

# Test 6: Dry-run mode (should still log)
uv run cc_setup -t test_target_jsonl2 -m basic
cat test_target_jsonl2/.claude/cc_setup.log.jsonl

# Cleanup test directories
rm -rf test_target_jsonl test_target_jsonl2
```

### Automated Validation
- `uv run cc_setup --help` - Verify help still works
- `uv run cc_setup -ha` - Verify artifact listing still works
- `uv run cc_setup -hx` - Verify examples still work

## Notes

### JSONL Format
JSONL (JSON Lines) is a convenient format for storing structured data that may be processed one record at a time. It is newline-delimited JSON where each line is a valid JSON object. This format is ideal for:
- Appending new entries without reading the entire file
- Streaming processing of large logs
- Easy parsing with tools like `jq`, Python, or other JSON libraries

Example JSONL entry:
```jsonl
{"timestamp": "2025-11-08T14:30:00Z", "version": "0.4.1", "operation_type": "artifact", "mode": "basic", "target_dir": "/path/to/repo", "execute": true, "overwrite": false, "result": "success", "statistics": {"files_copied": 51, "files_skipped": 0}, "artifacts": [{"filename": "settings.json", "category": "Settings", "status": "copied"}]}
```

### Version Numbering
The version should be read from `pyproject.toml` at runtime to ensure it's always accurate. Consider bumping the version to 0.5.0 when this feature is implemented, as it adds significant new functionality.

### Performance Considerations
Since JSONL logging happens after operations complete, it should have minimal performance impact. The log file will grow over time, but since we only append (never read the entire file during normal operations), this is acceptable. Users can rotate/archive old logs if needed.

### Future Enhancements
- Add a `--show-log` command to display the JSONL log in a formatted table
- Add a `--query-log` command to filter log entries by date, mode, or other criteria
- Consider adding a cleanup command to archive old log entries
- Consider adding a "verify" mode that checks if current state matches the log
