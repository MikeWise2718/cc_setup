# Bug: Identical Files Unnecessarily Overwritten with --overwrite Flag

## Metadata
issue_number: `N/A`
adw_id: `b281b95b`
issue_json: `{"title": "Skip overwriting identical files even with --overwrite flag", "body": "so when we are installing files, and we have a file that is identical in the source and target directories, and we specify overwrite, and have identical files, it overwrites it. I would like it, in this case, to skip the overwriting and to retain the blue \"Identical\" status."}`

## Bug Description
When running the `cc_setup.py` tool with the `--overwrite` flag, files that are identical between source and target directories are being overwritten unnecessarily. The expected behavior is that identical files should be skipped (retain their "✓ Identical" status in cyan) even when `--overwrite` is specified, since overwriting identical content serves no purpose and wastes I/O operations.

**Current Behavior:**
- With `--overwrite` flag: Identical files show "⚠ Overwrite" status (red) and are overwritten
- Files are copied even though source and target have identical content

**Expected Behavior:**
- With `--overwrite` flag: Identical files should show "✓ Identical" status (cyan) and be skipped
- Only files with different content should be overwritten
- Display message should indicate "Skip (identical)" or "Skipping (identical)"

## Problem Statement
The logic in `analyze_operations()` method (cc_setup.py:306-345) does not check if files are identical before setting `will_overwrite = True`. When `--overwrite` is enabled and a file exists, it always overwrites regardless of whether the content is identical, resulting in unnecessary file operations.

## Solution Statement
Modify the logic in `analyze_operations()` to check if files are identical before deciding to overwrite. When files are identical, set `will_copy = False` and `will_overwrite = False` regardless of the `--overwrite` flag setting. This ensures that:
1. Identical files are never overwritten (efficient, no unnecessary I/O)
2. The status remains "✓ Identical" (cyan) in the display
3. Only files with different content are subject to overwrite behavior

## Steps to Reproduce
1. Run `cc_setup.py` to install artifacts to a target directory:
   ```bash
   uv run cc_setup.py --target ./test_target --mode basic --execute
   ```
2. Run the same command again with `--overwrite` flag:
   ```bash
   uv run cc_setup.py --target ./test_target --mode basic --execute --overwrite
   ```
3. Observe that identical files show "⚠ Overwrite" status and are overwritten
4. Check logs to confirm files were copied unnecessarily

**Expected:** Identical files should show "✓ Identical" status and be skipped
**Actual:** Identical files show "⚠ Overwrite" status and are overwritten

## Root Cause Analysis
The bug is in the `analyze_operations()` method at lines 321-322:

```python
will_copy = (not exists or self.config.overwrite) and source_path.exists()
will_overwrite = exists and self.config.overwrite and source_path.exists()
```

This logic sets `will_overwrite = True` whenever:
- File exists in target
- `--overwrite` flag is enabled
- Source file exists

The problem is that `is_identical` is calculated (line 319) but **not used** in determining `will_copy` and `will_overwrite`. The logic should skip overwriting when files are identical, but currently it doesn't check the `is_identical` flag.

## Relevant Files
Use these files to fix the bug:

- **cc_setup.py** (lines 306-345) - Contains the `analyze_operations()` method where the bug exists
  - The `will_copy` and `will_overwrite` logic needs to check `is_identical` before deciding to overwrite
  - The `is_identical` variable is already calculated but not used in the decision logic

- **cc_setup.py** (lines 148-191) - Contains the `FileOperation` class
  - The `_determine_status()` method correctly shows "✓ Identical" status
  - The `get_action()` method correctly returns "Skip (identical)" messages
  - No changes needed here; the logic already supports skipping identical files

- **cc_setup.py** (lines 447-489) - Contains the `execute_operations()` method
  - This method respects `will_copy` flag, so no changes needed here
  - Once we fix the analysis logic, execution will automatically skip identical files

### New Files
No new files are needed for this bug fix.

## Step by Step Tasks
IMPORTANT: Execute every step in order, top to bottom.

### 1. Fix the overwrite logic in analyze_operations()
- Locate the `analyze_operations()` method in `cc_setup.py` (line 306)
- Find the logic at lines 321-322 that sets `will_copy` and `will_overwrite`
- Modify the logic to check `is_identical` before deciding to overwrite:
  - When files are identical (`is_identical == True`), set `will_copy = False` and `will_overwrite = False` regardless of `--overwrite` flag
  - When files are different, preserve the current behavior: overwrite if `--overwrite` is enabled
- The corrected logic should be:
  ```python
  # Don't copy if files are identical, even with --overwrite flag
  will_copy = (not exists or (self.config.overwrite and not is_identical)) and source_path.exists()
  will_overwrite = exists and self.config.overwrite and source_path.exists() and not is_identical
  ```

### 2. Verify the fix with manual testing
- Create a test target directory
- Run the tool once to install artifacts: `uv run cc_setup.py --target ./test_target --mode basic --execute`
- Run again with `--overwrite` flag: `uv run cc_setup.py --target ./test_target --mode basic --execute --overwrite`
- Verify that identical files show "✓ Identical" status in cyan
- Verify that identical files show "Skipping (identical)" action
- Check logs to confirm identical files were NOT copied

### 3. Test edge cases
- Test with `--overwrite` flag on a project where some files are identical and some are different
- Verify that identical files are skipped (cyan "✓ Identical")
- Verify that different files are overwritten (red "⚠ Overwrite")
- Verify that new files are copied (green "✓ New")

### 4. Run validation commands
- Execute all validation commands listed in the "Validation Commands" section below
- Ensure all tests pass with zero regressions
- Verify that the summary statistics correctly reflect skipped identical files

## Validation Commands
Execute every command to validate the bug is fixed with zero regressions.

```bash
# Test 1: Initial install to create identical files
uv run cc_setup.py --target ./test_target --mode basic --execute

# Test 2: Re-run with --overwrite - identical files should be SKIPPED
uv run cc_setup.py --target ./test_target --mode basic --execute --overwrite

# Expected output:
# - Identical files should show "✓ Identical" status in cyan
# - Action should be "Skipping (identical)"
# - Summary should show: "X files identical (skipped)"
# - Should NOT show files being overwritten if they're identical

# Test 3: Verify with dry-run first
uv run cc_setup.py --target ./test_target --mode basic --overwrite

# Expected: Should show identical files with "Skip (identical)" action

# Test 4: Modify one file to test mixed scenario
echo "# modified" >> ./test_target/.claude/commands/bug.md
uv run cc_setup.py --target ./test_target --mode basic --execute --overwrite

# Expected:
# - bug.md should show "⚠ Overwrite" and be overwritten (different content)
# - All other identical files should show "✓ Identical" and be skipped

# Test 5: Clean up test directory
rm -rf ./test_target
```

## Notes
- This is a surgical fix that only modifies 2 lines of code
- The fix improves efficiency by avoiding unnecessary file I/O operations
- The `FileOperation` class already has the correct display logic; we're just fixing the decision logic
- No new dependencies or libraries are needed
- The fix maintains backward compatibility - all existing functionality works the same, we're just optimizing the overwrite behavior
- Statistics tracking will automatically reflect the correct behavior since we're modifying the core decision logic
