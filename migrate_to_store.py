#!/usr/bin/env python3
"""
One-time migration script to copy artifacts from d:\tac to local store.
Creates a detailed log of all copied files in store/migration_log.txt
"""

from pathlib import Path
import shutil
from datetime import datetime

SOURCE_BASE = Path(r"d:\tac")
STORE_BASE = Path(__file__).parent / "store"
LOG_FILE = STORE_BASE / "migration_log.txt"


class MigrationLogger:
    """Handle logging of migration operations."""

    def __init__(self, log_file: Path):
        self.log_file = log_file
        self.log_file.parent.mkdir(parents=True, exist_ok=True)
        self.entries = []
        self.files_copied = 0
        self.files_skipped = 0

    def log_copy(self, source: Path, destination: Path, success: bool = True):
        """Log a file copy operation."""
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        status = "COPIED" if success else "FAILED"
        entry = f"[{timestamp}] {status}: {source} -> {destination}"
        self.entries.append(entry)
        print(entry)

        if success:
            self.files_copied += 1

    def log_skip(self, source: Path, reason: str):
        """Log a skipped file."""
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        entry = f"[{timestamp}] SKIPPED: {source} - {reason}"
        self.entries.append(entry)
        print(f"  {reason}: {source}")
        self.files_skipped += 1

    def log_info(self, message: str):
        """Log an informational message."""
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        entry = f"[{timestamp}] INFO: {message}"
        self.entries.append(entry)
        print(message)

    def log_section(self, title: str):
        """Log a section header."""
        separator = "=" * 80
        self.entries.append("")
        self.entries.append(separator)
        self.entries.append(title)
        self.entries.append(separator)
        print(f"\n{separator}")
        print(title)
        print(separator)

    def write_log(self):
        """Write all log entries to file."""
        with open(self.log_file, 'w', encoding='utf-8') as f:
            f.write("\n".join(self.entries))
            f.write("\n\n")
            f.write("=" * 80 + "\n")
            f.write("MIGRATION SUMMARY\n")
            f.write("=" * 80 + "\n")
            f.write(f"Files copied: {self.files_copied}\n")
            f.write(f"Files skipped: {self.files_skipped}\n")
            f.write(f"Total processed: {self.files_copied + self.files_skipped}\n")

        print(f"\n✓ Migration log written to: {self.log_file}")


def migrate_mode(source_repo: str, target_mode: str, logger: MigrationLogger):
    """Migrate artifacts from source repo to target mode."""
    logger.log_section(f"MIGRATING {target_mode.upper()} MODE FROM {source_repo}")

    source_base = SOURCE_BASE / source_repo
    target_base = STORE_BASE / target_mode

    # Check if source exists
    if not source_base.exists():
        logger.log_info(f"WARNING: Source repository not found: {source_base}")
        logger.log_info(f"Skipping {target_mode} mode migration")
        return

    # Ensure target directories exist
    target_base.mkdir(parents=True, exist_ok=True)
    logger.log_info(f"Created target directory: {target_base}")

    # Migrate settings.json
    logger.log_info("\nMigrating settings.json...")
    settings_src = source_base / ".claude" / "settings.json"
    settings_dst = target_base / "settings.json"

    if settings_src.exists():
        try:
            shutil.copy2(settings_src, settings_dst)
            logger.log_copy(settings_src, settings_dst)
        except Exception as e:
            logger.log_info(f"ERROR: Failed to copy settings.json: {e}")
    else:
        logger.log_skip(settings_src, "File not found")

    # Migrate categories
    migrations = [
        (".claude/hooks", "hooks"),
        (".claude/commands", "commands"),
        ("scripts", "scripts"),
        ("adws", "adws"),
    ]

    for source_subdir, target_subdir in migrations:
        logger.log_info(f"\nMigrating {target_subdir}...")
        source_path = source_base / source_subdir
        target_path = target_base / target_subdir

        if not source_path.exists():
            logger.log_skip(source_path, "Directory not found")
            continue

        target_path.mkdir(parents=True, exist_ok=True)

        # Copy all files (not directories)
        files_in_category = 0
        for item in source_path.iterdir():
            if item.is_file():
                dst = target_path / item.name
                try:
                    shutil.copy2(item, dst)
                    logger.log_copy(item, dst)
                    files_in_category += 1
                except Exception as e:
                    logger.log_info(f"ERROR: Failed to copy {item}: {e}")
            elif item.is_dir():
                # Skip directories like utils, adw_modules, etc.
                logger.log_skip(item, "Skipping directory")

        if files_in_category == 0:
            logger.log_info(f"  No files found in {source_subdir}")


def main():
    """Main migration function."""
    print("=" * 80)
    print("CLAUDE CODE ARTIFACT MIGRATION")
    print("=" * 80)
    print(f"\nMigrating artifacts from: {SOURCE_BASE}")
    print(f"To local store at: {STORE_BASE}")
    print(f"Log file: {LOG_FILE}")
    print()

    # Create logger
    logger = MigrationLogger(LOG_FILE)

    # Log header
    logger.log_section("MIGRATION STARTED")
    logger.log_info(f"Source base: {SOURCE_BASE}")
    logger.log_info(f"Store base: {STORE_BASE}")
    logger.log_info(f"Timestamp: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

    # Migrate basic mode
    migrate_mode("tac-6", "basic", logger)

    # Migrate iso mode
    migrate_mode("tac-7", "iso", logger)

    # Write final log
    logger.log_section("MIGRATION COMPLETE")
    logger.log_info(f"Total files copied: {logger.files_copied}")
    logger.log_info(f"Total files skipped: {logger.files_skipped}")
    logger.write_log()

    print("\n" + "=" * 80)
    print("SUMMARY")
    print("=" * 80)
    print(f"✓ Files copied: {logger.files_copied}")
    print(f"⚠ Files skipped: {logger.files_skipped}")
    print(f"📝 Log file: {LOG_FILE}")
    print("\n✓ Migration complete!")


if __name__ == "__main__":
    main()
