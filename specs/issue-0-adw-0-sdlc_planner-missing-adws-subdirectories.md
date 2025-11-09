# Bug: Missing adws Subdirectories in Migration and Setup

## Metadata
issue_number: `0`
adw_id: `0`
issue_json: `N/A`

## Bug Description
The `migrate_to_store.py` script and `cc_setup.py` tool failed to copy the necessary `adws` subdirectories (`adw_modules`, `adw_tests`, `adw_triggers`) when migrating from tac-6 (basic mode) and tac-7 (iso mode). These subdirectories contain critical Python modules, tests, and trigger scripts that are required for the ADW (Agent Developer Workflow) system to function properly.

Currently, only the `.py` files directly within the `adws` directory are being copied, while the subdirectories are being explicitly skipped in the migration script (migrate_to_store.py:139-141).

## Problem Statement
The `adws` directory structure is incomplete in the local store and in projects that have already been set up using `cc_setup`. The missing subdirectories contain:
- `adw_modules/`: Core Python modules for workflow operations, GitHub integration, state management, and utilities (9 files including agent.py, github.py, workflow_ops.py)
- `adw_tests/`: Test files for ADW functionality including health checks and E2E tests (6 test files)
- `adw_triggers/`: Trigger scripts for cron jobs and webhooks (3 trigger scripts)

Without these subdirectories, the ADW scripts cannot import required modules and will fail at runtime.

## Solution Statement
1. Update `migrate_to_store.py` to copy the `adw_modules`, `adw_tests`, and `adw_triggers` subdirectories (and their contents) from tac-6 and tac-7 into the local store
2. Update `cc_setup.py` to recursively copy these subdirectories when deploying artifacts to target projects
3. Ensure that existing ADW scripts in target projects are not overwritten (preserving user modifications) while still adding the missing subdirectories
4. Provide a migration path for projects that have already been set up using the old behavior by re-running cc_setup

## Steps to Reproduce
1. Run `python migrate_to_store.py` - observe that adws subdirectories are skipped
2. Check `store/basic/adws` - notice `adw_modules`, `adw_tests`, `adw_triggers` are missing
3. Check `store/iso/adws` - notice the same subdirectories are missing
4. Run `uv run cc_setup -t /path/to/project -m basic -ex` on a new project
5. Check the deployed `adws` directory - subdirectories are missing
6. Attempt to run an ADW script that imports from `adw_modules` - it will fail with ImportError

## Root Cause Analysis
The root cause is in `migrate_to_store.py` lines 128-141. The code explicitly skips directories with the comment "Skip directories like utils, adw_modules, etc." This was likely done to only copy the main ADW scripts, but it inadvertently excluded critical subdirectories.

Similarly, `cc_setup.py` in the `_discover_artifacts` method (lines 142-196) only iterates files with `if artifact_file.is_file()` (line 175), which means it does not handle subdirectories within the adws category.

## Relevant Files
Use these files to fix the bug:

- **migrate_to_store.py** (lines 78-145) - Migration script that needs to recursively copy adws subdirectories
- **cc_setup.py** (lines 115-196) - The ArtifactStore._discover_artifacts method
- **cc_setup.py** (lines 710-753) - The execute_operations method

### New Files
No new files need to be created. This is a fix to existing functionality.

## Step by Step Tasks
IMPORTANT: Execute every step in order, top to bottom.

### Step 1: Update migrate_to_store.py to Copy adws Subdirectories
- Read `migrate_to_store.py` to understand the current structure
- Modify the `migrate_mode` function around lines 109-144 to handle adws subdirectories specially
- For the `adws` category only, after copying individual files, check for and recursively copy the subdirectories: `adw_modules`, `adw_tests`, `adw_triggers`
- Use `shutil.copytree` to recursively copy these subdirectories with all their contents
- Add appropriate logging calls using `logger.log_copy` for each directory copied
- Ensure the function preserves file metadata (timestamps, permissions)

### Step 2: Extend cc_setup.py to Support Directory Artifacts
- Read the `ArtifactDefinition` class definition (lines 116-126)
- Add an `is_directory` boolean field to the `ArtifactDefinition` class
- Update the `_discover_artifacts` method to discover subdirectories for adws category
- Create `ArtifactDefinition` objects for directories with `is_directory=True`

### Step 3: Update execute_operations to Handle Directory Copying
- Read the `execute_operations` method (lines 710-753)
- Modify to check if artifact is a directory
- Use `shutil.copytree` for directory artifacts with proper overwrite handling

### Step 4: Update File Status Checking for Directories
- Modify `analyze_operations` method to handle directory artifacts
- Update status indicators for directories

### Step 5: Re-run migrate_to_store.py to Populate Store
- Execute `python migrate_to_store.py`
- Verify subdirectories are copied to store

### Step 6: Test cc_setup with New Directory Support
- Test dry run and execution with directory support
- Verify overwrite behavior

### Step 7: Verify Import Functionality
- Test Python imports from deployed adw_modules

### Step 8: Run Validation Commands
Execute validation commands below.

## Validation Commands
Execute every command to validate the bug is fixed with zero regressions.

- `python migrate_to_store.py` - Re-run migration
- `ls -la store/basic/adws/` - Verify subdirectories exist
- `ls -la store/iso/adws/` - Verify subdirectories exist
- `ls -la store/basic/adws/adw_modules/` - Verify 9 files
- `ls -la store/basic/adws/adw_tests/` - Verify 6 files
- `ls -la store/basic/adws/adw_triggers/` - Verify 3 files
- `uv run cc_setup -t test_adws_fix -m basic -ex` - Deploy
- `ls -la test_adws_fix/adws/adw_modules/` - Verify copied
- `uv run cc_setup -ha` - Verify help works

## Notes
- Preserve backward compatibility
- Respect --overwrite flag
- Handle executable permissions
- Only apply to adws category
