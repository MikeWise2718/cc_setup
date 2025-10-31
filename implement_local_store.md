# Implementation Plan: Local Store Architecture

**Date:** 2025-10-31
**Purpose:** Redesign cc_setup to use local artifact storage instead of external d:\tac repositories

---

## Current Architecture Analysis

### Current Design
- **Source Location:** External repositories at `d:\tac\tac-6` and `d:\tac\tac-7`
- **Artifact Definition:** Hard-coded in Python classes (`ArtifactDefinition`, `ArtifactMap`)
- **Discovery:** No discovery - artifacts are explicitly listed in code
- **Issues:**
  - Dependency on external file structure
  - Hard-coded artifact lists that may not match reality
  - Showing "missing" files when they don't exist in source
  - Users need specific directory structure at `d:\tac`

### Current Code Structure
```python
ArtifactDefinition(filename, source_repo, category, target_subdir, description, optional)
ArtifactMap._define_basic_mode() -> List[ArtifactDefinition]
ArtifactMap._define_iso_mode() -> List[ArtifactDefinition]
```

### Current File Operations
1. Construct source path: `source_dir / source_repo / target_subdir / filename`
2. Check if source file exists
3. Copy to: `target_dir / target_subdir / filename`

---

## New Architecture Design

### Design Principles
1. **Self-Contained:** All artifacts stored locally in project
2. **Dynamic Discovery:** Auto-discover what files exist
3. **Version Control Ready:** Artifacts can be tracked in git
4. **No External Dependencies:** No need for d:\tac
5. **Easy Updates:** Simply update files in store/ directory

### New Directory Structure
```
cc_setup/
├── cc_setup.py                    # Main script (refactored)
├── pyproject.toml
├── README.md
├── implement_local_store.md       # This file
├── logs/                          # Runtime logs
└── store/                         # NEW: Local artifact storage
    ├── basic/                     # Basic mode artifacts
    │   ├── settings.json          # Root level settings
    │   ├── hooks/                 # Hook scripts
    │   │   ├── notification.py
    │   │   ├── pre_compact.py
    │   │   ├── user_prompt_submit.py
    │   │   └── ...
    │   ├── commands/               # Slash commands
    │   │   ├── install.md
    │   │   ├── prime.md
    │   │   ├── bug.md
    │   │   └── ...
    │   ├── scripts/                # Utility scripts
    │   │   ├── start.sh
    │   │   ├── stop_apps.sh
    │   │   └── ...
    │   └── adws/                   # Agent Developer Workflows
    │       ├── adw_plan.py
    │       ├── adw_build.py
    │       └── ...
    └── iso/                        # Isolated worktree mode artifacts
        ├── settings.json
        ├── hooks/
        │   └── (same as basic)
        ├── commands/
        │   ├── (basic commands)
        │   ├── cleanup_worktrees.md
        │   ├── install_worktree.md
        │   └── ...
        ├── scripts/
        │   ├── (basic scripts)
        │   ├── check_ports.sh
        │   ├── purge_tree.sh
        │   └── ...
        └── adws/
            ├── adw_plan_iso.py
            ├── adw_build_iso.py
            └── ...
```

### Store Structure Rules
- **Level 1:** Mode (`basic/`, `iso/`)
- **Level 2:** Category (`hooks/`, `commands/`, `scripts/`, `adws/`)
- **Level 3:** Actual artifact files
- **Exception:** `settings.json` lives at mode level (not in a category subfolder)

### Path Mapping
| Source (old) | Target in Store | Target in Project |
|--------------|-----------------|-------------------|
| `d:\tac\tac-6\.claude\settings.json` | `store/basic/settings.json` | `.claude/settings.json` |
| `d:\tac\tac-6\.claude\hooks\*.py` | `store/basic/hooks/*.py` | `.claude/hooks/*.py` |
| `d:\tac\tac-6\.claude\commands\*.md` | `store/basic/commands/*.md` | `.claude/commands/*.md` |
| `d:\tac\tac-6\scripts\*.sh` | `store/basic/scripts/*.sh` | `scripts/*.sh` |
| `d:\tac\tac-6\adws\*.py` | `store/basic/adws/*.py` | `adws/*.py` |

---

## Dynamic Artifact Discovery

### Discovery Mechanism
Instead of hard-coding artifact lists, discover them at runtime:

```python
def discover_artifacts(mode: str) -> List[ArtifactDefinition]:
    """Discover all artifacts in store/{mode}/ directory."""
    store_path = Path(__file__).parent / "store" / mode
    artifacts = []

    # Discover settings.json (special case - not in subfolder)
    settings_file = store_path / "settings.json"
    if settings_file.exists():
        artifacts.append(ArtifactDefinition(
            filename="settings.json",
            source_path=settings_file,
            category="Settings",
            target_subdir=".claude",
            description="Claude Code configuration"
        ))

    # Discover categorized artifacts
    categories = {
        "hooks": (".claude/hooks", "Hook"),
        "commands": (".claude/commands", "Command"),
        "scripts": ("scripts", "Script"),
        "adws": ("adws", "ADW"),
    }

    for category_dir, (target_subdir, category_name) in categories.items():
        category_path = store_path / category_dir
        if not category_path.exists():
            continue

        for artifact_file in category_path.iterdir():
            if artifact_file.is_file():
                artifacts.append(ArtifactDefinition(
                    filename=artifact_file.name,
                    source_path=artifact_file,
                    category=category_name + "s",
                    target_subdir=target_subdir,
                    description=f"{category_name}: {artifact_file.name}"
                ))

    return artifacts
```

### Benefits of Discovery
- No more "missing" files (only shows what exists)
- Easy to add/remove artifacts (just add/remove files)
- No code changes needed to update artifact list
- Automatically handles differences between basic and iso

---

## Code Refactoring Plan

### Phase 1: Update Data Structures

**1.1 Modify ArtifactDefinition Class**
```python
class ArtifactDefinition:
    """Defines a single artifact to be copied."""

    def __init__(self, filename: str, source_path: Path, category: str,
                 target_subdir: str, description: str = ""):
        self.filename = filename
        self.source_path = source_path  # Changed from source_repo
        self.category = category
        self.target_subdir = target_subdir
        self.description = description
```

**Changes:**
- Remove `source_repo` parameter (no longer needed)
- Remove `optional` parameter (not needed with discovery)
- Add `source_path` as explicit Path object

**1.2 Replace ArtifactMap Class**
```python
class ArtifactStore:
    """Manages local artifact storage and discovery."""

    def __init__(self, store_base_path: Path = None):
        if store_base_path is None:
            # Default to store/ in same directory as script
            self.store_base_path = Path(__file__).parent / "store"
        else:
            self.store_base_path = Path(store_base_path)

    def get_artifacts(self, mode: str) -> List[ArtifactDefinition]:
        """Get all artifacts for specified mode."""
        return self._discover_artifacts(mode)

    def _discover_artifacts(self, mode: str) -> List[ArtifactDefinition]:
        """Discover artifacts in store/{mode}/"""
        # Implementation from discovery mechanism above
        pass

    def validate_store(self, mode: str) -> Tuple[bool, List[str]]:
        """Validate that store directory exists and has content."""
        mode_path = self.store_base_path / mode

        if not mode_path.exists():
            return False, [f"Store directory not found: {mode_path}"]

        # Check for at least some artifacts
        artifact_count = len(self.get_artifacts(mode))
        if artifact_count == 0:
            return False, [f"No artifacts found in: {mode_path}"]

        return True, []
```

### Phase 2: Update SetupConfig

**2.1 Remove source_dir Parameter**
```python
class SetupConfig:
    """Configuration for the setup process."""

    def __init__(self, args):
        self.target_dir = Path(args.target) if args.target else None
        self.mode = args.mode
        self.execute = args.execute
        self.overwrite = args.overwrite
        self.show_help_artifacts = args.help_artifacts
        # Removed: self.source_dir

        # Statistics
        self.files_to_copy = 0
        self.files_exist = 0
        self.files_to_overwrite = 0
        self.files_skipped = 0
        self.files_copied = 0
```

### Phase 3: Update CCSetup Class

**3.1 Replace artifact_map with artifact_store**
```python
class CCSetup:
    """Main class for Claude Code setup operations."""

    def __init__(self, config: SetupConfig):
        self.config = config
        self.artifact_store = ArtifactStore()  # Changed from artifact_map
        self.logger = self._setup_logging()
        self.operations: List[FileOperation] = []
```

**3.2 Update validate_source_directories**
```python
def validate_store(self) -> bool:
    """Validate that local store exists and has artifacts."""
    valid, errors = self.artifact_store.validate_store(self.config.mode)

    if not valid:
        for error in errors:
            console.print(f"[red]✗ {error}[/red]")
            self.logger.error(error)
        return False

    console.print(f"[green]✓ Local artifact store validated[/green]")
    self.logger.info(f"Local artifact store validated for mode: {self.config.mode}")
    return True
```

**3.3 Update analyze_operations**
```python
def analyze_operations(self) -> None:
    """Analyze what operations would be performed."""
    artifacts = self.artifact_store.get_artifacts(self.config.mode)

    for artifact in artifacts:
        # Source path is now directly in artifact
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

**3.4 Rename method call**
```python
def run(self) -> int:
    """Run the setup process."""
    try:
        self.display_header()

        # Validation - changed method name
        if not self.validate_store():  # Changed from validate_source_directories
            return 1

        if not self.validate_target_directory():
            return 1

        # ... rest unchanged
```

### Phase 4: Update CLI Arguments

**4.1 Remove --source-dir Argument**
```python
def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description="Claude Code Setup Tool - Copy artifacts into target projects",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Dry run (analysis only)
  uv run cc_setup.py --target /path/to/project --mode basic

  # Execute basic mode
  uv run cc_setup.py --target /path/to/project --mode basic --execute

  # Execute iso mode with overwrite
  uv run cc_setup.py --target /path/to/project --mode iso --execute --overwrite

  # Show available artifacts
  uv run cc_setup.py --help-artifacts
        """
    )

    parser.add_argument("--target", "-t", type=str,
        help="Target directory path (required unless --help-artifacts)")

    parser.add_argument("--mode", "-m", choices=["basic", "iso"],
        help="Setup mode: 'basic' or 'iso' (isolated worktree)")

    parser.add_argument("--execute", "-e", action="store_true",
        help="Execute file copy operations (default: dry-run mode)")

    parser.add_argument("--overwrite", "-o", action="store_true",
        help="Overwrite existing files (default: skip existing files)")

    # Removed: --source-dir argument

    parser.add_argument("--help-artifacts", action="store_true",
        help="Show what artifacts are installed in each mode")

    args = parser.parse_args()
    # ... rest unchanged
```

### Phase 5: Update Help Artifacts Display

**5.1 Update show_help_artifacts Function**
```python
def show_help_artifacts():
    """Display detailed artifact information for both modes."""
    artifact_store = ArtifactStore()

    console.print(Panel("[bold cyan]Claude Code Setup - Available Artifacts[/bold cyan]",
                       box=box.DOUBLE))

    for mode in ["basic", "iso"]:
        mode_title = "BASIC MODE" if mode == "basic" else "ISOLATED WORKTREE MODE"
        console.print(f"\n[bold green]{mode_title}[/bold green]")
        console.print("=" * 60)

        artifacts = artifact_store.get_artifacts(mode)

        # Group by category
        by_category = {}
        for artifact in artifacts:
            if artifact.category not in by_category:
                by_category[artifact.category] = []
            by_category[artifact.category].append(artifact.filename)

        table = Table(box=box.ROUNDED, show_header=True, header_style="bold cyan")
        table.add_column("Category", style="cyan", no_wrap=True)
        table.add_column("Count", justify="center", style="yellow")
        table.add_column("Files", style="white")

        for category, files in sorted(by_category.items()):
            table.add_row(category, str(len(files)), ", ".join(sorted(files)))

        console.print(table)
        console.print(f"\n[bold]Total {mode_title} Artifacts:[/bold] {len(artifacts)}")

    # Key differences
    console.print("\n\n[bold yellow]Key Differences:[/bold yellow]")
    console.print("• Basic Mode: Standard Claude Code setup for single-worktree projects")
    console.print("• Iso Mode: Enhanced setup with isolated worktree support")
    console.print("  - Additional worktree management commands")
    console.print("  - Isolated ADW workflows for parallel development")
    console.print("  - Enhanced scripts for port checking and tree management")
```

---

## Migration Strategy

### Step 1: Create Store Directory Structure
```bash
mkdir -p store/basic/{hooks,commands,scripts,adws}
mkdir -p store/iso/{hooks,commands,scripts,adws}
```

### Step 2: Copy Artifacts from d:\tac to Store

**Option A: Manual Migration Script**
Create a one-time migration script `migrate_to_store.py`:

```python
#!/usr/bin/env python3
"""One-time migration script to copy artifacts from d:\tac to local store."""

from pathlib import Path
import shutil

SOURCE_BASE = Path(r"d:\tac")
STORE_BASE = Path(__file__).parent / "store"

def migrate_mode(source_repo: str, target_mode: str):
    """Migrate artifacts from source repo to target mode."""
    source_base = SOURCE_BASE / source_repo
    target_base = STORE_BASE / target_mode

    # Ensure target directories exist
    target_base.mkdir(parents=True, exist_ok=True)

    # Migrate settings.json
    settings_src = source_base / ".claude" / "settings.json"
    if settings_src.exists():
        shutil.copy2(settings_src, target_base / "settings.json")
        print(f"✓ Copied settings.json")

    # Migrate categories
    migrations = [
        (".claude/hooks", "hooks"),
        (".claude/commands", "commands"),
        ("scripts", "scripts"),
        ("adws", "adws"),
    ]

    for source_subdir, target_subdir in migrations:
        source_path = source_base / source_subdir
        target_path = target_base / target_subdir

        if not source_path.exists():
            continue

        target_path.mkdir(parents=True, exist_ok=True)

        # Copy all files
        for item in source_path.iterdir():
            if item.is_file():
                shutil.copy2(item, target_path / item.name)
                print(f"✓ Copied {source_subdir}/{item.name}")

if __name__ == "__main__":
    print("Migrating artifacts to local store...")
    print("\nMigrating BASIC mode from tac-6...")
    migrate_mode("tac-6", "basic")

    print("\nMigrating ISO mode from tac-7...")
    migrate_mode("tac-7", "iso")

    print("\n✓ Migration complete!")
```

**Option B: Manual Copy**
Users can manually copy files they want from d:\tac to store/

### Step 3: Curate Store Contents

After migration, review and clean up:
1. Remove unwanted/specialized files
2. Ensure only recommended artifacts are included
3. Test both modes to verify completeness

**Recommended Basic Mode Artifacts:**
- Settings: `settings.json`
- Hooks: `notification.py`, `pre_compact.py`, `user_prompt_submit.py`, `post_tool_use.py`, `pre_tool_use.py`
- Commands: `install.md`, `prime.md`, `bug.md`, `chore.md`, `feature.md`, `implement.md`, `start.md`, `tools.md`, `commit.md`, `pull_request.md`, `review.md`, `document.md`, `patch.md`
- Scripts: `start.sh`, `stop_apps.sh`, `copy_dot_env.sh`, `clear_issue_comments.sh`, `delete_pr.sh`, `reset_db.sh`
- ADWs: Core workflows only (not all experimental ones)

**Recommended Iso Mode Artifacts:**
- All basic mode artifacts PLUS:
- Commands: `cleanup_worktrees.md`, `install_worktree.md`, `test.md`, `test_e2e.md`
- Scripts: `check_ports.sh`, `purge_tree.sh`
- ADWs: All isolated workflow variants (`*_iso.py`)

### Step 4: Test Migration

```bash
# Test basic mode
uv run cc_setup.py --help-artifacts

# Test dry-run
uv run cc_setup.py --target ./test_target --mode basic

# Test execution
uv run cc_setup.py --target ./test_target --mode basic --execute
```

---

## Implementation Checklist

### Code Changes
- [ ] Update `ArtifactDefinition` class signature
- [ ] Replace `ArtifactMap` with `ArtifactStore` class
- [ ] Implement `discover_artifacts()` method
- [ ] Implement `validate_store()` method
- [ ] Update `SetupConfig` class (remove source_dir)
- [ ] Update `CCSetup.__init__()` to use artifact_store
- [ ] Update `CCSetup.validate_source_directories()` -> `validate_store()`
- [ ] Update `CCSetup.analyze_operations()` to use new source paths
- [ ] Update `CCSetup.run()` method call
- [ ] Remove `--source-dir` CLI argument
- [ ] Update `show_help_artifacts()` to use discovery
- [ ] Update logging messages (remove source_dir references)

### Directory Setup
- [ ] Create `store/basic/` directory structure
- [ ] Create `store/iso/` directory structure
- [ ] Create subdirectories: hooks, commands, scripts, adws

### Migration
- [ ] Copy artifacts from tac-6 to store/basic
- [ ] Copy artifacts from tac-7 to store/iso
- [ ] Curate and remove unwanted artifacts
- [ ] Verify settings.json files are in place

### Testing
- [ ] Test `--help-artifacts` output
- [ ] Test basic mode dry-run
- [ ] Test iso mode dry-run
- [ ] Test basic mode execution
- [ ] Test iso mode execution
- [ ] Test with empty target directory
- [ ] Test with existing files
- [ ] Test overwrite functionality
- [ ] Verify log files are correct
- [ ] Check all file paths in output

### Documentation
- [ ] Update README.md
  - [ ] Remove references to d:\tac
  - [ ] Remove --source-dir documentation
  - [ ] Document local store structure
  - [ ] Update "how to add artifacts" section
- [ ] Update implementation_plan.md
- [ ] Create migration guide for existing users
- [ ] Document how to customize artifacts

---

## Benefits of New Design

### For Users
1. **No External Dependencies:** Don't need d:\tac directory
2. **Predictable:** Always shows what exists, no "missing" files
3. **Customizable:** Easy to add/remove artifacts by editing store/
4. **Portable:** Entire project can be zipped and shared
5. **Version Controlled:** Artifacts can be tracked in git

### For Developers
1. **Simpler Code:** No hard-coded artifact lists
2. **Dynamic Discovery:** Automatically adapts to store contents
3. **Easier Testing:** Test artifacts right in the project
4. **Better Separation:** Clear separation between code and data
5. **Easier Updates:** Update artifacts without code changes

### For Maintenance
1. **Clear Organization:** All artifacts in one place
2. **Easy to Audit:** Can see exactly what's included
3. **Simple Updates:** Replace files in store/ to update
4. **Mode Comparison:** Easy to see differences between basic/iso
5. **Documentation Ready:** Store structure is self-documenting

---

## Rollout Strategy

### Phase 1: Create New Version (v2.0)
1. Implement all code changes
2. Create store/ directory structure
3. Migrate artifacts from tac-6 and tac-7
4. Test thoroughly

### Phase 2: Backward Compatibility (Optional)
If needed, could support both modes temporarily:
```python
# Auto-detect if using local store or external source
if (Path(__file__).parent / "store").exists():
    # Use new local store mode
    artifact_store = ArtifactStore()
else:
    # Fall back to old external mode
    artifact_map = ArtifactMap()
```

### Phase 3: Documentation Update
1. Update README.md
2. Create migration guide
3. Document how to customize artifacts
4. Update all examples

### Phase 4: Release
1. Tag as v2.0
2. Update any external references
3. Notify users of breaking changes
4. Provide migration path

---

## Future Enhancements

### Possible Future Features
1. **Multiple Modes:** Add more than just basic/iso
2. **Artifact Metadata:** Add .json files describing each artifact
3. **Version Tracking:** Track versions of artifacts
4. **Update Command:** Fetch latest artifacts from remote
5. **Custom Modes:** Allow users to create custom mode combinations
6. **Artifact Validation:** Validate artifact syntax before copying
7. **Dependency Tracking:** Track which artifacts depend on others

### Store Metadata Example
```json
// store/basic/metadata.json
{
  "mode": "basic",
  "version": "1.0",
  "description": "Standard Claude Code setup",
  "last_updated": "2025-10-31",
  "artifacts": {
    "hooks/notification.py": {
      "version": "5",
      "description": "TTS notifications",
      "dependencies": []
    }
  }
}
```

---

## Testing Plan

### Unit Tests (Future)
1. Test artifact discovery for each mode
2. Test store validation
3. Test with missing directories
4. Test with empty directories
5. Test file path construction

### Integration Tests
1. Full dry-run for basic mode
2. Full dry-run for iso mode
3. Full execution for basic mode
4. Full execution for iso mode
5. Test overwrite functionality
6. Test with partially populated target

### Edge Cases
1. Empty store directory
2. Missing mode directory
3. Invalid mode name
4. Symlinks in store
5. Read-only store files
6. Non-file objects in store (directories, etc.)

---

## Summary

This redesign transforms cc_setup from a tool that depends on external repositories to a self-contained, portable tool with dynamic artifact discovery. The new architecture is simpler, more maintainable, and provides a better user experience.

**Key Changes:**
- Local store in `store/{mode}/{category}/` structure
- Dynamic artifact discovery (no hard-coding)
- Removed external dependency on d:\tac
- Simplified code with better separation of concerns
- Better user experience (no missing files, clear structure)

**Implementation Effort:**
- Code changes: ~4-6 hours
- Migration: ~1-2 hours
- Testing: ~2-3 hours
- Documentation: ~1-2 hours
- **Total: ~8-13 hours**

**Risk Level:** Medium
- Breaking change (no backward compatibility)
- Requires artifact migration
- Users need to understand new structure
- But: Relatively straightforward refactoring
