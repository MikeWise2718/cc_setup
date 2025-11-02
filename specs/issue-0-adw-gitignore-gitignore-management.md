# Feature: GitIgnore File Management

## Metadata
issue_number: `0`
adw_id: `gitignore`
issue_json: `{"title": "Add .gitignore management feature", "body": "I would like this to manage .gitignore files as well. There are sample .gitignore files in the store/git subfolder. There are two at the moment \".gitignore_python\" and \".gitignore_csharp\". I would like an option to compare the gitignore in the target directory to the specified .gitignore file. Perhaps with the option 'uv run cc_setup.py --target /path/to/project --gitignore python. In this case it should print out a diff between the files. If a furthur option is specified '--gitignore_execute merge'. It should replace the topic with a merged version (no lines deleted). If a furthur options is psecified '--gitignore_execute replace', then the target .gitignore should be prelaces with the source .gitignore."}`

## Feature Description
This feature adds .gitignore file management capabilities to the cc_setup tool. Users will be able to compare their project's .gitignore file against language-specific templates stored in `store/git/`, view differences, and optionally merge or replace their .gitignore file with the template. The feature supports multiple languages (currently Python and C#) with extensibility for additional languages.

The feature provides three operations:
1. **Compare/Diff**: Shows differences between target .gitignore and template
2. **Merge**: Adds missing entries from template to target (preserves all existing entries)
3. **Replace**: Completely replaces target .gitignore with template

## User Story
As a developer using cc_setup for project configuration
I want to manage my .gitignore files using language-specific templates
So that I can ensure my projects have comprehensive and standardized .gitignore rules without manually maintaining them

## Problem Statement
Currently, cc_setup only manages Claude Code artifacts (commands, hooks, ADWs, scripts, settings). Users must manually manage their .gitignore files, which can lead to:
- Inconsistent .gitignore patterns across projects
- Missing important exclusion patterns for their language/framework
- Time wasted manually researching and updating .gitignore rules
- Risk of committing sensitive files or build artifacts

## Solution Statement
Extend cc_setup with .gitignore management functionality that leverages a local store of language-specific .gitignore templates. The solution adds new command-line options (`--gitignore` and `--gitignore_execute`) that allow users to compare, merge, or replace their project's .gitignore file. This follows the same pattern as the existing artifact management system: analyze first (dry-run), then execute with explicit flags.

The implementation uses Python's `difflib` for generating unified diffs and set operations for intelligent merging that preserves existing entries while adding new ones.

## Relevant Files
Use these files to implement the feature:

- **cc_setup.py** (lines 1-649) - Main script that needs extension
  - Contains `SetupConfig` class for CLI argument storage (needs new gitignore args)
  - Contains `ArtifactStore` class for local store management (can be used as reference for gitignore store)
  - Contains `CCSetup` class with main execution logic (needs new gitignore operation methods)
  - Contains `main()` function with argparse setup (needs new CLI arguments)
  - Already has rich console display patterns to follow for output formatting

- **store/git/.gitignore_python** (51 lines) - Python template
  - Python-specific patterns (pycache, .pyc, venv, etc.)
  - Contains common IDE and OS patterns

- **store/git/.gitignore_csharp** (430 lines) - C# template
  - Visual Studio and .NET-specific patterns
  - Comprehensive coverage of build artifacts, caches, and temporary files

- **README.md** (lines 1-354) - Documentation that needs updating
  - Needs new section documenting --gitignore functionality
  - Needs examples of gitignore operations
  - Needs updated command-line options table

### New Files
None required - all functionality extends existing files.

## Implementation Plan

### Phase 1: Foundation
Add data structures and infrastructure to support .gitignore management alongside existing artifact management. This includes extending the CLI argument parser, configuration class, and adding helper methods for .gitignore file operations.

### Phase 2: Core Implementation
Implement the three core operations (compare/diff, merge, replace) with proper file handling, diff generation, and merge logic. Add rich console output formatting to maintain consistency with the existing tool's UX.

### Phase 3: Integration
Integrate the .gitignore functionality into the main execution flow, add comprehensive logging, update documentation, and ensure the feature works seamlessly alongside existing artifact management operations.

## Step by Step Tasks

### Task 1: Extend CLI Argument Parser
- Add `--gitignore` argument to accept language choice (e.g., "python", "csharp")
- Add `--gitignore_execute` argument with choices: "compare" (default), "merge", "replace"
- Update help text with examples of gitignore operations
- Ensure these arguments work independently from `--mode` argument

### Task 2: Extend SetupConfig Class
- Add `gitignore_lang` property to store the language choice from `--gitignore` argument
- Add `gitignore_execute` property to store the operation mode
- Add statistics properties: `gitignore_lines_added`, `gitignore_lines_removed`, `gitignore_unchanged`
- Initialize these properties in the `__init__` method from args

### Task 3: Add GitIgnore Helper Methods to CCSetup Class
- Add `get_gitignore_template_path(lang: str) -> Path` method
  - Returns path to `store/git/.gitignore_{lang}` file
  - Validates that the template file exists
  - Returns None if template not found
- Add `read_gitignore_lines(file_path: Path) -> List[str]` method
  - Reads .gitignore file and returns list of non-empty, stripped lines
  - Handles file not existing (returns empty list)
  - Removes comments and blank lines for cleaner processing
- Add `get_available_gitignore_languages() -> List[str]` method
  - Scans `store/git/` directory for `.gitignore_*` files
  - Extracts and returns list of available languages
  - Used for validation and help text

### Task 4: Implement Compare/Diff Operation
- Add `compare_gitignore()` method to CCSetup class
  - Reads both template and target .gitignore files
  - Uses `difflib.unified_diff()` to generate diff
  - Displays diff using rich console with color coding:
    - Green for lines to be added (+ prefix)
    - Red for lines in target but not template (- prefix)
    - Cyan for context lines
  - Returns boolean indicating if files are identical
  - Logs comparison results

### Task 5: Implement Merge Operation
- Add `merge_gitignore()` method to CCSetup class
  - Reads both template and target .gitignore files
  - Uses set union to combine unique lines (preserves all existing)
  - Preserves original section comments from template
  - Maintains logical grouping of patterns
  - Displays preview of what will be added (in dry-run mode)
  - Writes merged content to target in execute mode
  - Creates backup of original as `.gitignore.backup` before merge
  - Updates statistics: `gitignore_lines_added`
  - Logs merge operation details

### Task 6: Implement Replace Operation
- Add `replace_gitignore()` method to CCSetup class
  - Reads template .gitignore file
  - Displays warning about full replacement
  - Shows summary of current target file (line count)
  - In execute mode:
    - Creates backup of original as `.gitignore.backup`
    - Copies template to target .gitignore location
    - Logs replacement operation
  - Updates statistics: `gitignore_lines_added`, `gitignore_lines_removed`

### Task 7: Add GitIgnore Display Methods
- Add `display_gitignore_header()` method
  - Similar to `display_header()` but for gitignore operations
  - Shows language, operation mode, target path
  - Shows template location
- Add `display_gitignore_summary()` method
  - Shows operation results (lines added, removed, unchanged)
  - Shows backup file location if created
  - Provides next steps guidance

### Task 8: Integrate GitIgnore Flow into Main Run Logic
- Modify `CCSetup.run()` method to detect gitignore mode
  - Check if `config.gitignore_lang` is set
  - If set, run gitignore operations instead of artifact operations
  - Call appropriate method based on `gitignore_execute` value
- Add validation for gitignore language availability
- Ensure proper error handling and logging

### Task 9: Add GitIgnore Validation and Error Handling
- Validate that requested language template exists
  - Show available languages if not found
  - Exit gracefully with helpful error message
- Validate that target directory is specified
- Handle missing target .gitignore file gracefully
  - For compare: show that target is empty
  - For merge: treat as empty file (template becomes result)
  - For replace: show that new file will be created
- Add comprehensive error handling for file I/O operations

### Task 10: Update Help and Documentation
- Update `README.md` with new "GitIgnore Management" section
  - Add section after "Setup Modes" and before "Usage Examples"
  - Document the three operations with examples
  - Add command-line options to the options table
  - Include example workflows
- Update `--help` output in argparse with clear descriptions
- Add examples to epilog section of argparse

### Task 11: Add Unit Tests
- Create test cases for `get_gitignore_template_path()`
- Create test cases for `read_gitignore_lines()`
- Create test cases for `compare_gitignore()` with identical and different files
- Create test cases for `merge_gitignore()` with various scenarios
- Create test cases for `replace_gitignore()`
- Create test case for backup file creation
- Mock file I/O for isolated testing

### Task 12: Validation and Testing
- Run validation commands to ensure no regressions
- Test all three operations (compare, merge, replace) manually
- Test with missing target .gitignore file
- Test with missing template (invalid language)
- Test backup file creation
- Verify logging output is comprehensive
- Verify rich console output is properly formatted
- Test interaction with existing artifact management (ensure they don't conflict)

## Testing Strategy

### Unit Tests
- **File Reading**: Test `read_gitignore_lines()` with various file formats (empty, with comments, with blank lines)
- **Template Discovery**: Test `get_available_gitignore_languages()` returns correct list
- **Template Path Resolution**: Test `get_gitignore_template_path()` with valid and invalid languages
- **Comparison Logic**: Test `compare_gitignore()` with identical files, different files, and missing files
- **Merge Logic**: Test `merge_gitignore()` with overlapping and non-overlapping content
- **Replace Logic**: Test `replace_gitignore()` creates backup and replaces correctly
- **Integration**: Test that gitignore operations don't interfere with artifact operations

### Edge Cases
- Target .gitignore file does not exist (all three operations)
- Target .gitignore file exists but is empty
- Template file not found (invalid language parameter)
- Target directory does not exist
- Target directory exists but is not writable (permission errors)
- Template and target .gitignore files are identical
- Target .gitignore contains entries not in template (merge should preserve)
- Very large .gitignore files (performance testing)
- .gitignore files with unusual line endings (CRLF vs LF)
- Concurrent access (backup file naming conflicts)
- Running multiple operations in sequence

## Acceptance Criteria
- [ ] User can run `--gitignore python` to compare target .gitignore with Python template
- [ ] User can run `--gitignore csharp` to compare target .gitignore with C# template
- [ ] Compare operation shows clear unified diff output with color coding
- [ ] User can run `--gitignore_execute merge` to merge template into target (preserves all existing lines)
- [ ] Merge operation creates `.gitignore.backup` before modifying target
- [ ] User can run `--gitignore_execute replace` to completely replace target with template
- [ ] Replace operation creates `.gitignore.backup` before replacing
- [ ] Graceful handling when target .gitignore doesn't exist (merge and replace create new file)
- [ ] Clear error message when invalid language is specified, with list of available languages
- [ ] GitIgnore operations work independently from artifact management operations
- [ ] Can run both artifact and gitignore operations (not in same command, but sequentially)
- [ ] Rich console output matches existing style (colors, panels, formatting)
- [ ] All operations logged to timestamped log file
- [ ] README.md updated with comprehensive gitignore documentation
- [ ] No regressions in existing artifact management functionality
- [ ] Help text clearly documents all new options with examples

## Validation Commands
Execute every command to validate the feature works correctly with zero regressions.

### Test GitIgnore Compare Operation
- `uv run cc_setup.py --target D:\python\cc_setup --gitignore python` - Compare current .gitignore with Python template (dry-run)
- Verify unified diff output is displayed
- Verify colors are applied correctly (green for additions, red for removals)

### Test GitIgnore Merge Operation
- `mkdir -p test_target && echo "# Custom rule" > test_target/.gitignore` - Create test target with existing content
- `uv run cc_setup.py --target test_target --gitignore python --gitignore_execute merge` - Preview merge (dry-run)
- Verify preview shows what will be added
- Verify existing "# Custom rule" will be preserved
- `uv run cc_setup.py --target test_target --gitignore python --gitignore_execute merge --execute` - Execute merge
- Verify `.gitignore.backup` was created
- Verify merged .gitignore contains both original and template content
- `rm -rf test_target` - Cleanup

### Test GitIgnore Replace Operation
- `mkdir -p test_target && echo "# Custom rule" > test_target/.gitignore` - Create test target with existing content
- `uv run cc_setup.py --target test_target --gitignore csharp --gitignore_execute replace` - Preview replace (dry-run)
- Verify warning about replacement is shown
- `uv run cc_setup.py --target test_target --gitignore csharp --gitignore_execute replace --execute` - Execute replace
- Verify `.gitignore.backup` was created with original content
- Verify new .gitignore matches C# template exactly
- `rm -rf test_target` - Cleanup

### Test Edge Cases
- `uv run cc_setup.py --target test_target --gitignore invalid_lang` - Test with invalid language
- Verify error message lists available languages (python, csharp)
- `uv run cc_setup.py --target test_target_nonexist --gitignore python --gitignore_execute merge --execute` - Test with non-existent target directory
- Verify target directory and .gitignore are created

### Test Help and Documentation
- `uv run cc_setup.py --help` - Verify new options documented
- Verify examples include gitignore operations
- `cat README.md` - Verify README includes gitignore section

### Test No Regressions in Existing Functionality
- `uv run cc_setup.py --target test_target --mode basic` - Run existing artifact management (dry-run)
- Verify normal operation unchanged
- `uv run cc_setup.py --help-artifacts` - Verify artifact help still works
- `rm -rf test_target` - Cleanup

### Validate Logging
- `ls logs/` - Verify new log file created
- `tail -50 logs/cc_setup_*.log | grep -i gitignore` - Verify gitignore operations logged

## Notes

### Implementation Notes
- The `--gitignore` and `--gitignore_execute` options work independently from `--mode` (basic/iso)
- Users should not specify both artifact mode and gitignore mode in the same command
- The dry-run pattern (default behavior) is preserved: analyze first, then execute with flags
- Use `difflib.unified_diff()` for generating clean, readable diffs
- For merge operation, use set operations for deduplication but preserve order where possible
- Backup files use simple `.backup` suffix; consider adding timestamps if multiple backups needed

### Future Considerations
- Support for more languages (JavaScript/TypeScript, Java, Go, Rust, etc.)
- Allow users to add custom templates to `store/git/`
- Interactive mode for selectively choosing which patterns to merge
- Validate .gitignore syntax (warn about invalid patterns)
- Integration with `git check-ignore` to test patterns
- Support for global .gitignore templates
- Cloud-based template repository synchronization
- Diff tool integration (external diff viewers)

### Design Decisions
- **Why separate from artifact management?** GitIgnore is fundamentally different from Claude Code artifacts - it's a single file operation vs. multiple files, and the operations (merge, replace) don't map to artifact copying
- **Why backup files?** Provides safety net for users; `.gitignore` files often contain project-specific customizations worth preserving
- **Why merge preserves all existing lines?** Conservative approach prioritizes not breaking existing functionality; users may have project-specific patterns not in templates
- **Why difflib for comparison?** Standard library solution, widely understood format (unified diff), good for terminal output

### Dependencies
- No new external dependencies required
- Uses existing libraries: `pathlib`, `difflib`, `rich` (already in project), `argparse`
- Templates stored locally in `store/git/` directory (already created)
