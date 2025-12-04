# Feature: Add isox Mode to cc_setup

## Metadata
issue_number: `0`
adw_id: `0`
issue_json: `{"title": "Add isox mode to cc_setup", "body": "At the moment there are two modes, basic, and iso. I would like to add a new method isox, and the adws directory it is based on is located in d:\\python\\scipap\\adws. Make a plan that you can execute to accomplish this."}`

## Feature Description
Add a third setup mode called "isox" to the cc_setup tool by migrating artifacts from `d:\python\scipap\adws` into a new `store/isox/` directory. The isox mode represents an enhanced version of the iso (isolated worktree) mode with additional features and updated modules.

The key difference is that isox mode will:
- Have its artifacts permanently stored in `store/isox/` (created via migration)
- Include additional modules like `complexity.py` and `console.py` in `adw_modules/`
- Provide more recent versions of the isolated worktree ADW scripts
- Follow the same artifact discovery pattern as basic and iso modes

## User Story
As a developer using cc_setup
I want to install the isox mode artifacts
So that I can use the latest enhanced version of the isolated worktree ADW system from the scipap project

## Problem Statement
Currently, cc_setup only supports two modes (basic and iso), and both use the local `store/` directory for their artifacts. There is a need to add a third mode (isox) by migrating artifacts from `d:\python\scipap\adws` into the local store, making them a permanent part of the cc_setup tool.

The scipap directory contains updated ADW modules including:
- New modules: `complexity.py` and `console.py`
- Updated versions of existing modules with newer timestamps
- Enhanced workflow scripts

These artifacts need to be migrated into `store/isox/` to become the master copy for the new mode.

## Solution Statement
Extend cc_setup to support a third mode "isox" by:
1. Creating or updating the migration script to copy artifacts from `d:\python\scipap\adws` into `store/isox/`
2. Running the migration to populate `store/isox/` with the scipap artifacts
3. Adding "isox" as a valid mode choice in the argument parser
4. Updating documentation to describe the isox mode and its differences
5. Ensuring all existing file comparison, logging, and display functionality works with the new mode

The implementation will follow the existing pattern used for basic and iso modes. The `store/isox/` directory will become the permanent master copy of these artifacts, just like `store/basic/` and `store/iso/`.

## Relevant Files
Use these files to implement the feature:

- `migrate_to_store.py` - Migration script that needs to be extended to handle scipap source
- `cc_setup.py` (lines 1570-1574) - Contains the argument parser where mode choices are defined
- `cc_setup.py` (lines 770-771) - Mode string display logic needs to include isox description
- `cc_setup.py` (around line 1390) - `show_help_artifacts()` function needs to include isox
- `README.md` (lines 7-8, 152-166) - Documentation about available modes that needs updating
- `README.md` (lines 194-236) - Section describing setup modes that needs a new isox section
- `store/migration_log.txt` - Will be updated by migration script
- `d:\python\scipap\adws\` - Source directory containing the isox artifacts

### New Files
- `store/isox/` - New directory to store isox mode artifacts (created via migration)
- `store/isox/adws/` - ADW workflow scripts
- `store/isox/adws/adw_modules/` - ADW modules including new complexity.py and console.py
- `store/isox/adws/adw_tests/` - ADW test scripts
- `store/isox/adws/adw_triggers/` - ADW trigger scripts
- `store/isox/commands/` - Slash commands (if they exist in scipap)
- `store/isox/hooks/` - Claude Code hooks (if they exist in scipap)
- `store/isox/scripts/` - Utility scripts (if they exist in scipap)
- `store/isox/settings.json` - Settings file (if it exists in scipap)
- `specs/issue-0-adw-0-sdlc_planner-add-isox-mode.md` - This specification file

## Implementation Plan

### Phase 1: Migration
Create and populate the store/isox/ directory with artifacts from scipap:
- Update migrate_to_store.py to add isox migration
- Run migration to copy artifacts from `d:\python\scipap\adws` to `store/isox/`
- Verify all artifacts are copied correctly with proper directory structure
- Update migration log

### Phase 2: Code Integration
Add isox as a valid mode in cc_setup:
- Extend the argument parser to accept "isox" as a valid mode
- Add mode validation logic to handle the new mode
- Update mode display strings to include isox
- Ensure all artifact categories work correctly

### Phase 3: Documentation and Testing
Complete the feature with documentation and validation:
- Update README with isox mode description and examples
- Update help commands to include isox
- Test dry-run and execute modes with isox
- Verify no regressions in basic and iso modes

## Step by Step Tasks
IMPORTANT: Execute every step in order, top to bottom.

### 1. Update migrate_to_store.py to Add isox Migration
- Open `migrate_to_store.py`
- Locate the `main()` function (around line 170)
- Note that scipap is at `d:\python\scipap` not `d:\tac\scipap`
- Modify `migrate_mode()` function to accept an optional `source_base` parameter (default to `SOURCE_BASE`)
- After the iso migration call (line 193), add: `migrate_mode("adws", "isox", logger, source_base=Path(r"d:\python\scipap"))`
- This will migrate from `d:\python\scipap\adws` to `store/isox/`

### 2. Run the Migration Script
- Execute: `python migrate_to_store.py`
- Watch the output to see isox migration progress
- Verify that `store/isox/` is created
- Check that artifacts are copied:
  - ADW workflow scripts: `store/isox/adws/*.py`
  - ADW modules: `store/isox/adws/adw_modules/` including complexity.py and console.py
  - ADW tests: `store/isox/adws/adw_tests/`
  - ADW triggers: `store/isox/adws/adw_triggers/`
- Review the migration log in `store/migration_log.txt`

### 3. Verify Migrated Artifacts
- Run: `ls -la store/isox/adws/`
- Verify ADW scripts are present (adw_build_iso.py, adw_plan_iso.py, adw_test_iso.py, etc.)
- Run: `ls -la store/isox/adws/adw_modules/`
- Confirm complexity.py and console.py are present
- Run: `find store/isox -type f | wc -l` (or on Windows: `dir /s /b store\isox | find /c ":"`)
- Note the total file count for documentation
- Verify the directory structure matches the scipap source

### 4. Update Argument Parser to Accept isox Mode
- Open `cc_setup.py`
- Locate the `--mode` argument definition (around line 1571-1573)
- Change `choices=["basic", "iso"]` to `choices=["basic", "iso", "isox"]`
- Update the help text from `'basic' or 'iso' (isolated worktree)` to `'basic', 'iso' (isolated worktree), or 'isox' (isolated worktree extended)`
- Save the file

### 5. Update Mode Display Strings in display_header
- Locate the `display_header()` method (around line 768-780)
- Find the mode_str assignment (line 770)
- Change from: `mode_str = "Basic Mode" if self.config.mode == "basic" else "Isolated Worktree Mode"`
- To:
  ```python
  mode_str = "Basic Mode" if self.config.mode == "basic" else \
             "Isolated Worktree Mode" if self.config.mode == "iso" else \
             "Isolated Worktree Extended Mode"
  ```

### 6. Update show_help_artifacts Function
- Locate `show_help_artifacts()` function (around line 1383)
- Find the loop: `for mode in ["basic", "iso"]:` (line 1390)
- Change to: `for mode in ["basic", "iso", "isox"]:`
- Save the file

### 7. Update show_examples Function
- Locate the `show_examples()` function (around line 1429)
- Add new isox examples to the artifacts management section after the iso examples
- Add tuples to the examples list:
  ```python
  ("Execute isox mode", [
      "uv run cc_setup --target /path/to/project --mode isox --execute",
      "uv run cc_setup -t /path/to/project -m isox -ex"
  ]),
  ("Execute isox mode with overwrite", [
      "uv run cc_setup --target /path/to/project --mode isox --execute --overwrite",
      "uv run cc_setup -t /path/to/project -m isox -ex -ov"
  ])
  ```

### 8. Test Argument Parser
- Run: `uv run cc_setup --help`
- Verify that the mode choices show `{basic,iso,isox}`
- Verify help text mentions all three modes
- Ensure no syntax errors

### 9. Test Help Commands
- Run: `uv run cc_setup --help-artifacts`
- Verify that isox mode is listed
- Check the artifact count for isox (should match what was migrated)
- Run: `uv run cc_setup --help-examples`
- Verify that isox examples are shown

### 10. Test isox Mode with Dry Run
- Run: `uv run cc_setup -t test_isox_dry -m isox`
- Verify that the tool discovers artifacts from `store/isox/`
- Check that the output shows correct artifact counts
- Verify that the directory tree displays correctly
- Ensure the header shows "Isolated Worktree Extended Mode"
- Confirm no errors occur during artifact discovery

### 11. Test isox Mode Execution
- Run: `uv run cc_setup -t test_isox_exec -m isox -ex`
- Verify that all artifacts are copied successfully
- Check that `test_isox_exec/.claude/` contains expected files (if any)
- Verify that `test_isox_exec/adws/` contains ADW scripts
- Verify that `test_isox_exec/adws/adw_modules/` contains `complexity.py` and `console.py`
- Confirm that JSONL log is created at `test_isox_exec/.claude/cc_setup.log.jsonl`

### 12. Test File Comparison and Overwrite Logic
- Run: `uv run cc_setup -t test_isox_exec -m isox -ex` (without overwrite)
- Verify that all files show as "✓ Identical" and are skipped
- Run: `uv run cc_setup -t test_isox_exec -m isox -ex -ov`
- Verify that files are overwritten
- Check console output shows correct status indicators

### 13. Test Regression - Verify Basic and Iso Modes Still Work
- Run: `uv run cc_setup -t test_basic_verify -m basic -ex`
- Verify basic mode works without errors
- Run: `uv run cc_setup -t test_iso_verify -m iso -ex`
- Verify iso mode works without errors
- Confirm no functionality was broken by adding isox

### 14. Update README Documentation
- Open `README.md`
- Update line 7: Change "**Two Setup Modes**" to "**Three Setup Modes**"
- Update line 158: In the --mode row, change description to show "basic", "iso", or "isox"
- After line 236 (end of iso mode section), add new section:
  ```markdown
  ### Isolated Worktree Extended Mode (isox) (XX artifacts)

  Installs the latest enhanced isolated worktree artifacts from the scipap project:

  - **Settings**: X file (if present)
  - **Hooks**: X files (if present)
  - **Commands**: XX slash commands (if present)
  - **Scripts**: XX utility scripts (if present)
  - **ADWs**: XX isolated Agent Developer Workflow files
  - **ADW Modules**: XX modules including `complexity.py` and `console.py`

  **Directory Structure:**
  ```
  target-project/
  ├── .claude/
  │   ├── commands/          # XX slash commands (if present)
  │   ├── hooks/             # X hooks (if present)
  │   ├── adws/              # XX ADWs
  │   └── settings.json      # (if present)
  ├── scripts/               # XX utility scripts (if present)
  └── trees/                 # Worktree directory
  ```
  ```
- Replace "XX" with actual counts from step 3
- Add isox example to Quick Start section (around line 119-123):
  ```markdown
  ### Execute Isolated Worktree Extended Setup
  Copy enhanced artifacts from the scipap project:

  ```bash
  uv run cc_setup --target /path/to/project --mode isox --execute
  # Short form:
  uv run cc_setup -t /path/to/project -m isox -ex
  ```
  ```

### 15. Run All Validation Commands
Execute every command to validate the feature works correctly with zero regressions.

## Testing Strategy

### Unit Tests
- Test that argument parser accepts "isox" mode
- Test that ArtifactStore correctly discovers artifacts from `store/isox/`
- Test that all artifact categories are discovered correctly for isox mode
- Test that file comparison works for isox artifacts
- Test that JSONL logging records isox operations correctly
- Test that migration script correctly copies from scipap to store/isox/

### Edge Cases
- Migration from non-existent scipap directory (should show clear error or skip gracefully)
- store/isox/ exists but is empty (should show "no artifacts found")
- User runs isox mode before migration (should show error about missing store directory)
- User tries to use gitignore operations with isox mode (should work normally)
- User runs isox mode with all flags: `-t /path -m isox -ex -ov` (should work correctly)
- Migration script runs when store/isox/ already exists (should overwrite/update)

## Acceptance Criteria
- [ ] Migration script successfully copies artifacts from `d:\python\scipap\adws` to `store/isox/`
- [ ] `store/isox/` directory structure is created properly
- [ ] `store/isox/adws/adw_modules/` contains `complexity.py` and `console.py`
- [ ] cc_setup accepts "isox" as a valid mode via `--mode isox` or `-m isox`
- [ ] isox mode discovers artifacts from `store/isox/` directory
- [ ] All artifact categories are discovered correctly
- [ ] Dry-run mode shows correct artifact count and file list for isox
- [ ] Execute mode successfully copies all artifacts to target directory
- [ ] File comparison logic works (detects identical, different, new files)
- [ ] Overwrite logic works correctly with isox mode
- [ ] JSONL operation logging records isox operations with correct metadata
- [ ] `--help-artifacts` displays isox mode with artifact breakdown
- [ ] `--help-examples` shows isox usage examples
- [ ] README.md is updated with isox mode description and examples
- [ ] No regressions in basic or iso modes

## Validation Commands
Execute every command to validate the feature works correctly with zero regressions.

- `python migrate_to_store.py` - Run migration to create store/isox/
- `ls -la store/isox/` - Verify store/isox/ directory exists
- `ls -la store/isox/adws/adw_modules/` - Verify complexity.py and console.py are present
- `find store/isox -type f | wc -l` (or Windows: `dir /s /b store\isox | find /c ":"`) - Count total files migrated
- `uv run cc_setup --help` - Verify isox appears in mode choices
- `uv run cc_setup --help-artifacts` - Verify isox mode is listed with artifact count
- `uv run cc_setup --help-examples` - Verify isox examples are shown
- `uv run cc_setup -t test_isox_dry -m isox` - Dry run to verify artifact discovery
- `uv run cc_setup -t test_isox_exec -m isox -ex` - Execute to verify artifact copying
- `uv run cc_setup -t test_isox_exec -m isox -ex` - Run again to verify skip logic for identical files
- `uv run cc_setup -t test_isox_exec -m isox -ex -ov` - Run with overwrite to verify overwrite logic
- `uv run cc_setup -t test_basic_verify -m basic -ex` - Verify basic mode still works (no regression)
- `uv run cc_setup -t test_iso_verify -m iso -ex` - Verify iso mode still works (no regression)
- `ls test_isox_exec/.claude/` - Verify .claude directory structure (if applicable)
- `ls test_isox_exec/adws/adw_modules/` - Verify adw_modules contains complexity.py and console.py
- `cat test_isox_exec/.claude/cc_setup.log.jsonl` - Verify JSONL log contains isox operation

## Notes

### Migration Approach
The isox mode follows the same pattern as basic and iso modes by storing artifacts in the local `store/` directory. The migration script (`migrate_to_store.py`) is extended to copy artifacts from `d:\python\scipap\adws` into `store/isox/`, making them a permanent part of the cc_setup tool.

### One-Time Migration
The migration from scipap to store/isox/ is a one-time operation. After the migration:
- `store/isox/` becomes the master copy of these artifacts
- Updates to scipap won't automatically reflect in cc_setup
- To update isox artifacts in the future, re-run the migration script or manually update files in `store/isox/`

### Additional Modules in isox
The scipap directory includes two new modules not present in the iso mode:
- `complexity.py` - Provides complexity estimation for ADW tasks
- `console.py` - Provides enhanced console output formatting

These modules represent enhancements to the ADW system that are being actively developed in the scipap project.

### Self-Contained Distribution
After migration, cc_setup with isox mode is fully self-contained:
- No dependency on external scipap directory
- Works on any system where cc_setup is installed
- All artifacts are versioned with the cc_setup tool itself
- Follows the same distribution model as basic and iso modes

### Updating isox Artifacts
To update the isox artifacts from scipap in the future:
1. Update the source at `d:\python\scipap\adws`
2. Re-run `python migrate_to_store.py` to copy updated files
3. Use `--overwrite` flag when running cc_setup to update existing installations
4. Document the update in `store/migration_log.txt`

### scipap Directory Structure
The scipap source at `d:\python\scipap\adws` is expected to have:
- ADW workflow Python scripts at the root (adw_*.py)
- `adw_modules/` subdirectory with shared modules
- `adw_tests/` subdirectory with test scripts
- `adw_triggers/` subdirectory with trigger scripts
- Optionally: `.claude/settings.json`, `.claude/commands/`, `.claude/hooks/`, `scripts/`

The migration script will handle whatever structure exists in scipap and copy it appropriately to `store/isox/`.
