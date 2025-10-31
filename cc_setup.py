#!/usr/bin/env python3
"""
Claude Code Setup Tool
A utility to copy Claude Code artifacts from local store into target projects.
"""

import argparse
import hashlib
import logging
import shutil
import sys
from datetime import datetime
from pathlib import Path
from typing import List, Tuple

from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich.tree import Tree
from rich.progress import Progress, SpinnerColumn, TextColumn, BarColumn
from rich import box

# Initialize Rich console
console = Console()


class ArtifactDefinition:
    """Defines a single artifact to be copied."""

    def __init__(self, filename: str, source_path: Path, category: str,
                 target_subdir: str, description: str = ""):
        self.filename = filename
        self.source_path = source_path
        self.category = category
        self.target_subdir = target_subdir
        self.description = description


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
        store_path = self.store_base_path / mode
        artifacts = []

        if not store_path.exists():
            return artifacts

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
            "hooks": (".claude/hooks", "Hooks"),
            "commands": (".claude/commands", "Commands"),
            "scripts": ("scripts", "Scripts"),
            "adws": ("adws", "ADWs"),
        }

        for category_dir, (target_subdir, category_name) in categories.items():
            category_path = store_path / category_dir
            if not category_path.exists():
                continue

            for artifact_file in sorted(category_path.iterdir()):
                if artifact_file.is_file():
                    # Determine description based on file type
                    if category_dir == "hooks":
                        desc = f"Hook: {artifact_file.stem}"
                    elif category_dir == "commands":
                        desc = f"Slash command: /{artifact_file.stem}"
                    elif category_dir == "scripts":
                        desc = f"Utility script: {artifact_file.name}"
                    elif category_dir == "adws":
                        desc = f"Agent Developer Workflow: {artifact_file.stem}"
                    else:
                        desc = artifact_file.name

                    artifacts.append(ArtifactDefinition(
                        filename=artifact_file.name,
                        source_path=artifact_file,
                        category=category_name,
                        target_subdir=target_subdir,
                        description=desc
                    ))

        return artifacts

    def validate_store(self, mode: str) -> Tuple[bool, List[str]]:
        """Validate that store directory exists and has content."""
        mode_path = self.store_base_path / mode

        if not self.store_base_path.exists():
            return False, [f"Store directory not found: {self.store_base_path}"]

        if not mode_path.exists():
            return False, [f"Mode directory not found: {mode_path}"]

        # Check for at least some artifacts
        artifact_count = len(self.get_artifacts(mode))
        if artifact_count == 0:
            return False, [f"No artifacts found in: {mode_path}"]

        return True, []


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
        self.files_identical = 0
        self.files_different = 0
        self.files_to_overwrite = 0
        self.files_skipped = 0
        self.files_copied = 0


class FileOperation:
    """Represents a single file operation."""

    def __init__(self, artifact: ArtifactDefinition, source_path: Path,
                 target_path: Path, exists: bool, is_identical: bool,
                 will_copy: bool, will_overwrite: bool):
        self.artifact = artifact
        self.source_path = source_path
        self.target_path = target_path
        self.exists = exists
        self.is_identical = is_identical
        self.will_copy = will_copy
        self.will_overwrite = will_overwrite
        self.status = self._determine_status()

    def _determine_status(self) -> str:
        """Determine the status indicator."""
        if not self.source_path.exists():
            return "✗ Missing"
        elif self.will_overwrite:
            return "⚠ Overwrite"
        elif self.exists:
            if self.is_identical:
                return "✓ Identical"
            else:
                return "⚠ Different"
        else:
            return "✓ New"

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
                return "Skipping (identical)" if execute else "Skip (identical)"
            else:
                return "Skipping (different)" if execute else "Skip (different)"


class CCSetup:
    """Main class for Claude Code setup operations."""

    def __init__(self, config: SetupConfig):
        self.config = config
        self.artifact_store = ArtifactStore()
        self.logger = self._setup_logging()
        self.operations: List[FileOperation] = []

    def _setup_logging(self) -> logging.Logger:
        """Set up logging to file."""
        log_dir = Path("logs")
        log_dir.mkdir(exist_ok=True)

        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        log_file = log_dir / f"cc_setup_{timestamp}.log"

        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler(log_file),
            ]
        )

        logger = logging.getLogger(__name__)
        logger.info("=" * 80)
        logger.info("CC Setup Tool Started")
        logger.info(f"Target Directory: {self.config.target_dir}")
        logger.info(f"Mode: {self.config.mode}")
        logger.info(f"Execute: {self.config.execute}")
        logger.info(f"Overwrite: {self.config.overwrite}")
        logger.info(f"Store Directory: {self.artifact_store.store_base_path}")
        logger.info("=" * 80)

        return logger

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

    def validate_target_directory(self) -> bool:
        """Validate or create target directory."""
        if not self.config.target_dir.exists():
            console.print(f"[yellow]⚠ Target directory does not exist: {self.config.target_dir}[/yellow]")
            if self.config.execute:
                try:
                    self.config.target_dir.mkdir(parents=True, exist_ok=True)
                    console.print(f"[green]✓ Created target directory[/green]")
                    self.logger.info(f"Created target directory: {self.config.target_dir}")
                except Exception as e:
                    console.print(f"[red]✗ Failed to create target directory: {e}[/red]")
                    self.logger.error(f"Failed to create target directory: {e}")
                    return False
            else:
                console.print(f"[yellow]  (Will be created in execute mode)[/yellow]")
                self.logger.info("Target directory will be created in execute mode")
        else:
            console.print(f"[green]✓ Target directory exists[/green]")
            self.logger.info("Target directory exists")

        return True

    def analyze_operations(self) -> None:
        """Analyze what operations would be performed."""
        artifacts = self.artifact_store.get_artifacts(self.config.mode)

        for artifact in artifacts:
            source_path = artifact.source_path
            target_path = self.config.target_dir / artifact.target_subdir / artifact.filename

            exists = target_path.exists()

            # Check if files are identical
            is_identical = False
            if exists and source_path.exists():
                is_identical = self.files_are_identical(source_path, target_path)

            will_copy = (not exists or self.config.overwrite) and source_path.exists()
            will_overwrite = exists and self.config.overwrite and source_path.exists()

            operation = FileOperation(artifact, source_path, target_path,
                                     exists, is_identical, will_copy, will_overwrite)
            self.operations.append(operation)

            # Update statistics
            if will_copy and not will_overwrite:
                self.config.files_to_copy += 1
            if exists:
                self.config.files_exist += 1
                if is_identical:
                    self.config.files_identical += 1
                else:
                    self.config.files_different += 1
            if will_overwrite:
                self.config.files_to_overwrite += 1

        self.logger.info(f"Analysis complete: {len(self.operations)} operations planned")
        self.logger.info(f"Files to copy: {self.config.files_to_copy}")
        self.logger.info(f"Files exist: {self.config.files_exist}")
        self.logger.info(f"Files identical: {self.config.files_identical}")
        self.logger.info(f"Files different: {self.config.files_different}")
        self.logger.info(f"Files to overwrite: {self.config.files_to_overwrite}")

    def display_header(self) -> None:
        """Display header panel."""
        mode_str = "Basic Mode" if self.config.mode == "basic" else "Isolated Worktree Mode"
        exec_str = "[green]EXECUTE MODE[/green]" if self.config.execute else "[yellow]DRY RUN[/yellow]"
        overwrite_str = " | [red]OVERWRITE ENABLED[/red]" if self.config.overwrite else ""

        header_text = f"""[bold]Claude Code Setup Tool[/bold]

Target: [cyan]{self.config.target_dir}[/cyan]
Mode: [cyan]{mode_str}[/cyan]
Status: {exec_str}{overwrite_str}
Store: [dim]{self.artifact_store.store_base_path}[/dim]"""

        console.print(Panel(header_text, box=box.ROUNDED, border_style="blue"))

    def display_directory_tree(self) -> None:
        """Display directory structure to be created."""
        tree = Tree(f"[bold cyan]{self.config.target_dir.name}/[/bold cyan]")

        claude_node = tree.add("[cyan].claude/[/cyan]")
        claude_node.add("[green]commands/[/green]")
        claude_node.add("[green]hooks/[/green]")
        claude_node.add("[green]adws/[/green]")
        claude_node.add("[yellow]settings.json[/yellow]")

        tree.add("[cyan]scripts/[/cyan]")

        if self.config.mode == "iso":
            tree.add("[cyan]trees/[/cyan] (created by worktree commands)")

        console.print("\n[bold]📁 Directory Structure:[/bold]")
        console.print(tree)

    def display_operations_table(self) -> None:
        """Display operations in a table."""
        table = Table(title="\n📋 Artifacts Analysis", box=box.ROUNDED)

        table.add_column("Category", style="cyan", no_wrap=True)
        table.add_column("File", style="white")
        table.add_column("Status", justify="center", no_wrap=True)
        table.add_column("Action", style="yellow", no_wrap=True)

        for op in self.operations:
            # Determine row style
            if not op.source_path.exists():
                style = "red dim"
            elif op.will_overwrite:
                style = "red"
            elif op.exists:
                if op.is_identical:
                    style = "cyan"
                else:
                    style = "yellow"
            else:
                style = "green"

            table.add_row(
                op.artifact.category,
                op.artifact.filename,
                op.status,
                op.get_action(False),
                style=style
            )

            self.logger.info(f"{op.artifact.category}: {op.artifact.filename} - "
                           f"{op.status} - {op.get_action(False)}"
                           f"{' (identical)' if op.is_identical else ''}")

        console.print(table)

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

        console.print("\n" + "=" * 60)
        console.print(Panel(summary_text, box=box.ROUNDED, border_style="blue"))

        if not self.config.execute:
            console.print("\n[bold yellow]⚠ This is a DRY RUN. Use --execute to perform actual copy.[/bold yellow]")

        self.logger.info("Summary displayed")

    def execute_operations(self) -> None:
        """Execute the file copy operations."""
        if not self.config.execute:
            return

        console.print("\n[bold]Executing operations...[/bold]\n")

        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            BarColumn(),
            TextColumn("[progress.percentage]{task.percentage:>3.0f}%"),
            console=console
        ) as progress:

            task = progress.add_task("[cyan]Copying files...", total=len(self.operations))

            for op in self.operations:
                # Create target directory if needed
                op.target_path.parent.mkdir(parents=True, exist_ok=True)

                if op.will_copy:
                    try:
                        shutil.copy2(op.source_path, op.target_path)

                        # Set executable permissions for .sh files on Unix
                        if op.artifact.filename.endswith('.sh') and sys.platform != 'win32':
                            op.target_path.chmod(0o755)

                        self.config.files_copied += 1
                        self.logger.info(f"Copied: {op.artifact.filename} -> {op.target_path}")

                    except Exception as e:
                        console.print(f"[red]✗ Failed to copy {op.artifact.filename}: {e}[/red]")
                        self.logger.error(f"Failed to copy {op.artifact.filename}: {e}")
                else:
                    self.config.files_skipped += 1
                    self.logger.info(f"Skipped: {op.artifact.filename}")

                progress.update(task, advance=1)

        console.print(f"\n[green]✓ Operation complete![/green]")
        self.logger.info("Execution complete")

    def run(self) -> int:
        """Run the setup process."""
        try:
            self.display_header()

            # Validation
            if not self.validate_store():
                return 1

            if not self.validate_target_directory():
                return 1

            # Analysis
            console.print("\n[bold]Analyzing artifacts...[/bold]")
            self.analyze_operations()

            # Display
            self.display_directory_tree()
            self.display_operations_table()

            # Execute if requested
            if self.config.execute:
                self.execute_operations()

            # Summary
            self.display_summary()

            self.logger.info("CC Setup completed successfully")
            return 0

        except KeyboardInterrupt:
            console.print("\n[yellow]Operation cancelled by user[/yellow]")
            self.logger.warning("Operation cancelled by user")
            return 130
        except Exception as e:
            console.print(f"\n[red]✗ Error: {e}[/red]")
            self.logger.error(f"Error: {e}", exc_info=True)
            return 1


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

        if not artifacts:
            console.print(f"[yellow]No artifacts found for {mode} mode[/yellow]")
            continue

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

        for category in sorted(by_category.keys()):
            files = by_category[category]
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

    parser.add_argument(
        "--target", "-t",
        type=str,
        help="Target directory path (required unless --help-artifacts)"
    )

    parser.add_argument(
        "--mode", "-m",
        choices=["basic", "iso"],
        help="Setup mode: 'basic' or 'iso' (isolated worktree)"
    )

    parser.add_argument(
        "--execute", "-e",
        action="store_true",
        help="Execute file copy operations (default: dry-run mode)"
    )

    parser.add_argument(
        "--overwrite", "-o",
        action="store_true",
        help="Overwrite existing files (default: skip existing files)"
    )

    parser.add_argument(
        "--help-artifacts",
        action="store_true",
        help="Show what artifacts are installed in each mode"
    )

    args = parser.parse_args()

    # Handle --help-artifacts
    if args.help_artifacts:
        show_help_artifacts()
        return 0

    # Validate required arguments
    if not args.target or not args.mode:
        parser.error("--target and --mode are required (unless using --help-artifacts)")

    # Create config and run
    config = SetupConfig(args)
    setup = CCSetup(config)

    return setup.run()


if __name__ == "__main__":
    sys.exit(main())
