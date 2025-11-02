# Chore: Switch out argparse for rich-argparse

## Metadata
issue_number: `N/A`
adw_id: `N/A`
issue_json: `{"title": "switch out argparse for rich-argparse", "body": "The argparse library does not make good use of color, when for example a required parameter is missing. Should we be using a different library maybe? Or can we somehow add color to argparse?"}`

## Chore Description
Replace the standard argparse library with rich-argparse to provide colorful, visually appealing help text and error messages. The current argparse implementation lacks color formatting for error messages (e.g., when required parameters are missing), making the CLI less user-friendly. Since the project already uses the `rich` library extensively for terminal output, integrating `rich-argparse` is a natural fit that requires minimal code changes while providing significant UX improvements.

## Relevant Files
Use these files to resolve the chore:

- **cc_setup.py:576-646** - Contains the main argument parser setup
  - Lines 578-595 define the ArgumentParser and its configuration
  - Lines 597-625 define all command-line arguments
  - Lines 627-642 handle argument parsing and validation logic
  - This is the only file that needs modification for this chore

- **pyproject.toml:1-17** - Project dependency configuration
  - Lines 7-9 contain the dependencies list where `rich-argparse` needs to be added
  - Currently only lists `rich>=13.0.0` as a dependency

- **README.md:294-297** - Requirements documentation
  - Lines 294-297 list the project requirements
  - Should be reviewed to ensure documentation accuracy after the change

## Step by Step Tasks
IMPORTANT: Execute every step in order, top to bottom.

### Step 1: Add rich-argparse dependency
- Open `pyproject.toml`
- Add `rich-argparse>=1.0.0` to the dependencies list (after the existing `rich` dependency)
- Save the file

### Step 2: Install the new dependency
- Run `uv sync` to install the newly added `rich-argparse` package
- Verify the installation completes successfully

### Step 3: Update cc_setup.py imports
- Open `cc_setup.py`
- Add `from rich_argparse import RichHelpFormatter` to the imports section (around line 7-21 where other imports are)
- Keep all existing imports intact

### Step 4: Update ArgumentParser to use RichHelpFormatter
- In `cc_setup.py`, locate the `main()` function (line 576)
- Find the `argparse.ArgumentParser()` instantiation (line 578)
- Change `formatter_class=argparse.RawDescriptionHelpFormatter` to `formatter_class=RichHelpFormatter`
- Ensure all other ArgumentParser parameters remain unchanged

### Step 5: Test the changes with various scenarios
- Run `uv run cc_setup.py --help` to verify colorful help output
- Run `uv run cc_setup.py` (without arguments) to verify colorful error messages for missing required parameters
- Run `uv run cc_setup.py --help-artifacts` to ensure the special case still works
- Run `uv run cc_setup.py --target test_target2 --mode basic` (dry run) to verify normal operation works
- Verify all outputs display properly with rich formatting

## Validation Commands
Execute every command to validate the chore is complete with zero regressions.

- `uv sync` - Ensure all dependencies are installed correctly
- `uv run cc_setup.py --help` - Verify help text displays with rich formatting and no errors
- `uv run cc_setup.py` - Verify missing required arguments show colorful error message
- `uv run cc_setup.py --help-artifacts` - Verify the help-artifacts special case works correctly
- `uv run cc_setup.py --target test_target2 --mode basic` - Verify dry-run mode works with no errors
- `uv run cc_setup.py --target test_target2 --mode basic --execute` - Verify execute mode works with no errors

## Notes
- The `rich-argparse` library is specifically designed to work seamlessly with the `rich` library already used in this project
- This change requires only minimal code modifications: adding one import and changing one parameter
- The `RichHelpFormatter` is a drop-in replacement for `argparse.RawDescriptionHelpFormatter`, so it will preserve the existing epilog formatting
- No changes to argument definitions are required - all existing arguments will automatically benefit from rich formatting
- The change is backward compatible and won't affect the tool's functionality, only its visual presentation
- Rich-argparse will automatically colorize argument names, descriptions, metavars, and error messages
