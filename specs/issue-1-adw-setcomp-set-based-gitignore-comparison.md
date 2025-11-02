# Feature: Set-Based GitIgnore Comparison

## Metadata
issue_number: `1`
adw_id: `setcomp`
issue_json: `{"title": "Add set-based comparison for .gitignore files", "body": "diff does not work so well for .gitignore since the exclusion entries do not depend on their order in the file in anyway. I would prefer to have a hashtable based comparison, whereby entries in the source but not in the target are listed in one color, and vice-versa in another color. Please plan that feature. Make it an option for now."}`

## Feature Description
This feature adds an alternative comparison mode for .gitignore files that uses set-based (hashtable) logic instead of line-by-line diff. Since .gitignore patterns are order-independent, this provides a more semantically meaningful comparison by grouping patterns into three categories:
1. Patterns only in template (missing from target)
2. Patterns only in target (custom patterns not in template)
3. Patterns in both (common patterns)

The feature will be implemented as an optional flag (`--gitignore_compare_mode`) that allows users to choose between "diff" (current unified diff) and "set" (new set-based comparison).

## User Story
As a developer using cc_setup to manage .gitignore files
I want to see a set-based comparison that shows which patterns are missing, which are extra, and which are common
So that I can understand the semantic differences without being confused by line order changes

## Problem Statement
The current `compare` operation uses `difflib.unified_diff()` which performs line-by-line comparison. This creates several issues for .gitignore files:
- Order changes show as differences even though .gitignore semantics are order-independent
- Hard to quickly identify which patterns are actually missing vs just reordered
- Diff context lines add noise when you just want to know "what's missing" and "what's extra"
- Users need to mentally parse diff output (+/- prefixes, @@ markers) to understand actual pattern differences

## Solution Statement
Add a new comparison mode that treats .gitignore files as sets of patterns. The implementation will:
- Parse both files into sets of non-empty, non-comment lines (content patterns only)
- Calculate three sets: patterns only in template, patterns only in target, patterns in both
- Display results in three clearly labeled sections with distinct colors:
  - **Missing from target** (green) - patterns in template but not in target
  - **Extra in target** (yellow) - custom patterns in target but not in template
  - **Common patterns** (cyan) - patterns present in both files
- Add `--gitignore_compare_mode` CLI argument with choices: "diff" (default, maintains backward compatibility) or "set" (new mode)
- Update configuration, comparison logic, and documentation

## Relevant Files
Use these files to implement the feature:

- **cc_setup.py** (lines 553-598) - Contains `compare_gitignore()` method
  - Currently uses `difflib.unified_diff()` for comparison
  - Needs new set-based comparison logic
  - Lines 129-155: `SetupConfig` class needs new `gitignore_compare_mode` property
  - Lines 977-989: CLI argument parser needs new `--gitignore_compare_mode` argument
  - Lines 326-343: `read_gitignore_lines()` helper can be reused for reading files

- **README.md** (lines 149-268) - GitIgnore Management documentation
  - Lines 155-165: Compare operation documentation needs update
  - Needs new section explaining set-based comparison mode
  - Command-line options table (lines 67-76) needs new option
  - Examples section needs set-based comparison examples

### New Files
None required - all changes are extensions to existing files.

## Implementation Plan

### Phase 1: Foundation
Add infrastructure to support multiple comparison modes by extending the configuration system and CLI arguments. This includes adding the new `--gitignore_compare_mode` parameter and updating `SetupConfig` to store the comparison mode preference.

### Phase 2: Core Implementation
Implement the set-based comparison logic as a new method `compare_gitignore_set()` that performs hashtable-based analysis and displays results in three clearly labeled sections. Modify the existing `compare_gitignore()` to route to the appropriate comparison implementation based on the mode.

### Phase 3: Integration
Update the routing logic in `run_gitignore_operations()` to pass the comparison mode through, add comprehensive logging, update help text and documentation, and ensure backward compatibility (diff mode remains default).

## Step by Step Tasks

### Task 1: Add CLI Argument for Comparison Mode
- Add `--gitignore_compare_mode` argument to argparse in `main()` function
- Set choices to `["diff", "set"]` with default value `"diff"` for backward compatibility
- Add clear help text: "GitIgnore comparison mode: 'diff' for unified diff (default), 'set' for set-based comparison"
- Place argument after `--gitignore_execute` in the argument list

### Task 2: Extend SetupConfig Class
- Add `gitignore_compare_mode` property to `SetupConfig.__init__()`
- Initialize from `args.gitignore_compare_mode` with proper attribute checking
- Default to `"diff"` if attribute not present (defensive coding)
- Add comment explaining the two modes

### Task 3: Create Helper Method for Pattern Extraction
- Add `extract_gitignore_patterns(lines: List[str]) -> set[str]` method to CCSetup class
- Filter out empty lines: `line.strip() == ""`
- Filter out comment-only lines: `line.strip().startswith('#')`
- Return set of meaningful patterns (non-empty, non-comment lines)
- Handle edge cases: mixed lines with inline comments (keep the pattern part)
- Add comprehensive docstring explaining pattern extraction logic

### Task 4: Implement Set-Based Comparison Method
- Add `compare_gitignore_set() -> bool` method to CCSetup class
- Read template and target files using existing `read_gitignore_lines()`
- Extract patterns using new `extract_gitignore_patterns()` helper
- Calculate three sets:
  - `missing_from_target = template_patterns - target_patterns`
  - `extra_in_target = target_patterns - template_patterns`
  - `common_patterns = template_patterns & target_patterns`
- Return `True` if files are identical (all patterns common, no missing/extra)
- Return `False` if there are differences

### Task 5: Add Display Logic for Set-Based Comparison
- In `compare_gitignore_set()` method, add display logic after calculating sets
- Display header: `[bold]Set-Based Comparison:[/bold]`
- Show statistics summary:
  - Total patterns in template
  - Total patterns in target
  - Common patterns count
  - Missing from target count
  - Extra in target count
- Display three sections with clear labels and colors:
  - **Missing from Target** (green): patterns user should consider adding
    - Sort alphabetically for easy scanning
    - Prefix each with `+ ` to indicate addition suggestion
  - **Extra in Target** (yellow): custom patterns not in template
    - Sort alphabetically
    - Prefix with `! ` to indicate custom/extra
  - **Common Patterns** (cyan): patterns in both files
    - Sort alphabetically
    - Show count only by default, with option to list if verbose
- Handle empty sets gracefully (e.g., "None" or skip section)
- Log comparison results with statistics

### Task 6: Update Routing Logic in compare_gitignore
- Modify existing `compare_gitignore()` method to check comparison mode
- Add logic: `if self.config.gitignore_compare_mode == "set":`
- Route to `compare_gitignore_set()` for set mode
- Keep existing `difflib.unified_diff()` logic for diff mode
- Ensure both modes return consistent boolean (True if identical, False if different)
- Add logging to track which comparison mode was used

### Task 7: Update Display Header for Comparison Mode
- Modify `display_gitignore_header()` method
- Add comparison mode to the header display
- Show mode as: `Comparison Mode: [cyan]{mode.upper()}[/cyan]`
- Add explanation for set mode: `[dim](order-independent pattern comparison)[/dim]`
- Keep existing header format for other operations (merge, replace)

### Task 8: Add Unit Tests
- Create test cases for `extract_gitignore_patterns()`:
  - Test with empty file
  - Test with comments only
  - Test with mixed content (patterns + comments)
  - Test with inline comments (e.g., `*.pyc  # Python bytecode`)
  - Test with blank lines
- Create test cases for `compare_gitignore_set()`:
  - Test identical files (same patterns, different order)
  - Test completely different files
  - Test partial overlap (some common, some missing, some extra)
  - Test empty target file
  - Test empty template file
- Mock file I/O for isolated testing
- Verify color output and formatting

### Task 9: Update README Documentation
- Update "Compare (Default)" section (line 155-165) to mention both modes
- Add new subsection "Comparison Modes" after "Available Operations"
- Document diff mode (current behavior, good for seeing line-by-line changes)
- Document set mode (new behavior, good for semantic pattern comparison)
- Add command-line option to table (line 67-76):
  - `| --gitignore_compare_mode | | Comparison mode: 'diff' or 'set' (default: diff) |`
- Add examples showing set-based comparison:
  ```bash
  # Set-based comparison (order-independent)
  uv run cc_setup.py --target /path/to/project --gitignore python --gitignore_compare_mode set
  ```
- Add "When to use each mode" guidance section

### Task 10: Update Help Text and Examples
- Update argparse epilog in `main()` function
- Add example for set-based comparison
- Update help text to explain the difference between modes
- Add recommendation: "Use 'set' mode for order-independent comparison"

### Task 11: Test All Comparison Scenarios
- Test diff mode with identical files (should show "Files are identical")
- Test diff mode with different files (should show unified diff)
- Test set mode with identical files (should show "Files are identical")
- Test set mode with same patterns in different order (should show "Files are identical")
- Test set mode with missing patterns (should show green "+ pattern")
- Test set mode with extra patterns (should show yellow "! pattern")
- Test set mode with mixed differences (missing + extra + common)
- Verify backward compatibility (default mode is diff)
- Test invalid comparison mode (should error gracefully)

### Task 12: Validation and Documentation Review
- Run validation commands to ensure no regressions
- Verify help output shows new option
- Verify README has complete documentation
- Test that existing diff mode still works as before
- Test that new set mode provides clear, useful output
- Verify logging captures comparison mode and results

## Testing Strategy

### Unit Tests
- **Pattern Extraction**: Test `extract_gitignore_patterns()` with various input formats
  - Empty files, comment-only files, pattern-only files
  - Mixed content with comments and patterns
  - Lines with trailing/leading whitespace
  - Inline comments (pattern + comment on same line)
- **Set Operations**: Verify set difference, intersection, and union calculations
  - Identical sets (should report no differences)
  - Disjoint sets (should report all as differences)
  - Overlapping sets (should correctly identify missing/extra/common)
- **Display Logic**: Verify output formatting and color coding
  - Empty sections display correctly (or are skipped)
  - Patterns are sorted alphabetically
  - Correct color codes applied
- **Routing Logic**: Test that comparison mode selection works
  - Default mode is "diff"
  - Explicit "diff" mode uses unified diff
  - Explicit "set" mode uses set-based comparison

### Edge Cases
- Empty .gitignore files (both template and target)
- Target .gitignore doesn't exist (compare against empty set)
- Files with only comments (no actual patterns)
- Files with duplicate patterns (should deduplicate in set)
- Very large .gitignore files (performance testing)
- .gitignore files with unusual characters or encoding
- Files with Windows (CRLF) vs Unix (LF) line endings
- Patterns with leading/trailing whitespace
- Comment-only files vs empty files (should both be empty sets)
- Invalid comparison mode specified (should error with helpful message)

## Acceptance Criteria
- [ ] User can specify `--gitignore_compare_mode set` to use set-based comparison
- [ ] User can specify `--gitignore_compare_mode diff` to use traditional diff (or omit for default)
- [ ] Set mode displays three sections: Missing from Target (green), Extra in Target (yellow), Common Patterns (cyan)
- [ ] Set mode correctly identifies patterns regardless of order in file
- [ ] Set mode filters out comments and blank lines, comparing only actual patterns
- [ ] Diff mode continues to work as before (backward compatibility)
- [ ] Default comparison mode is "diff" (no breaking changes)
- [ ] Help text clearly explains both comparison modes
- [ ] README documents both modes with examples and usage guidance
- [ ] Patterns in each section are sorted alphabetically for easy reading
- [ ] Statistics summary shows counts for each category
- [ ] Both modes return consistent boolean values (True/False for identical/different)
- [ ] Logging captures which comparison mode was used
- [ ] No regressions in existing merge and replace operations

## Validation Commands
Execute every command to validate the feature works correctly with zero regressions.

### Test Set-Based Comparison
- `cd /d/python/cc_setup && mkdir -p test_set_compare && echo "*.pyc" > test_set_compare/.gitignore && echo "*.log" >> test_set_compare/.gitignore` - Create test file with patterns
- `uv run cc_setup.py --target test_set_compare --gitignore python --gitignore_compare_mode set` - Test set-based comparison
- Verify output shows:
  - Missing from Target section (patterns in template but not in target) - green
  - Extra in Target section (*.log, custom pattern not in template) - yellow
  - Statistics summary with counts
- `rm -rf test_set_compare` - Cleanup

### Test Set Mode with Reordered File
- `cd /d/python/cc_setup && mkdir -p test_reorder` - Create test directory
- `tail -r store/git/.gitignore_python > test_reorder/.gitignore` - Copy Python template in reverse order (or manually reorder)
- `uv run cc_setup.py --target test_reorder --gitignore python --gitignore_compare_mode set` - Test with reordered patterns
- Verify output shows "Files are identical" (same patterns, different order)
- `uv run cc_setup.py --target test_reorder --gitignore python --gitignore_compare_mode diff` - Compare with diff mode
- Verify diff mode shows many differences due to ordering
- `rm -rf test_reorder` - Cleanup

### Test Backward Compatibility (Diff Mode)
- `uv run cc_setup.py --target /d/python/cc_setup --gitignore python` - Test default mode (should be diff)
- `uv run cc_setup.py --target /d/python/cc_setup --gitignore python --gitignore_compare_mode diff` - Test explicit diff mode
- Verify unified diff output is displayed as before
- Verify no regression in existing diff behavior

### Test Help and Documentation
- `uv run cc_setup.py --help` - Verify new option documented
- Verify help text includes `--gitignore_compare_mode`
- Verify examples include set-based comparison
- `cat README.md | grep -A 10 "gitignore_compare_mode"` - Verify README has documentation

### Test Invalid Mode
- `uv run cc_setup.py --target test --gitignore python --gitignore_compare_mode invalid` - Test invalid mode
- Verify error message is clear and helpful

### Test Existing Operations Still Work
- `uv run cc_setup.py --target test_target --mode basic` - Test artifact management
- `uv run cc_setup.py --help-artifacts` - Test help artifacts
- `mkdir -p test_merge && uv run cc_setup.py --target test_merge --gitignore python --gitignore_execute merge` - Test merge operation
- Verify no regressions in existing functionality
- `rm -rf test_merge test_target` - Cleanup

## Notes

### Implementation Notes
- The `--gitignore_compare_mode` option only affects the `compare` operation (when `--gitignore_execute` is `compare` or omitted)
- Merge and replace operations are unaffected by comparison mode
- Set-based comparison is more performant for large files (O(n) vs O(n²) for diff)
- Pattern deduplication happens automatically with set data structure
- Comments are preserved in merge/replace but ignored in set comparison

### Design Decisions
- **Why default to "diff" mode?** Maintains backward compatibility; users who depend on current behavior won't see unexpected changes
- **Why two modes instead of replacing diff?** Some users may want to see line-by-line changes (e.g., to track comment changes); offering both provides flexibility
- **Why filter comments in set mode?** Comments don't affect .gitignore semantics; comparing only patterns provides clearer semantic comparison
- **Why sort output alphabetically?** Makes it easy to scan for specific patterns; groups related patterns together
- **Why three sections instead of two?** Showing "common patterns" provides context about overlap and helps users understand the relationship between files

### Future Enhancements
- Add `--verbose` flag to show common patterns list (currently only shows count)
- Support for negation patterns (!) and their semantic meaning
- Detect functionally equivalent patterns (e.g., `*.pyc` vs `**/*.pyc`)
- Add "smart merge" that understands pattern semantics
- Export comparison results to JSON format
- Support for .gitignore comments preservation in merge operations
- Interactive mode to selectively add/remove patterns
- Pattern validation against git's .gitignore rules

### Related Documentation
- Git .gitignore documentation: https://git-scm.com/docs/gitignore
- Python set operations: https://docs.python.org/3/library/stdtypes.html#set-types-set-frozenset
- Pattern matching considerations for future enhancements
