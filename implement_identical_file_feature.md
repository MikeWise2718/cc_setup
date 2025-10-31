# Implementation Plan: Identical File Detection Feature

**Date:** 2025-10-31
**Purpose:** Add file comparison to detect when existing files are identical to source files

---

## Overview

Currently, when `cc_setup.py` encounters an existing file in the target directory, it simply marks it as "⚠ Exists" and skips it (unless `--overwrite` is used). This feature will enhance the tool to compare existing files with source files and distinguish between:

1. **Identical files**: Existing file matches source exactly (no action needed)
2. **Different files**: Existing file differs from source (may need update)

This provides better visibility into which files are already up-to-date vs. which ones have diverged.

---

## User Benefits

### Better Decision Making
- Users can see which files are already current
- Easier to identify which files might need updating
- Reduces unnecessary overwrites of identical files

### Improved Visibility
- Clear distinction between "up-to-date" and "needs update"
- Helps identify configuration drift
- Better understanding of project state

### Workflow Optimization
- Skip overwriting files that are already correct
- Focus attention on files that actually differ
- Faster dry-run analysis

---

## Design Specifications

### File Comparison Method

**Option A: Content Hash (SHA-256)**
```python
import hashlib

def get_file_hash(file_path: Path) -> str:
    """Calculate SHA-256 hash of file contents."""
    sha256 = hashlib.sha256()
    with open(file_path, 'rb') as f:
        while chunk := f.read(8192):
            sha256.update(chunk)
    return sha256.hexdigest()

def files_are_identical(source: Path, target: Path) -> bool:
    """Check if two files have identical content."""
    return get_file_hash(source) == get_file_hash(target)
```

**Pros:**
- Fast for large files (only reads each file once)
- Accurate even for binary files
- Can cache hashes if needed

**Cons:**
- Slightly more complex
- Small overhead for tiny files

**Option B: Direct Byte Comparison**
```python
def files_are_identical(source: Path, target: Path) -> bool:
    """Check if two files have identical content."""
    with open(source, 'rb') as f1, open(target, 'rb') as f2:
        return f1.read() == f2.read()
```

**Pros:**
- Simple implementation
- Works for all file types

**Cons:**
- Loads entire files into memory
- May be slower for large files

**Recommendation**: Use **Option A (Content Hash)** for better performance and scalability.

---

## Status Indicators

### Current Status System
```python
"✓ New"       # File doesn't exist in target
"⚠ Exists"    # File exists in target (will skip)
"⚠ Overwrite" # File exists and will be overwritten
"✗ Missing"   # Source file doesn't exist
```

### Enhanced Status System
```python
"✓ New"       # File doesn't exist in target
"✓ Identical" # File exists and is identical to source (NEW)
"⚠ Different" # File exists but differs from source (ENHANCED)
"⚠ Overwrite" # File exists and will be overwritten
"✗ Missing"   # Source file doesn't exist
```

### Color Coding
- `✓ New` - **Green**: Will be copied
- `✓ Identical` - **Cyan/Blue**: Already up-to-date, no action needed
- `⚠ Different` - **Yellow**: Exists but differs, will skip (or overwrite with flag)
- `⚠ Overwrite` - **Red**: Will overwrite different file
- `✗ Missing` - **Red Dim**: Source missing, will skip

---

## Action Messages

### Current Actions
```python
"Will copy"        # New file will be copied
"Skip"             # Existing file will be skipped
"Will overwrite"   # Existing file will be overwritten
"Skip (missing)"   # Source missing
```

### Enhanced Actions
```python
"Will copy"              # New file will be copied
"Skip (identical)"       # File is already up-to-date (NEW)
"Skip (different)"       # File differs but skip mode (ENHANCED)
"Will overwrite"         # File differs, overwrite enabled
"Skip (missing)"         # Source missing
```

---

## Statistics Updates

### Current Statistics
```python
self.files_to_copy = 0      # New files to copy
self.files_exist = 0        # Files that exist
self.files_to_overwrite = 0 # Files to overwrite
self.files_skipped = 0      # Files skipped (execution)
self.files_copied = 0       # Files copied (execution)
```

### Enhanced Statistics
```python
self.files_to_copy = 0      # New files to copy
self.files_exist = 0        # Files that exist (total)
self.files_identical = 0    # Files that are identical (NEW)
self.files_different = 0    # Files that are different (NEW)
self.files_to_overwrite = 0 # Files to overwrite
self.files_skipped = 0      # Files skipped (execution)
self.files_copied = 0       # Files copied (execution)
```

### Summary Panel Updates

**Current:**
```
• 51 new files to copy
• 0 files already exist (will skip)
• 0 files will be overwritten
```

**Enhanced:**
```
• 45 new files to copy
• 5 files identical (already up-to-date)
• 1 file different (will skip)
• 0 files will be overwritten
```

---

## Code Changes

### Phase 1: Add File Comparison Utility

**Location**: New utility function in `CCSetup` class

```python
import hashlib

def get_file_hash(self, file_path: Path) -> str:
    """Calculate SHA-256 hash of file contents.

    Args:
        file_path: Path to file to hash

    Returns:
        Hexadecimal string of SHA-256 hash

    Raises:
        OSError: If file cannot be read
    """
    try:
        sha256 = hashlib.sha256()
        with open(file_path, 'rb') as f:
            while chunk := f.read(8192):
                sha256.update(chunk)
        return sha256.hexdigest()
    except OSError as e:
        self.logger.warning(f"Failed to hash {file_path}: {e}")
        raise

def files_are_identical(self, source: Path, target: Path) -> bool:
    """Check if two files have identical content.

    Args:
        source: Source file path
        target: Target file path

    Returns:
        True if files are identical, False otherwise

    Note:
        Returns False if either file cannot be read
    """
    try:
        return self.get_file_hash(source) == self.get_file_hash(target)
    except OSError:
        return False
```

### Phase 2: Update FileOperation Class

**Current `__init__`:**
```python
def __init__(self, artifact: ArtifactDefinition, source_path: Path,
             target_path: Path, exists: bool, will_copy: bool, will_overwrite: bool):
    self.artifact = artifact
    self.source_path = source_path
    self.target_path = target_path
    self.exists = exists
    self.will_copy = will_copy
    self.will_overwrite = will_overwrite
    self.status = self._determine_status()
```

**Enhanced `__init__`:**
```python
def __init__(self, artifact: ArtifactDefinition, source_path: Path,
             target_path: Path, exists: bool, is_identical: bool,
             will_copy: bool, will_overwrite: bool):
    self.artifact = artifact
    self.source_path = source_path
    self.target_path = target_path
    self.exists = exists
    self.is_identical = is_identical  # NEW
    self.will_copy = will_copy
    self.will_overwrite = will_overwrite
    self.status = self._determine_status()
```

**Current `_determine_status`:**
```python
def _determine_status(self) -> str:
    """Determine the status indicator."""
    if self.will_overwrite:
        return "⚠ Overwrite"
    elif self.exists and not self.will_copy:
        return "⚠ Exists"
    elif not self.source_path.exists():
        return "✗ Missing"
    else:
        return "✓ New"
```

**Enhanced `_determine_status`:**
```python
def _determine_status(self) -> str:
    """Determine the status indicator."""
    if not self.source_path.exists():
        return "✗ Missing"
    elif self.will_overwrite:
        return "⚠ Overwrite"
    elif self.exists:
        if self.is_identical:
            return "✓ Identical"  # NEW
        else:
            return "⚠ Different"  # ENHANCED
    else:
        return "✓ New"
```

**Current `get_action`:**
```python
def get_action(self, execute: bool) -> str:
    """Get the action description."""
    if not self.source_path.exists():
        return "Skip (missing)"
    elif self.will_overwrite:
        return "Overwriting" if execute else "Will overwrite"
    elif self.will_copy:
        return "Copying" if execute else "Will copy"
    else:
        return "Skipping" if execute else "Skip"
```

**Enhanced `get_action`:**
```python
def get_action(self, execute: bool) -> str:
    """Get the action description."""
    if not self.source_path.exists():
        return "Skip (missing)"
    elif self.will_overwrite:
        return "Overwriting" if execute else "Will overwrite"
    elif self.will_copy:
        return "Copying" if execute else "Will copy"
    else:
        # File exists and won't be copied
        if self.is_identical:
            return "Skipping (identical)" if execute else "Skip (identical)"  # NEW
        else:
            return "Skipping (different)" if execute else "Skip (different)"  # ENHANCED
```

### Phase 3: Update SetupConfig Class

Add new statistics:

```python
class SetupConfig:
    """Configuration for the setup process."""

    def __init__(self, args):
        self.target_dir = Path(args.target) if args.target else None
        self.mode = args.mode
        self.execute = args.execute
        self.overwrite = args.overwrite
        self.show_help_artifacts = args.help_artifacts

        # Statistics
        self.files_to_copy = 0
        self.files_exist = 0
        self.files_identical = 0      # NEW
        self.files_different = 0      # NEW
        self.files_to_overwrite = 0
        self.files_skipped = 0
        self.files_copied = 0
```

### Phase 4: Update analyze_operations Method

**Current:**
```python
def analyze_operations(self) -> None:
    """Analyze what operations would be performed."""
    artifacts = self.artifact_store.get_artifacts(self.config.mode)

    for artifact in artifacts:
        source_path = artifact.source_path
        target_path = self.config.target_dir / artifact.target_subdir / artifact.filename

        exists = target_path.exists()
        will_copy = (not exists or self.config.overwrite) and source_path.exists()
        will_overwrite = exists and self.config.overwrite and source_path.exists()

        operation = FileOperation(artifact, source_path, target_path,
                                 exists, will_copy, will_overwrite)
        self.operations.append(operation)

        # Update statistics
        if will_copy and not will_overwrite:
            self.config.files_to_copy += 1
        if exists:
            self.config.files_exist += 1
        if will_overwrite:
            self.config.files_to_overwrite += 1
```

**Enhanced:**
```python
def analyze_operations(self) -> None:
    """Analyze what operations would be performed."""
    artifacts = self.artifact_store.get_artifacts(self.config.mode)

    for artifact in artifacts:
        source_path = artifact.source_path
        target_path = self.config.target_dir / artifact.target_subdir / artifact.filename

        exists = target_path.exists()

        # Check if files are identical (NEW)
        is_identical = False
        if exists and source_path.exists():
            is_identical = self.files_are_identical(source_path, target_path)

        will_copy = (not exists or self.config.overwrite) and source_path.exists()
        will_overwrite = exists and self.config.overwrite and source_path.exists()

        operation = FileOperation(artifact, source_path, target_path,
                                 exists, is_identical, will_copy, will_overwrite)
        self.operations.append(operation)

        # Update statistics (ENHANCED)
        if will_copy and not will_overwrite:
            self.config.files_to_copy += 1
        if exists:
            self.config.files_exist += 1
            if is_identical:
                self.config.files_identical += 1  # NEW
            else:
                self.config.files_different += 1  # NEW
        if will_overwrite:
            self.config.files_to_overwrite += 1
```

### Phase 5: Update display_operations_table Method

**Current row styling:**
```python
for op in self.operations:
    # Determine row style
    if op.will_overwrite:
        style = "red"
    elif op.exists and not op.will_copy:
        style = "yellow"
    elif not op.source_path.exists():
        style = "red dim"
    else:
        style = "green"
```

**Enhanced row styling:**
```python
for op in self.operations:
    # Determine row style (ENHANCED)
    if not op.source_path.exists():
        style = "red dim"
    elif op.will_overwrite:
        style = "red"
    elif op.exists:
        if op.is_identical:
            style = "cyan"           # NEW: Cyan for identical
        else:
            style = "yellow"         # Yellow for different
    else:
        style = "green"              # Green for new
```

### Phase 6: Update display_summary Method

**Current:**
```python
def display_summary(self) -> None:
    """Display summary panel."""
    total_new = self.config.files_to_copy
    total_exists = self.config.files_exist - self.config.files_to_overwrite
    total_overwrite = self.config.files_to_overwrite

    if self.config.execute:
        summary_text = f"""[bold]Execution Complete[/bold]

• [green]{self.config.files_copied}[/green] files copied
• [yellow]{self.config.files_skipped}[/yellow] files skipped (already exist)
• [red]{self.config.files_to_overwrite}[/red] files overwritten"""
    else:
        summary_text = f"""[bold]Analysis Summary[/bold]

• [green]{total_new}[/green] new files to copy
• [yellow]{total_exists}[/yellow] files already exist (will skip)
• [red]{total_overwrite}[/red] files will be overwritten"""
```

**Enhanced:**
```python
def display_summary(self) -> None:
    """Display summary panel."""
    total_new = self.config.files_to_copy
    total_identical = self.config.files_identical
    total_different = self.config.files_different
    total_overwrite = self.config.files_to_overwrite

    if self.config.execute:
        summary_text = f"""[bold]Execution Complete[/bold]

• [green]{self.config.files_copied}[/green] files copied
• [cyan]{total_identical}[/cyan] files identical (skipped)
• [yellow]{self.config.files_skipped - total_identical}[/yellow] files different (skipped)
• [red]{self.config.files_to_overwrite}[/red] files overwritten"""
    else:
        summary_text = f"""[bold]Analysis Summary[/bold]

• [green]{total_new}[/green] new files to copy
• [cyan]{total_identical}[/cyan] files identical (already up-to-date)
• [yellow]{total_different}[/yellow] files different (will skip)
• [red]{total_overwrite}[/red] files will be overwritten"""
```

### Phase 7: Update Logging

Add comparison results to log:

```python
# In analyze_operations method, after creating FileOperation
self.logger.info(
    f"{op.artifact.category}: {op.artifact.filename} - "
    f"{op.status} - {op.get_action(False)}"
    f"{' (identical)' if op.is_identical else ''}"  # NEW
)
```

---

## Performance Considerations

### File Size Impact

**Small files (< 1MB):**
- SHA-256 hashing is very fast
- Negligible performance impact
- Most Claude Code artifacts are small

**Large files (> 10MB):**
- Still fast (SHA-256 is optimized)
- Read in 8KB chunks to manage memory
- No significant user-facing delay

### Benchmark Estimates

```
File Size   | Hash Time | Impact
------------|-----------|------------------
1 KB        | < 0.1ms   | Imperceptible
10 KB       | < 0.5ms   | Imperceptible
100 KB      | < 2ms     | Imperceptible
1 MB        | ~15ms     | Barely noticeable
10 MB       | ~150ms    | Noticeable but acceptable
```

For cc_setup artifacts (mostly text files < 100KB), total comparison overhead for 50 files would be < 100ms.

### Optimization Strategies

**1. Skip Comparison for New Files**
```python
# Only compare if file exists
if exists and source_path.exists():
    is_identical = self.files_are_identical(source_path, target_path)
else:
    is_identical = False
```

**2. Quick Size Check First (Optional)**
```python
def files_might_differ(self, source: Path, target: Path) -> bool:
    """Quick check if files might differ based on size."""
    return source.stat().st_size != target.stat().st_size

def files_are_identical(self, source: Path, target: Path) -> bool:
    """Check if two files have identical content."""
    # Quick size check first
    if self.files_might_differ(source, target):
        return False
    # Full hash comparison
    return self.get_file_hash(source) == self.get_file_hash(target)
```

**3. Parallel Hashing (Advanced, Optional)**
- Use ThreadPoolExecutor to hash multiple files concurrently
- Only beneficial for many files or very large files
- Adds complexity, probably not needed for cc_setup

---

## Testing Strategy

### Unit Tests

**Test 1: Identical Files**
```python
def test_identical_files():
    # Create two identical files
    source = tmp_path / "source.txt"
    target = tmp_path / "target.txt"
    content = "Hello, World!"
    source.write_text(content)
    target.write_text(content)

    # Should detect as identical
    assert files_are_identical(source, target) == True
```

**Test 2: Different Files**
```python
def test_different_files():
    source = tmp_path / "source.txt"
    target = tmp_path / "target.txt"
    source.write_text("Version 1")
    target.write_text("Version 2")

    # Should detect as different
    assert files_are_identical(source, target) == False
```

**Test 3: Binary Files**
```python
def test_binary_files():
    source = tmp_path / "source.bin"
    target = tmp_path / "target.bin"
    source.write_bytes(b'\x00\x01\x02\x03')
    target.write_bytes(b'\x00\x01\x02\x03')

    # Should work with binary
    assert files_are_identical(source, target) == True
```

**Test 4: Status Indicators**
```python
def test_status_identical():
    # Existing file, identical
    op = FileOperation(artifact, source, target, exists=True,
                      is_identical=True, will_copy=False, will_overwrite=False)
    assert op.status == "✓ Identical"

def test_status_different():
    # Existing file, different
    op = FileOperation(artifact, source, target, exists=True,
                      is_identical=False, will_copy=False, will_overwrite=False)
    assert op.status == "⚠ Different"
```

### Integration Tests

**Test 1: First Run (All New)**
```bash
# All files should be marked as "✓ New"
uv run cc_setup.py --target ./test --mode basic
# Verify: 51 new files to copy
```

**Test 2: Second Run (All Identical)**
```bash
# First run
uv run cc_setup.py --target ./test --mode basic --execute
# Second run
uv run cc_setup.py --target ./test --mode basic
# Verify: 51 files identical (already up-to-date)
```

**Test 3: Modified Files**
```bash
# First run
uv run cc_setup.py --target ./test --mode basic --execute
# Modify one file
echo "modified" >> ./test/.claude/hooks/notification.py
# Second run
uv run cc_setup.py --target ./test --mode basic
# Verify: 50 identical, 1 different
```

**Test 4: Overwrite Different Files**
```bash
# Modify file
echo "modified" >> ./test/.claude/hooks/notification.py
# Run with overwrite
uv run cc_setup.py --target ./test --mode basic --execute --overwrite
# Verify: File restored to original
```

---

## Edge Cases

### Case 1: File Exists but Unreadable
```python
def files_are_identical(self, source: Path, target: Path) -> bool:
    try:
        return self.get_file_hash(source) == self.get_file_hash(target)
    except (OSError, PermissionError) as e:
        self.logger.warning(f"Cannot compare {target}: {e}")
        return False  # Treat as different
```

### Case 2: Source Missing
```python
# Already handled by existing logic
if not source_path.exists():
    is_identical = False
```

### Case 3: Target Missing (New File)
```python
# Skip comparison for new files
if not exists:
    is_identical = False
```

### Case 4: Symlinks
```python
def get_file_hash(self, file_path: Path) -> str:
    # Follow symlinks (default behavior)
    with open(file_path, 'rb') as f:
        # Compares target of symlink, not symlink itself
```

---

## User Documentation Updates

### README.md Changes

**Add section under "Output Explained":**

```markdown
### File Status Indicators

The tool compares existing files with source files to determine their status:

- **✓ New** (Green): File doesn't exist in target, will be copied
- **✓ Identical** (Cyan): File exists and matches source exactly (already up-to-date)
- **⚠ Different** (Yellow): File exists but differs from source (will skip unless --overwrite)
- **⚠ Overwrite** (Red): File exists and will be overwritten (--overwrite flag)
- **✗ Missing** (Red Dim): Source file not found

This helps you understand which files are current vs. which may need updating.
```

**Update "File Handling" section:**

```markdown
## File Handling

### Default Behavior (No Overwrite)

- **New files**: Copied to target
- **Identical files**: Skipped (already up-to-date)
- **Different files**: Skipped (not modified)

### With `--overwrite` Flag

- **New files**: Copied to target
- **Identical files**: Skipped (no need to overwrite)
- **Different files**: Overwritten with source version
```

---

## Implementation Checklist

### Code Changes
- [ ] Add `hashlib` import
- [ ] Implement `get_file_hash()` method
- [ ] Implement `files_are_identical()` method
- [ ] Update `FileOperation.__init__()` signature
- [ ] Update `FileOperation._determine_status()`
- [ ] Update `FileOperation.get_action()`
- [ ] Add `files_identical` and `files_different` to `SetupConfig`
- [ ] Update `analyze_operations()` to perform comparison
- [ ] Update `display_operations_table()` row styling
- [ ] Update `display_summary()` with new statistics
- [ ] Update logging to include comparison results

### Testing
- [ ] Test with all new files
- [ ] Test with all identical files
- [ ] Test with mix of identical and different files
- [ ] Test with binary files
- [ ] Test with large files (> 1MB)
- [ ] Test with missing source files
- [ ] Test with unreadable target files
- [ ] Test overwrite behavior with different files
- [ ] Verify statistics are accurate
- [ ] Verify log output is correct

### Documentation
- [ ] Update README.md with new status indicators
- [ ] Update README.md file handling section
- [ ] Update inline code comments
- [ ] Add docstrings to new methods

### Performance
- [ ] Benchmark with 50+ files
- [ ] Verify no significant slowdown
- [ ] Test with large files (10MB+)
- [ ] Monitor memory usage

---

## Example Output

### Before Enhancement

```
┌──────────┬─────────────────┬───────────┬──────────┐
│ Category │ File            │ Status    │ Action   │
├──────────┼─────────────────┼───────────┼──────────┤
│ Settings │ settings.json   │ ⚠ Exists  │ Skip     │
│ Hooks    │ notification.py │ ⚠ Exists  │ Skip     │
└──────────┴─────────────────┴───────────┴──────────┘

• 0 new files to copy
• 2 files already exist (will skip)
```

### After Enhancement

```
┌──────────┬─────────────────┬──────────────┬──────────────────┐
│ Category │ File            │ Status       │ Action           │
├──────────┼─────────────────┼──────────────┼──────────────────┤
│ Settings │ settings.json   │ ✓ Identical  │ Skip (identical) │
│ Hooks    │ notification.py │ ⚠ Different  │ Skip (different) │
└──────────┴─────────────────┴──────────────┴──────────────────┘

• 0 new files to copy
• 1 file identical (already up-to-date)
• 1 file different (will skip)
```

---

## Benefits Summary

### For Users
1. **Better Visibility**: Know which files are current vs. outdated
2. **Informed Decisions**: Decide which files need updating
3. **Confidence**: See that files are already up-to-date
4. **Tracking**: Identify when local modifications exist

### For Workflows
1. **Skip Unnecessary Overwrites**: Don't overwrite identical files
2. **Detect Drift**: Find files that have diverged from source
3. **Validation**: Verify installations are correct
4. **Updates**: Easily see what needs refreshing

---

## Timeline Estimate

- **Phase 1-2**: File comparison utility and FileOperation updates - 1-2 hours
- **Phase 3-4**: Statistics and analyze_operations updates - 1 hour
- **Phase 5-6**: Display updates and logging - 1 hour
- **Phase 7**: Testing and edge cases - 2 hours
- **Documentation**: README updates - 30 minutes

**Total**: ~5-6 hours

---

## Future Enhancements

### Detailed Diff Display
Show actual differences for text files:
```bash
uv run cc_setup.py --target ./test --mode basic --show-diffs
```

### Comparison Report
Generate detailed report of all differences:
```
store/comparison_report_20251031.txt
```

### Selective Overwrite
Interactively choose which different files to overwrite:
```bash
uv run cc_setup.py --target ./test --mode basic --interactive
```

### Size-Based Optimization
Skip comparison for very large files to save time.

---

## Summary

This feature adds intelligent file comparison to cc_setup, distinguishing between files that are:
- **New** (need to be copied)
- **Identical** (already up-to-date)
- **Different** (may need updating)

The implementation is straightforward, performant, and provides significant value to users by improving visibility into file states and enabling better decision-making about updates and overwrites.
