# Feature: Enhanced CLI Output with Version Info and Improved Error Handling

## Metadata
issue_number: `0`
adw_id: `0`
issue_json: `{"title": "Enhanced CLI Output with Version Info and Improved Error Handling", "body": "I am not happy with this default prompt. I would like cc_setup to display it's version number, and its install date. Also if there is an error, I woudl like the error message to be in red, with the missing parameters somehow highlighted. I suspect this will need a custom error handler."}`

## Feature Description
Enhance the cc_setup CLI tool with improved user experience through better version information display and enhanced error messaging. The feature will add version and installation date display to the CLI output, and implement a custom error handler that presents validation errors in a visually appealing format with red-colored error messages and highlighted missing parameter names.

## User Story
As a cc_setup user
I want to see version and installation information clearly displayed
So that I can verify which version is installed and when it was installed, and understand CLI errors more easily with clear, highlighted error messages

## Problem Statement
Currently, the cc_setup tool lacks clear version identification and installation tracking, making it difficult for users to know which version they are using. Additionally, argparse's default error messages are plain text without color highlighting, making it harder for users to quickly identify what parameters are missing or incorrect when they make command-line mistakes. The error message shown in the screenshot demonstrates this issue - while functional, it lacks visual emphasis and doesn't clearly highlight the specific missing parameter.

## Solution Statement
Implement three key enhancements:

1. **Version Display**: Add a `--version` / `-v` flag that displays the current cc_setup version from pyproject.toml
2. **Install Date Tracking**: Store and display the installation date by creating a metadata file during package installation that records when the tool was installed
3. **Custom Error Handler**: Replace argparse's default error handler with a custom implementation that:
   - Displays error messages in red using rich console
   - Highlights parameter names (like `--target`) in a contrasting color
   - Provides a more visually distinct error format
   - Maintains all existing error validation logic

This approach leverages the existing Rich library already used throughout the codebase for consistent, beautiful terminal output.

## Relevant Files
Use these files to implement the feature:

- **cc_setup.py:1394-1491** - Main entry point and argument parsing logic
  - Contains the main() function where argparse is configured
  - This is where we'll add the --version flag
  - This is where we'll implement the custom error handler by subclassing ArgumentParser

- **cc_setup.py:31-60** - OperationLogger class with _read_version() method
  - Already has logic to read version from pyproject.toml
  - We can extract this into a standalone utility function for reuse in main()

- **pyproject.toml:1-35** - Project configuration
  - Contains the version number (currently 0.6.1) that needs to be displayed
  - Contains the project.scripts entry point configuration

- **cc_setup.py:1-29** - Module imports and setup
  - Where we'll add any new imports needed for install date tracking
  - Already imports rich.console.Console for colored output

### New Files
- **cc_setup_metadata.json** - Installation metadata file (created in package directory)
  - Stores installation timestamp
  - Format: `{"installed_at": "2025-11-09T10:30:00+00:00"}`
  - Created during first run or installation
  - Located in the same directory as cc_setup.py

## Implementation Plan

### Phase 1: Foundation
Add utility functions for version and install date management:
- Extract version reading logic from OperationLogger into a standalone function
- Create functions to read/write installation metadata
- Ensure metadata file is created if it doesn't exist

### Phase 2: Core Implementation
Implement the three main features:
- Add --version flag to display version and install date
- Create custom ArgumentParser subclass with enhanced error formatting
- Integrate custom error handler into the main() function

### Phase 3: Integration
Connect all pieces and ensure consistent behavior:
- Replace default ArgumentParser with custom subclass
- Test all error scenarios to ensure proper formatting
- Verify version display works correctly
- Update help text if needed

## Step by Step Tasks

### Extract and create version utilities
- Extract the version reading logic from OperationLogger._read_version() into a standalone function get_version()
- Create function get_install_date() that reads from cc_setup_metadata.json
- Create function set_install_date() that writes to cc_setup_metadata.json with current timestamp
- Place these utility functions near the top of cc_setup.py after imports

### Implement install date tracking
- Modify the main() function to call set_install_date() on first run (if metadata file doesn't exist)
- Ensure cc_setup_metadata.json is created in the same directory as cc_setup.py
- Handle exceptions gracefully if file creation fails (don't break the tool)

### Create custom ArgumentParser with enhanced error handling
- Create a new class CustomArgumentParser that inherits from argparse.ArgumentParser
- Override the error() method to provide custom formatting
- Use rich console to display errors in red
- Parse error messages to identify and highlight parameter names (anything starting with -- or -)
- Format error messages in a Panel or with special formatting for visual distinction

### Add --version flag
- Add --version / -v argument to the argument parser
- When --version is used, display formatted output showing:
  - Tool name: "cc_setup"
  - Version from pyproject.toml
  - Install date from metadata file (or "unknown" if not available)
  - Exit gracefully after displaying version info
- Use rich Panel or formatted text for attractive display

### Update main() to use custom parser
- Replace argparse.ArgumentParser instantiation with CustomArgumentParser
- Ensure all existing arguments continue to work
- Test that error messages now display in red with highlighted parameters

### Update OperationLogger to use shared version function
- Modify OperationLogger._read_version() to call the new shared get_version() function
- This ensures version reading logic is centralized and consistent

### Testing
- Test --version flag displays correct information
- Test missing --target parameter shows red error with highlighted "--target"
- Test missing --mode parameter shows red error with highlighted "--mode"
- Test invalid --mode value shows red error with helpful message
- Test that normal operations still work correctly
- Test install date is created and persists correctly

### Validation
- Run all validation commands to ensure no regressions

## Testing Strategy

### Unit Tests
No unit tests exist for this Python project currently. Testing will be manual and validation-based.

### Edge Cases
- **Missing metadata file**: Tool should create it on first run and continue working
- **Corrupted metadata file**: Tool should handle JSON parse errors gracefully
- **Version not in pyproject.toml**: Tool should display "unknown" version
- **Missing pyproject.toml**: Tool should handle this gracefully with "unknown" version
- **Various error scenarios**: Test all common user errors (missing target, missing mode, invalid mode, etc.)
- **--version with other arguments**: --version should take precedence and display version then exit

## Acceptance Criteria
- [ ] Running `cc_setup --version` or `cc_setup -v` displays version number and install date in a formatted panel
- [ ] Running `cc_setup` without required arguments shows error message in red color
- [ ] Missing parameter names (like `--target`) are highlighted in error messages with a distinct color
- [ ] Install date is tracked and persists across runs in cc_setup_metadata.json
- [ ] Install date file is created automatically on first run if it doesn't exist
- [ ] All existing functionality continues to work without regressions
- [ ] Error messages are more visually distinct and easier to read than default argparse errors
- [ ] Version information can be displayed without needing a --target directory
- [ ] The custom error handler works for all existing validation errors (missing target, missing mode, etc.)

## Validation Commands
Execute every command to validate the feature works correctly with zero regressions.

### Test version display
```bash
# Test --version flag (long form)
uv run cc_setup --version

# Test -v flag (short form)
uv run cc_setup -v
```

### Test error messages with missing parameters
```bash
# Test missing --target (should show red error with "--target" highlighted)
uv run cc_setup --mode basic

# Test missing --mode (should show red error with "--mode" highlighted)
uv run cc_setup --target test_target

# Test missing both --target and --mode (should show red error)
uv run cc_setup
```

### Test error messages with invalid values
```bash
# Test invalid --mode value (should show red error with helpful message)
uv run cc_setup --target test_target --mode invalid
```

### Test normal operations still work
```bash
# Test dry run still works
uv run cc_setup --target test_target --mode basic

# Test help flags still work
uv run cc_setup --help
uv run cc_setup --help-artifacts
uv run cc_setup --help-examples
```

### Verify metadata file creation
```bash
# Check that metadata file was created
cat cc_setup_metadata.json

# Verify it contains valid JSON with installed_at field
python -c "import json; print(json.load(open('cc_setup_metadata.json')))"
```

## Notes
- The install date will be tracked from the first time the tool is run, not the actual pip/uv installation time (since we can't hook into the installation process easily)
- Using Rich library for error formatting ensures consistency with the rest of the tool's output
- The metadata file should be excluded from git tracking (add to .gitignore if needed)
- Consider whether the metadata file should be excluded from the wheel distribution (currently it would be excluded by the existing *.md exclusion pattern, but .json files are not explicitly excluded)
- The custom error handler should preserve all of argparse's existing validation behavior - we're only changing the presentation, not the logic
- Parameter highlighting in error messages should work for both long-form (--target) and short-form (-t) parameter names
