#!/usr/bin/env python3
"""
Claude Code Setup Tool
A utility to copy Claude Code artifacts from local store into target projects.
"""

import argparse
import difflib
import hashlib
import json
import logging
import shutil
import sys
import tomllib
from datetime import datetime, timezone
from pathlib import Path
from typing import List, Tuple, Optional, Dict, Any

from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich.tree import Tree
from rich.progress import Progress, SpinnerColumn, TextColumn, BarColumn
from rich import box
from rich_argparse import RichHelpFormatter

# Initialize Rich console
console = Console()


class OperationLogger:
    """Handles JSONL logging of cc_setup operations to target repositories."""

    def __init__(self, target_dir: Path, logger: logging.Logger):
        """Initialize the operation logger.

        Args:
            target_dir: Target directory where .claude/cc_setup.log.jsonl will be created
            logger: Standard logger for logging errors in JSONL logging itself
        """
        self.target_dir = target_dir
        self.logger = logger
        self.version = self._read_version()

    def _read_version(self) -> str:
        """Read version from pyproject.toml.

        Returns:
            Version string, or "unknown" if unable to read
        """
        try:
            pyproject_path = Path(__file__).parent / "pyproject.toml"
            if pyproject_path.exists():
                with open(pyproject_path, "rb") as f:
                    data = tomllib.load(f)
                    return data.get("project", {}).get("version", "unknown")
        except Exception as e:
            self.logger.warning(f"Failed to read version from pyproject.toml: {e}")
        return "unknown"

    def _serialize_path(self, obj: Any) -> Any:
        """Convert Path objects to strings for JSON serialization.

        Args:
            obj: Object to serialize

        Returns:
            Serializable version of the object
        """
        if isinstance(obj, Path):
            return str(obj)
        elif isinstance(obj, dict):
            return {k: self._serialize_path(v) for k, v in obj.items()}
        elif isinstance(obj, list):
            return [self._serialize_path(item) for item in obj]
        return obj

    def log_operation(self, operation_data: Dict[str, Any]) -> None:
        """Write operation data to JSONL log file.

        Args:
            operation_data: Dictionary containing operation details
        """
        try:
            # Ensure .claude directory exists
            claude_dir = self.target_dir / ".claude"
            claude_dir.mkdir(parents=True, exist_ok=True)

            # Path to JSONL log file
            log_path = claude_dir / "cc_setup.log.jsonl"

            # Add timestamp and version to operation data
            log_entry = {
                "timestamp": datetime.now(timezone.utc).isoformat(),
                "version": self.version,
                **operation_data
            }

            # Serialize Path objects
            log_entry = self._serialize_path(log_entry)

            # Append to JSONL file (one JSON object per line)
            with open(log_path, "a", encoding="utf-8") as f:
                json.dump(log_entry, f, ensure_ascii=False)
                f.write("\n")

            self.logger.info(f"JSONL log entry written to {log_path}")

        except Exception as e:
            # Don't fail the operation if logging fails
            error_msg = f"Failed to write JSONL log: {e}"
            self.logger.error(error_msg)
            console.print(f"[yellow]⚠ Warning: {error_msg}[/yellow]")


class ArtifactDefinition:
    """Defines a single artifact to be copied."""

    def __init__(self, filename: str, source_path: Path, category: str,
                 target_subdir: str, description: str = "", is_directory: bool = False):
        self.filename = filename
        self.source_path = source_path
        self.category = category
        self.target_subdir = target_subdir
        self.description = description
        self.is_directory = is_directory


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

            # Special handling for adws category - discover subdirectories
            if category_dir == "adws":
                adws_subdirs = ["adw_modules", "adw_tests", "adw_triggers"]
                for subdir_name in adws_subdirs:
                    subdir_path = category_path / subdir_name
                    if subdir_path.exists() and subdir_path.is_dir():
                        # Determine description for subdirectory
                        if subdir_name == "adw_modules":
                            desc = "ADW Modules Directory"
                        elif subdir_name == "adw_tests":
                            desc = "ADW Tests Directory"
                        elif subdir_name == "adw_triggers":
                            desc = "ADW Triggers Directory"
                        else:
                            desc = f"ADW Directory: {subdir_name}"

                        artifacts.append(ArtifactDefinition(
                            filename=subdir_name,
                            source_path=subdir_path,
                            category=category_name,
                            target_subdir=target_subdir,
                            description=desc,
                            is_directory=True
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
        self.show_help_examples = args.help_examples

        # GitIgnore configuration
        self.gitignore_lang = args.gitignore if hasattr(args, 'gitignore') else None
        self.gitignore_execute = args.gitignore_execute if hasattr(args, 'gitignore_execute') else 'compare'
        # Comparison mode: 'diff' for unified diff, 'set' for set-based comparison
        self.gitignore_compare_mode = args.gitignore_compare_mode if hasattr(args, 'gitignore_compare_mode') else 'diff'

        # Statistics
        self.files_to_copy = 0
        self.files_exist = 0
        self.files_identical = 0
        self.files_different = 0
        self.files_to_overwrite = 0
        self.files_skipped = 0
        self.files_copied = 0

        # GitIgnore statistics
        self.gitignore_lines_added = 0
        self.gitignore_lines_removed = 0
        self.gitignore_unchanged = 0


class FileOperation:
    """Represents a single file operation."""

    def __init__(self, artifact: ArtifactDefinition, source_path: Path,
                 target_path: Path, exists: bool, is_identical: bool,
                 will_copy: bool, will_overwrite: bool, file_count: int = 1):
        self.artifact = artifact
        self.source_path = source_path
        self.target_path = target_path
        self.exists = exists
        self.is_identical = is_identical
        self.will_copy = will_copy
        self.will_overwrite = will_overwrite
        self.file_count = file_count  # Number of files (1 for files, N for directories)
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
        self.operation_logger = None  # Will be initialized after target_dir is validated

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

    def _collect_artifact_operation_data(self, result: str, error_message: Optional[str] = None) -> Dict[str, Any]:
        """Collect data for artifact operations.

        Args:
            result: Operation result ("success", "error", or "cancelled")
            error_message: Optional error message if result is "error"

        Returns:
            Dictionary containing operation data for JSONL logging
        """
        operation_data = {
            "operation_type": "artifact",
            "mode": self.config.mode,
            "target_dir": self.config.target_dir,
            "execute": self.config.execute,
            "overwrite": self.config.overwrite,
            "result": result,
            "statistics": {
                "files_to_copy": self.config.files_to_copy,
                "files_exist": self.config.files_exist,
                "files_identical": self.config.files_identical,
                "files_different": self.config.files_different,
                "files_to_overwrite": self.config.files_to_overwrite,
                "files_copied": self.config.files_copied,
                "files_skipped": self.config.files_skipped,
            },
            "artifacts": []
        }

        # Add artifact details
        for op in self.operations:
            artifact_entry = {
                "filename": op.artifact.filename,
                "category": op.artifact.category,
                "target_subdir": op.artifact.target_subdir,
                "status": op.status,
                "action": op.get_action(self.config.execute),
                "exists": op.exists,
                "is_identical": op.is_identical,
            }
            operation_data["artifacts"].append(artifact_entry)

        # Add error message if present
        if error_message:
            operation_data["error_message"] = error_message

        return operation_data

    def _collect_gitignore_operation_data(self, result: str, error_message: Optional[str] = None) -> Dict[str, Any]:
        """Collect data for gitignore operations.

        Args:
            result: Operation result ("success", "error", or "cancelled")
            error_message: Optional error message if result is "error"

        Returns:
            Dictionary containing operation data for JSONL logging
        """
        operation_data = {
            "operation_type": "gitignore",
            "mode": self.config.gitignore_lang,
            "target_dir": self.config.target_dir,
            "execute": self.config.execute,
            "gitignore_operation": self.config.gitignore_execute,
            "result": result,
        }

        # Add comparison mode if it's a compare operation
        if self.config.gitignore_execute == "compare":
            operation_data["comparison_mode"] = self.config.gitignore_compare_mode

        # Add statistics if available
        if self.config.gitignore_execute in ["merge", "replace"]:
            operation_data["statistics"] = {
                "lines_added": self.config.gitignore_lines_added,
                "lines_removed": self.config.gitignore_lines_removed,
            }

        # Add error message if present
        if error_message:
            operation_data["error_message"] = error_message

        return operation_data

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

    def count_files_in_directory(self, directory: Path) -> int:
        """Count the number of files recursively in a directory.

        Args:
            directory: Directory path to count files in

        Returns:
            Total number of files in directory and subdirectories
        """
        try:
            if not directory.exists() or not directory.is_dir():
                return 0
            return len([f for f in directory.rglob('*') if f.is_file()])
        except Exception as e:
            self.logger.warning(f"Failed to count files in {directory}: {e}")
            return 0

    def get_gitignore_template_path(self, lang: str) -> Optional[Path]:
        """Get path to gitignore template for specified language.

        Args:
            lang: Language name (e.g., 'python', 'csharp')

        Returns:
            Path to template file, or None if not found
        """
        template_path = self.artifact_store.store_base_path / "git" / f".gitignore_{lang}"
        if template_path.exists():
            return template_path
        return None

    def get_available_gitignore_languages(self) -> List[str]:
        """Get list of available gitignore languages.

        Returns:
            List of language names that have templates
        """
        git_dir = self.artifact_store.store_base_path / "git"
        if not git_dir.exists():
            return []

        languages = []
        for file in git_dir.iterdir():
            if file.is_file() and file.name.startswith(".gitignore_"):
                lang = file.name.replace(".gitignore_", "")
                languages.append(lang)

        return sorted(languages)

    def read_gitignore_lines(self, file_path: Path) -> List[str]:
        """Read .gitignore file and return list of lines.

        Args:
            file_path: Path to .gitignore file

        Returns:
            List of lines from the file (including empty lines and comments)
        """
        if not file_path.exists():
            return []

        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                return [line.rstrip('\n\r') for line in f.readlines()]
        except Exception as e:
            self.logger.error(f"Failed to read {file_path}: {e}")
            return []

    def extract_gitignore_patterns(self, lines: List[str]) -> set:
        """Extract meaningful patterns from .gitignore lines.

        Filters out empty lines and comment-only lines, returning only
        actual ignore patterns. This is useful for semantic comparison
        where order doesn't matter.

        Args:
            lines: List of lines from .gitignore file

        Returns:
            Set of non-empty, non-comment patterns
        """
        patterns = set()
        for line in lines:
            stripped = line.strip()
            # Skip empty lines
            if not stripped:
                continue
            # Skip comment-only lines
            if stripped.startswith('#'):
                continue
            # Add the pattern (with original spacing preserved)
            patterns.add(stripped)
        return patterns

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

            # Check if files/directories are identical
            is_identical = False
            if exists and source_path.exists():
                # For directories, we don't do deep comparison (too expensive)
                # Just mark as not identical if it's a directory
                if artifact.is_directory:
                    is_identical = False
                else:
                    is_identical = self.files_are_identical(source_path, target_path)

            # For directories: copy if doesn't exist OR if overwrite is enabled
            # For files: don't copy if identical, even with --overwrite flag
            if artifact.is_directory:
                will_copy = (not exists or self.config.overwrite) and source_path.exists()
                will_overwrite = exists and self.config.overwrite and source_path.exists()
            else:
                will_copy = (not exists or (self.config.overwrite and not is_identical)) and source_path.exists()
                will_overwrite = exists and self.config.overwrite and source_path.exists() and not is_identical

            # Count files for directories, 1 for regular files
            file_count = 1
            if artifact.is_directory and source_path.exists():
                file_count = self.count_files_in_directory(source_path)

            operation = FileOperation(artifact, source_path, target_path,
                                     exists, is_identical, will_copy, will_overwrite, file_count)
            self.operations.append(operation)

            # Update statistics (count actual files for directories)
            if will_copy and not will_overwrite:
                self.config.files_to_copy += file_count
            if exists:
                self.config.files_exist += file_count
                if is_identical:
                    self.config.files_identical += file_count
                else:
                    self.config.files_different += file_count
            if will_overwrite:
                self.config.files_to_overwrite += file_count

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

            # For directories, show file count
            filename_display = op.artifact.filename
            if op.artifact.is_directory and op.file_count > 1:
                filename_display = f"{op.artifact.filename} ({op.file_count} files)"

            table.add_row(
                op.artifact.category,
                filename_display,
                op.status,
                op.get_action(False),
                style=style
            )

            # Log with file count if directory
            log_msg = f"{op.artifact.category}: {op.artifact.filename}"
            if op.artifact.is_directory and op.file_count > 1:
                log_msg += f" ({op.file_count} files)"
            log_msg += f" - {op.status} - {op.get_action(False)}"
            if op.is_identical:
                log_msg += " (identical)"
            self.logger.info(log_msg)

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
                        # Handle directory artifacts
                        if op.artifact.is_directory:
                            # For directories, use copytree
                            if op.target_path.exists():
                                # If overwrite is enabled and directory exists, remove it first
                                if self.config.overwrite:
                                    shutil.rmtree(op.target_path)
                                    shutil.copytree(op.source_path, op.target_path)
                                # If not overwriting, skip (will_copy should be False, but double-check)
                            else:
                                # Directory doesn't exist, copy it
                                shutil.copytree(op.source_path, op.target_path)

                            self.config.files_copied += op.file_count
                            self.logger.info(f"Copied directory: {op.artifact.filename} ({op.file_count} files) -> {op.target_path}")
                        else:
                            # Handle file artifacts (existing logic)
                            shutil.copy2(op.source_path, op.target_path)

                            # Set executable permissions for .sh files on Unix
                            if op.artifact.filename.endswith('.sh') and sys.platform != 'win32':
                                op.target_path.chmod(0o755)

                            self.config.files_copied += op.file_count
                            self.logger.info(f"Copied: {op.artifact.filename} -> {op.target_path}")

                    except Exception as e:
                        console.print(f"[red]✗ Failed to copy {op.artifact.filename}: {e}[/red]")
                        self.logger.error(f"Failed to copy {op.artifact.filename}: {e}")
                else:
                    self.config.files_skipped += op.file_count
                    skip_msg = f"Skipped: {op.artifact.filename}"
                    if op.artifact.is_directory and op.file_count > 1:
                        skip_msg += f" ({op.file_count} files)"
                    self.logger.info(skip_msg)

                progress.update(task, advance=1)

        console.print(f"\n[green]✓ Operation complete![/green]")
        self.logger.info("Execution complete")

    def compare_gitignore_set(self) -> bool:
        """Compare target .gitignore with template using set-based logic.

        Uses set operations to show semantic differences (order-independent).
        Displays three sections: missing from target, extra in target, and common patterns.

        Returns:
            True if files are identical, False otherwise
        """
        template_path = self.get_gitignore_template_path(self.config.gitignore_lang)
        target_path = self.config.target_dir / ".gitignore"

        template_lines = self.read_gitignore_lines(template_path)
        target_lines = self.read_gitignore_lines(target_path)

        # Extract patterns (filtering out comments and empty lines)
        template_patterns = self.extract_gitignore_patterns(template_lines)
        target_patterns = self.extract_gitignore_patterns(target_lines)

        # Calculate set differences
        missing_from_target = template_patterns - target_patterns
        extra_in_target = target_patterns - template_patterns
        common_patterns = template_patterns & target_patterns

        # Check if files are identical
        if not missing_from_target and not extra_in_target:
            console.print("[green]✓ Files are identical - no pattern differences[/green]")
            self.logger.info("GitIgnore files are identical (set-based comparison)")
            return True

        # Display set-based comparison results
        console.print("\n[bold]Set-Based Comparison:[/bold]\n")

        # Statistics summary
        console.print(f"[cyan]Statistics:[/cyan]")
        console.print(f"  Template patterns: {len(template_patterns)}")
        console.print(f"  Target patterns: {len(target_patterns)}")
        console.print(f"  Common patterns: {len(common_patterns)}")
        console.print(f"  Missing from target: {len(missing_from_target)}")
        console.print(f"  Extra in target: {len(extra_in_target)}")
        console.print()

        # Display missing patterns (in template but not in target)
        if missing_from_target:
            console.print(f"[bold green]Missing from Target[/bold green] ({len(missing_from_target)} patterns):")
            console.print("[dim]These patterns are in the template but not in your .gitignore[/dim]")
            for pattern in sorted(missing_from_target):
                console.print(f"[green]  + {pattern}[/green]")
            console.print()

        # Display extra patterns (in target but not in template)
        if extra_in_target:
            console.print(f"[bold yellow]Extra in Target[/bold yellow] ({len(extra_in_target)} patterns):")
            console.print("[dim]These are custom patterns not in the template[/dim]")
            for pattern in sorted(extra_in_target):
                console.print(f"[yellow]  ! {pattern}[/yellow]")
            console.print()

        # Display common patterns count
        if common_patterns:
            console.print(f"[bold cyan]Common Patterns[/bold cyan] ({len(common_patterns)} patterns):")
            console.print("[dim]These patterns exist in both files[/dim]")
            # Just show count by default to avoid clutter
            console.print(f"[cyan]  {len(common_patterns)} patterns in common[/cyan]")
            console.print()

        self.logger.info(f"GitIgnore set-based comparison: {len(missing_from_target)} missing, "
                        f"{len(extra_in_target)} extra, {len(common_patterns)} common")
        return False

    def compare_gitignore(self) -> bool:
        """Compare target .gitignore with template and display diff.

        Routes to appropriate comparison method based on comparison mode.

        Returns:
            True if files are identical, False otherwise
        """
        # Route to set-based comparison if mode is 'set'
        if self.config.gitignore_compare_mode == "set":
            self.logger.info("Using set-based comparison mode")
            return self.compare_gitignore_set()

        # Default: unified diff comparison
        self.logger.info("Using unified diff comparison mode")
        template_path = self.get_gitignore_template_path(self.config.gitignore_lang)
        target_path = self.config.target_dir / ".gitignore"

        template_lines = self.read_gitignore_lines(template_path)
        target_lines = self.read_gitignore_lines(target_path)

        if not target_path.exists():
            console.print(f"\n[yellow]⚠ Target .gitignore does not exist: {target_path}[/yellow]")
            console.print(f"[dim]Comparing against empty file[/dim]\n")

        # Generate unified diff
        diff = list(difflib.unified_diff(
            target_lines,
            template_lines,
            fromfile=str(target_path),
            tofile=f"template ({self.config.gitignore_lang})",
            lineterm=''
        ))

        if not diff:
            console.print("[green]✓ Files are identical - no changes needed[/green]")
            self.logger.info("GitIgnore files are identical")
            return True

        # Display diff with color coding
        console.print("[bold]Diff Output:[/bold]\n")
        for line in diff:
            if line.startswith('+++') or line.startswith('---'):
                console.print(f"[cyan]{line}[/cyan]")
            elif line.startswith('+'):
                console.print(f"[green]{line}[/green]")
            elif line.startswith('-'):
                console.print(f"[red]{line}[/red]")
            elif line.startswith('@@'):
                console.print(f"[yellow]{line}[/yellow]")
            else:
                console.print(line)

        self.logger.info(f"GitIgnore comparison completed: {len(diff)} diff lines")
        return False

    def merge_gitignore(self) -> None:
        """Merge template .gitignore into target (preserves all existing lines)."""
        template_path = self.get_gitignore_template_path(self.config.gitignore_lang)
        target_path = self.config.target_dir / ".gitignore"
        backup_path = self.config.target_dir / ".gitignore.backup"

        template_lines = self.read_gitignore_lines(template_path)
        target_lines = self.read_gitignore_lines(target_path)

        # Convert to sets for comparison (excluding empty lines and comments for dedup)
        def is_content_line(line):
            stripped = line.strip()
            return stripped and not stripped.startswith('#')

        existing_content = {line for line in target_lines if is_content_line(line)}
        template_content = {line for line in template_lines if is_content_line(line)}

        # Find lines to add
        lines_to_add = template_content - existing_content

        if not lines_to_add:
            console.print("[green]✓ Target .gitignore already contains all template patterns[/green]")
            self.logger.info("No new lines to merge")
            return

        # Build merged content: keep all target lines, then add missing template lines
        merged_lines = target_lines.copy()

        # Add separator if target had content
        if target_lines and target_lines[-1].strip():
            merged_lines.append("")

        # Add new patterns with a header
        if lines_to_add:
            merged_lines.append(f"# Added from {self.config.gitignore_lang} template")
            for line in template_lines:
                if is_content_line(line) and line in lines_to_add:
                    merged_lines.append(line)

        self.config.gitignore_lines_added = len(lines_to_add)

        # Display preview
        console.print(f"\n[bold]Lines to be added:[/bold] {len(lines_to_add)}")
        for line in sorted(lines_to_add):
            console.print(f"[green]+ {line}[/green]")

        if not self.config.execute:
            console.print("\n[yellow]⚠ This is a DRY RUN. Use --execute to perform merge.[/yellow]")
            self.logger.info(f"Merge preview: {len(lines_to_add)} lines would be added")
            return

        # Execute merge
        try:
            # Create backup if target exists
            if target_path.exists():
                shutil.copy2(target_path, backup_path)
                console.print(f"\n[cyan]Backup created: {backup_path}[/cyan]")
                self.logger.info(f"Backup created: {backup_path}")

            # Write merged content
            with open(target_path, 'w', encoding='utf-8') as f:
                f.write('\n'.join(merged_lines))
                if merged_lines and not merged_lines[-1] == '':
                    f.write('\n')

            console.print(f"[green]✓ Merged {len(lines_to_add)} new patterns into {target_path}[/green]")
            self.logger.info(f"Merged {len(lines_to_add)} patterns into .gitignore")

        except Exception as e:
            console.print(f"[red]✗ Failed to merge .gitignore: {e}[/red]")
            self.logger.error(f"Failed to merge .gitignore: {e}")
            raise

    def replace_gitignore(self) -> None:
        """Replace target .gitignore completely with template."""
        template_path = self.get_gitignore_template_path(self.config.gitignore_lang)
        target_path = self.config.target_dir / ".gitignore"
        backup_path = self.config.target_dir / ".gitignore.backup"

        template_lines = self.read_gitignore_lines(template_path)
        target_lines = self.read_gitignore_lines(target_path)

        self.config.gitignore_lines_added = len(template_lines)
        self.config.gitignore_lines_removed = len(target_lines)

        # Display warning
        console.print("\n[bold red]⚠ WARNING: REPLACE Operation[/bold red]")
        console.print(f"This will completely replace your .gitignore file with the {self.config.gitignore_lang} template.")

        if target_path.exists():
            console.print(f"\n[yellow]Current .gitignore:[/yellow] {len(target_lines)} lines")
        else:
            console.print(f"\n[yellow]Target .gitignore does not exist - will create new file[/yellow]")

        console.print(f"[green]Template:[/green] {len(template_lines)} lines")

        if not self.config.execute:
            console.print("\n[yellow]⚠ This is a DRY RUN. Use --execute to perform replacement.[/yellow]")
            self.logger.info(f"Replace preview: would replace with {len(template_lines)} lines")
            return

        # Execute replacement
        try:
            # Create backup if target exists
            if target_path.exists():
                shutil.copy2(target_path, backup_path)
                console.print(f"\n[cyan]Backup created: {backup_path}[/cyan]")
                self.logger.info(f"Backup created: {backup_path}")

            # Copy template to target
            shutil.copy2(template_path, target_path)

            console.print(f"[green]✓ Replaced .gitignore with {self.config.gitignore_lang} template[/green]")
            self.logger.info(f"Replaced .gitignore with {self.config.gitignore_lang} template")

        except Exception as e:
            console.print(f"[red]✗ Failed to replace .gitignore: {e}[/red]")
            self.logger.error(f"Failed to replace .gitignore: {e}")
            raise

    def display_gitignore_header(self) -> None:
        """Display header for gitignore operations."""
        operation_names = {
            'compare': 'COMPARE / DIFF',
            'merge': 'MERGE',
            'replace': 'REPLACE'
        }
        operation = operation_names.get(self.config.gitignore_execute, self.config.gitignore_execute.upper())

        exec_str = "[green]EXECUTE MODE[/green]" if self.config.execute else "[yellow]DRY RUN[/yellow]"

        template_path = self.get_gitignore_template_path(self.config.gitignore_lang)

        header_text = f"""[bold]Claude Code Setup Tool - GitIgnore Management[/bold]

Target: [cyan]{self.config.target_dir}[/cyan]
Language: [cyan]{self.config.gitignore_lang}[/cyan]
Operation: [cyan]{operation}[/cyan]
Status: {exec_str}
Template: [dim]{template_path}[/dim]"""

        # Add comparison mode for compare operations
        if self.config.gitignore_execute == 'compare':
            mode_upper = self.config.gitignore_compare_mode.upper()
            mode_desc = "(order-independent pattern comparison)" if self.config.gitignore_compare_mode == "set" else "(line-by-line unified diff)"
            header_text += f"\nComparison Mode: [cyan]{mode_upper}[/cyan] [dim]{mode_desc}[/dim]"

        console.print(Panel(header_text, box=box.ROUNDED, border_style="blue"))

    def display_gitignore_summary(self) -> None:
        """Display summary of gitignore operation."""
        backup_path = self.config.target_dir / ".gitignore.backup"

        if self.config.gitignore_execute == 'compare':
            return  # No summary needed for compare

        summary_lines = []

        if self.config.execute:
            summary_lines.append("[bold]Operation Complete[/bold]\n")

            if self.config.gitignore_execute == 'merge':
                summary_lines.append(f"• [green]{self.config.gitignore_lines_added}[/green] patterns added")
            elif self.config.gitignore_execute == 'replace':
                summary_lines.append(f"• [green]{self.config.gitignore_lines_added}[/green] lines in new file")
                if self.config.gitignore_lines_removed > 0:
                    summary_lines.append(f"• [yellow]{self.config.gitignore_lines_removed}[/yellow] lines in original file")

            if backup_path.exists():
                summary_lines.append(f"• [cyan]Backup saved:[/cyan] {backup_path}")

        summary_text = '\n'.join(summary_lines)

        if summary_text:
            console.print("\n" + "=" * 60)
            console.print(Panel(summary_text, box=box.ROUNDED, border_style="blue"))

    def run_gitignore_operations(self) -> int:
        """Run gitignore operations.

        Returns:
            Exit code (0 for success, 1 for error)
        """
        try:
            self.display_gitignore_header()

            # Validate template exists
            template_path = self.get_gitignore_template_path(self.config.gitignore_lang)
            if not template_path:
                available = self.get_available_gitignore_languages()
                console.print(f"\n[red]✗ Template not found for language: {self.config.gitignore_lang}[/red]")
                if available:
                    console.print(f"\n[yellow]Available languages:[/yellow] {', '.join(available)}")
                else:
                    console.print(f"\n[yellow]No gitignore templates found in: {self.artifact_store.store_base_path / 'git'}[/yellow]")
                self.logger.error(f"Template not found: {self.config.gitignore_lang}")
                return 1

            # Validate target directory
            if not self.validate_target_directory():
                return 1

            # Initialize operation logger after target directory is validated
            self.operation_logger = OperationLogger(self.config.target_dir, self.logger)

            console.print(f"\n[green]✓ Template found: {template_path.name}[/green]")

            # Execute operation
            if self.config.gitignore_execute == 'compare':
                self.compare_gitignore()
            elif self.config.gitignore_execute == 'merge':
                self.merge_gitignore()
            elif self.config.gitignore_execute == 'replace':
                self.replace_gitignore()
            else:
                console.print(f"[red]✗ Unknown operation: {self.config.gitignore_execute}[/red]")
                return 1

            # Display summary
            self.display_gitignore_summary()

            self.logger.info("GitIgnore operations completed successfully")

            # Log operation to JSONL
            operation_data = self._collect_gitignore_operation_data("success")
            self.operation_logger.log_operation(operation_data)

            return 0

        except KeyboardInterrupt:
            console.print("\n[yellow]Operation cancelled by user[/yellow]")
            self.logger.warning("Operation cancelled by user")

            # Log cancelled operation to JSONL
            if self.operation_logger:
                operation_data = self._collect_gitignore_operation_data("cancelled")
                self.operation_logger.log_operation(operation_data)

            return 130
        except Exception as e:
            console.print(f"\n[red]✗ Error: {e}[/red]")
            self.logger.error(f"Error: {e}", exc_info=True)

            # Log failed operation to JSONL
            if self.operation_logger:
                operation_data = self._collect_gitignore_operation_data("error", str(e))
                self.operation_logger.log_operation(operation_data)

            return 1

    def run(self) -> int:
        """Run the setup process."""
        # Check if this is a gitignore operation
        if self.config.gitignore_lang:
            return self.run_gitignore_operations()

        # Original artifact management flow
        try:
            self.display_header()

            # Validation
            if not self.validate_store():
                return 1

            if not self.validate_target_directory():
                return 1

            # Initialize operation logger after target directory is validated
            self.operation_logger = OperationLogger(self.config.target_dir, self.logger)

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

            # Log operation to JSONL
            operation_data = self._collect_artifact_operation_data("success")
            self.operation_logger.log_operation(operation_data)

            return 0

        except KeyboardInterrupt:
            console.print("\n[yellow]Operation cancelled by user[/yellow]")
            self.logger.warning("Operation cancelled by user")

            # Log cancelled operation to JSONL
            if self.operation_logger:
                operation_data = self._collect_artifact_operation_data("cancelled")
                self.operation_logger.log_operation(operation_data)

            return 130
        except Exception as e:
            console.print(f"\n[red]✗ Error: {e}[/red]")
            self.logger.error(f"Error: {e}", exc_info=True)

            # Log failed operation to JSONL
            if self.operation_logger:
                operation_data = self._collect_artifact_operation_data("error", str(e))
                self.operation_logger.log_operation(operation_data)

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


def show_examples():
    """Display usage examples in a well-formatted way."""
    console.print(Panel("[bold cyan]Claude Code Setup - Usage Examples[/bold cyan]",
                       box=box.DOUBLE))

    # Artifact Management Examples
    console.print("\n[bold green]📦 Artifact Management[/bold green]")
    console.print("=" * 60)

    examples = [
        ("Dry run (analysis only)", [
            "uv run cc_setup --target /path/to/project --mode basic",
            "uv run cc_setup -t /path/to/project -m basic"
        ]),
        ("Execute basic mode", [
            "uv run cc_setup --target /path/to/project --mode basic --execute",
            "uv run cc_setup -t /path/to/project -m basic -ex"
        ]),
        ("Execute iso mode with overwrite", [
            "uv run cc_setup --target /path/to/project --mode iso --execute --overwrite",
            "uv run cc_setup -t /path/to/project -m iso -ex -ov"
        ]),
        ("Show available artifacts", [
            "uv run cc_setup --help-artifacts",
            "uv run cc_setup -ha"
        ])
    ]

    for title, commands in examples:
        console.print(f"\n[cyan]• {title}:[/cyan]")
        console.print(f"  [white]{commands[0]}[/white]")
        console.print(f"  [dim]{commands[1]}[/dim]")

    # GitIgnore Management Examples
    console.print("\n\n[bold green]📝 GitIgnore Management[/bold green]")
    console.print("=" * 60)

    gitignore_examples = [
        ("Compare .gitignore with template (unified diff)", [
            "uv run cc_setup --target /path/to/project --gitignore python",
            "uv run cc_setup -t /path/to/project -gi python"
        ]),
        ("Compare using set-based mode (order-independent)", [
            "uv run cc_setup --target /path/to/project --gitignore python --gitignore_compare_mode set",
            "uv run cc_setup -t /path/to/project -gi python -gic set"
        ]),
        ("Merge template into existing .gitignore (preserves all lines)", [
            "uv run cc_setup --target /path/to/project --gitignore python --gitignore_execute merge --execute",
            "uv run cc_setup -t /path/to/project -gi python -gix merge -ex"
        ]),
        ("Replace .gitignore with template", [
            "uv run cc_setup --target /path/to/project --gitignore csharp --gitignore_execute replace --execute",
            "uv run cc_setup -t /path/to/project -gi csharp -gix replace -ex"
        ])
    ]

    for title, commands in gitignore_examples:
        console.print(f"\n[cyan]• {title}:[/cyan]")
        console.print(f"  [white]{commands[0]}[/white]")
        console.print(f"  [dim]{commands[1]}[/dim]")

    console.print("\n")


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description="Claude Code Setup Tool - Copy artifacts and manage .gitignore files\n\nFor usage examples, run: cc_setup --help-examples",
        formatter_class=RichHelpFormatter
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
        "--execute", "-ex",
        action="store_true",
        help="Execute file operations (default: dry-run mode)"
    )

    parser.add_argument(
        "--overwrite", "-ov",
        action="store_true",
        help="Overwrite existing files (default: skip existing files)"
    )

    parser.add_argument(
        "--help-artifacts", "-ha",
        action="store_true",
        help="Show what artifacts are installed in each mode"
    )

    parser.add_argument(
        "--help-examples", "-hx",
        action="store_true",
        help="Show usage examples with both long-form and short-form commands"
    )

    parser.add_argument(
        "--gitignore", "-gi",
        type=str,
        metavar="LANGUAGE",
        help="Manage .gitignore file for specified language (e.g., 'python', 'csharp')"
    )

    parser.add_argument(
        "--gitignore_execute", "-gix",
        choices=["compare", "merge", "replace"],
        default="compare",
        help="GitIgnore operation: 'compare' (default), 'merge', or 'replace'"
    )

    parser.add_argument(
        "--gitignore_compare_mode", "-gic",
        choices=["diff", "set"],
        default="diff",
        help="GitIgnore comparison mode: 'diff' for unified diff (default), 'set' for set-based comparison"
    )

    args = parser.parse_args()

    # Handle --help-artifacts
    if args.help_artifacts:
        show_help_artifacts()
        return 0

    # Handle --help-examples
    if args.help_examples:
        show_examples()
        return 0

    # Validate required arguments
    if not args.target:
        parser.error("--target is required (unless using --help-artifacts or --help-examples)")

    # If gitignore is specified, mode is not required
    if args.gitignore:
        if args.mode:
            console.print("[yellow]⚠ Warning: --mode is ignored when using --gitignore[/yellow]")
    else:
        # If not gitignore mode, mode is required
        if not args.mode:
            parser.error("--mode is required (unless using --gitignore)")

    # Create config and run
    config = SetupConfig(args)
    setup = CCSetup(config)

    return setup.run()


if __name__ == "__main__":
    sys.exit(main())
