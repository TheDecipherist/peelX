#!/usr/bin/env python3
"""
PeelX - Archive Extractor & Runner
Scans directories, extracts nested archives, and provides an interface to run executables.
"""

import os
import sys
import re
import zipfile
import tarfile
import shutil
import subprocess
import platform
import datetime
from pathlib import Path
from typing import List, Set, Tuple

# Try importing interactive selector at module level so PyInstaller bundles it
try:
    from peelx.interactive_selector import select_executable_interactive
    _HAS_INTERACTIVE = True
except Exception as _e:
    _HAS_INTERACTIVE = False
    _INTERACTIVE_ERROR = str(_e)


class PeelX:
    """Handles scanning, extracting, and managing archives in directories."""

    # Supported archive extensions
    ARCHIVE_EXTENSIONS = {'.zip', '.rar', '.7z', '.tar', '.gz', '.bz2', '.xz', '.tgz', '.tbz2'}

    # Split archive patterns (will be checked separately)
    # RAR split: .r00, .r01, .r02, etc.
    # ZIP split: .z01, .z02, etc.
    # Generic: .001, .002, .003, etc.
    # 7z split: .7z.001, .7z.002, etc.

    # Executable extensions by platform
    EXECUTABLE_EXTENSIONS = {
        'Windows': {'.exe', '.bat', '.cmd', '.msi'},
        'Linux': {'.sh', '.bin', '.run', ''},  # Empty string for files with execute permission
        'Darwin': {'.app', '.sh', '.command', ''}  # macOS
    }

    # File extensions to exclude from executable detection
    NON_EXECUTABLE_EXTENSIONS = {
        '.nfo', '.txt', '.md', '.sfv', '.diz', '.readme',
        '.log', '.ini', '.cfg', '.conf', '.json', '.xml',
        '.jpg', '.jpeg', '.png', '.gif', '.bmp',
        '.mp3', '.wav', '.flac', '.ogg',
        '.pdf', '.doc', '.docx'
    }

    # Checksum and metadata files that should be deleted with archives
    ARCHIVE_METADATA_EXTENSIONS = {
        '.sfv',      # Simple File Verification
        '.md5',      # MD5 checksums
        '.sha1',     # SHA1 checksums
        '.sha256',   # SHA256 checksums
        '.crc',      # CRC checksums
        '.par2',     # Parity files
        '.par',      # Old parity files
    }

    def __init__(self, base_dir: str = 'archives', dry_run: bool = False, debug: bool = False):
        self.base_dir = Path(base_dir)
        self.current_platform = platform.system()
        self.dry_run = dry_run
        self.debug = debug

    def scan_directories(self) -> List[Tuple[Path, bool]]:
        """
        Scan the base directory for subdirectories.
        Returns list of (folder_path, has_archives) tuples.
        """
        if not self.base_dir.exists():
            return []

        folders = []
        for item in self.base_dir.iterdir():
            if item.is_dir():
                has_archives = self._has_archives(item)
                folders.append((item, has_archives))

        return folders

    def _is_split_archive(self, filename: str) -> bool:
        """Check if a file is a split archive part."""
        filename_lower = filename.lower()

        # RAR split: .r00, .r01, .r02, etc.
        if re.match(r'.*\.r\d{2,3}$', filename_lower):
            return True

        # ZIP split: .z01, .z02, etc.
        if re.match(r'.*\.z\d{2,3}$', filename_lower):
            return True

        # Generic numbered splits: .001, .002, .003, etc.
        if re.match(r'.*\.\d{3}$', filename_lower):
            return True

        # 7z split: .7z.001, .7z.002, etc.
        if re.match(r'.*\.7z\.\d{3}$', filename_lower):
            return True

        return False

    def _has_archives(self, directory: Path) -> bool:
        """Check if directory contains any archive files (recursively)."""
        for root, _, files in os.walk(directory):
            for file in files:
                file_path = Path(file)
                if file_path.suffix.lower() in self.ARCHIVE_EXTENSIONS:
                    return True
                if self._is_split_archive(file):
                    return True
        return False

    def _is_archive_or_metadata(self, file_path: Path) -> bool:
        """
        Check if a file is an archive, split archive part, or archive metadata file.
        This is used to determine what should be deleted after extraction.
        """
        filename = file_path.name

        suffix = file_path.suffix.lower()

        # Check standard archive extensions
        if suffix in self.ARCHIVE_EXTENSIONS:
            return True

        # Check split archive patterns
        if self._is_split_archive(filename):
            return True

        # Check archive metadata files (.sfv, .md5, etc.)
        if suffix in self.ARCHIVE_METADATA_EXTENSIONS:
            return True

        return False

    def _is_archive(self, file_path: Path) -> bool:
        """Check if a file is an archive or split archive part (for deletion purposes)."""
        # Kept for backward compatibility, now calls the new method
        return self._is_archive_or_metadata(file_path)

    def _is_extractable_archive(self, file_path: Path) -> bool:
        """
        Check if a file should be extracted.
        Split archive parts (.r00, .r01, etc.) should NOT be extracted individually.
        Only the main archive file should be extracted.
        """
        filename = file_path.name

        # Don't try to extract split archive parts
        if self._is_split_archive(filename):
            return False

        # Extract standard archive files
        return file_path.suffix.lower() in self.ARCHIVE_EXTENSIONS

    def extract_archive(self, archive_path: Path, extract_to: Path) -> bool:
        """
        Extract an archive file to the specified directory.
        Returns True if successful, False otherwise.
        """
        archive_str = str(archive_path).lower()

        try:
            if archive_str.endswith('.zip'):
                with zipfile.ZipFile(archive_path, 'r') as zip_ref:
                    # Validate all members to prevent zip-slip path traversal
                    for member in zip_ref.namelist():
                        member_path = (extract_to / member).resolve()
                        if not str(member_path).startswith(str(extract_to.resolve())):
                            raise Exception(f"Path traversal detected in zip member: {member}")
                    zip_ref.extractall(extract_to)
                return True

            elif archive_str.endswith('.rar'):
                # Try system command first (more reliable for split archives)
                if self._extract_with_unrar(archive_path, extract_to):
                    return True
                # Fall back to Python library
                try:
                    import rarfile
                    with rarfile.RarFile(archive_path, 'r') as rar_ref:
                        rar_ref.extractall(extract_to)
                    return True
                except ImportError:
                    print(f"  ✗ Could not extract RAR. Install unrar or rarfile library.")
                    return False
                except Exception as e:
                    print(f"  ✗ rarfile extraction failed: {e}")
                    return False

            elif archive_str.endswith('.7z'):
                # Try system command first (more reliable, supports all compression methods)
                if self._extract_with_7z(archive_path, extract_to):
                    return True
                # Fall back to Python library
                try:
                    import py7zr
                    with py7zr.SevenZipFile(archive_path, 'r') as sz_ref:
                        sz_ref.extractall(extract_to)
                    return True
                except ImportError:
                    print(f"  ✗ Could not extract 7z. Install 7z or py7zr library.")
                    return False
                except Exception as e:
                    print(f"  ✗ py7zr extraction failed: {e}")
                    return False

            elif archive_str.endswith(('.tar', '.tar.gz', '.tgz', '.tar.bz2', '.tbz2', '.tar.xz')):
                with tarfile.open(archive_path, 'r:*') as tar_ref:
                    # Validate all members to prevent path traversal (CVE-2007-4559)
                    for member in tar_ref.getmembers():
                        member_path = (extract_to / member.name).resolve()
                        if not str(member_path).startswith(str(extract_to.resolve())):
                            raise Exception(f"Path traversal detected in tar member: {member.name}")
                    tar_ref.extractall(extract_to)
                return True

            elif archive_str.endswith('.gz') and not archive_str.endswith('.tar.gz'):
                import gzip
                output_file = extract_to / archive_path.stem
                with gzip.open(archive_path, 'rb') as f_in:
                    with open(output_file, 'wb') as f_out:
                        shutil.copyfileobj(f_in, f_out)
                return True

            elif archive_str.endswith('.bz2') and not archive_str.endswith('.tar.bz2'):
                import bz2
                output_file = extract_to / archive_path.stem
                with bz2.open(archive_path, 'rb') as f_in:
                    with open(output_file, 'wb') as f_out:
                        shutil.copyfileobj(f_in, f_out)
                return True

            else:
                print(f"  ⚠ Unsupported archive format: {archive_path.name}")
                return False

        except Exception as e:
            print(f"  ✗ Error extracting {archive_path.name}: {e}")
            return False

    def _extract_with_unrar(self, archive_path: Path, extract_to: Path) -> bool:
        """Attempt to extract RAR using system unrar command."""
        try:
            subprocess.run(['unrar', 'x', '-y', str(archive_path), str(extract_to) + os.sep],
                         check=True, capture_output=True, text=True)
            return True
        except FileNotFoundError:
            # unrar not installed, silently fail
            return False
        except subprocess.CalledProcessError as e:
            # Show error if extraction failed
            print(f"  ✗ unrar failed: {e.stderr.strip() if e.stderr else 'Unknown error'}")
            return False

    def _extract_with_7z(self, archive_path: Path, extract_to: Path) -> bool:
        """Attempt to extract 7z using system 7z command."""
        try:
            subprocess.run(['7z', 'x', f'-o{extract_to}', str(archive_path), '-y'],
                         check=True, capture_output=True, text=True)
            return True
        except FileNotFoundError:
            # 7z not installed, silently fail
            return False
        except subprocess.CalledProcessError as e:
            # Show error if extraction failed
            print(f"  ✗ 7z failed: {e.stderr.strip() if e.stderr else 'Unknown error'}")
            return False

    def extract_all_archives_recursive(self, directory: Path, processed: Set[str] = None) -> None:
        """
        Recursively extract all archives in a directory, including nested archives.
        """
        if processed is None:
            processed = set()

        max_iterations = 50  # Prevent infinite loops
        iteration = 0

        while iteration < max_iterations:
            archives_found = []

            # Find all extractable archives in current state (skip split parts)
            for root, _, files in os.walk(directory):
                for file in files:
                    file_path = Path(root) / file
                    if self._is_extractable_archive(file_path) and str(file_path) not in processed:
                        archives_found.append(file_path)

            if not archives_found:
                break  # No more archives to extract

            if self.debug:
                print(f"  Found {len(archives_found)} archive(s) to extract...")

            total_archives = len(archives_found)
            for idx, archive_path in enumerate(archives_found, 1):
                # Calculate progress percentage
                progress = int((idx / total_archives) * 100)

                if self.dry_run:
                    if self.debug:
                        print(f"    [DRY-RUN] Would extract: {archive_path.name}")
                    else:
                        print(f"\r  Extracting: {progress}%", end='', flush=True)
                    processed.add(str(archive_path))
                else:
                    if self.debug:
                        print(f"    [{progress}%] Extracting: {archive_path.name}")
                    else:
                        print(f"\r  Extracting: {progress}%", end='', flush=True)

                    extract_to = archive_path.parent

                    if self.extract_archive(archive_path, extract_to):
                        processed.add(str(archive_path))
                    else:
                        # Mark as processed even if failed to avoid retry
                        processed.add(str(archive_path))

            # Complete the progress line
            if not self.debug:
                print(f"\r  Extracting: 100% ✓")

            iteration += 1

        if iteration >= max_iterations:
            print(f"  ⚠ Reached maximum iteration limit. Some nested archives may remain.")

    def backup_archives(self, directory: Path, backup_dir: Path) -> int:
        """
        Create backup of all archive files before deletion.
        Returns count of backed up files.
        """
        backup_count = 0
        timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        folder_backup = backup_dir / f"{directory.name}_{timestamp}"

        for root, _, files in os.walk(directory):
            for file in files:
                file_path = Path(root) / file
                if self._is_archive(file_path):
                    # Create backup directory structure
                    rel_path = file_path.relative_to(directory)
                    backup_file = folder_backup / rel_path

                    backup_file.parent.mkdir(parents=True, exist_ok=True)

                    if self.dry_run:
                        backup_count += 1
                        print(f"    [DRY-RUN] Would backup: {file_path.name}")
                    else:
                        try:
                            shutil.copy2(file_path, backup_file)
                            backup_count += 1
                            print(f"    Backed up: {file_path.name}")
                        except Exception as e:
                            print(f"    ✗ Could not backup {file_path.name}: {e}")

        if backup_count > 0 and not self.dry_run:
            print(f"\n  📦 Backup saved to: {folder_backup}")

        return backup_count

    def delete_archives(self, directory: Path) -> int:
        """
        Delete all archive files in the directory.
        Returns count of deleted files.
        """
        deleted_count = 0

        # First, collect all files to delete for progress tracking
        files_to_delete = []
        for root, _, files in os.walk(directory):
            for file in files:
                file_path = Path(root) / file
                if self._is_archive(file_path):
                    files_to_delete.append(file_path)

        total_files = len(files_to_delete)
        if total_files == 0:
            return 0

        # Now delete with progress indicator
        for idx, file_path in enumerate(files_to_delete, 1):
            progress = int((idx / total_files) * 100)

            if self.dry_run:
                deleted_count += 1
                if self.debug:
                    print(f"    [DRY-RUN] Would delete: {file_path.name}")
                else:
                    print(f"\r  Cleaning up: {progress}%", end='', flush=True)
            else:
                try:
                    file_path.unlink()
                    deleted_count += 1
                    if self.debug:
                        print(f"    [{progress}%] Deleted: {file_path.name}")
                    else:
                        print(f"\r  Cleaning up: {progress}%", end='', flush=True)
                except Exception as e:
                    if self.debug:
                        print(f"    ✗ Could not delete {file_path.name}: {e}")

        # Complete the progress line
        if not self.debug:
            print(f"\r  Cleaning up: 100% ✓")

        return deleted_count

    def _is_wsl(self) -> bool:
        """Detect if running under Windows Subsystem for Linux."""
        try:
            return os.path.exists('/proc/version') and 'microsoft' in Path('/proc/version').read_text().lower()
        except Exception:
            return False

    def find_executables(self, directory: Path) -> List[Path]:
        """Find all executable files in the directory."""
        executables = []
        platform_exts = self.EXECUTABLE_EXTENSIONS.get(self.current_platform, set())

        # On WSL, also look for Windows executables
        if self.current_platform == 'Linux' and self._is_wsl():
            platform_exts = platform_exts | self.EXECUTABLE_EXTENSIONS.get('Windows', set())

        for root, _, files in os.walk(directory):
            for file in files:
                file_path = Path(root) / file

                suffix = file_path.suffix.lower()

                # Skip known non-executable extensions
                if suffix in self.NON_EXECUTABLE_EXTENSIONS:
                    continue

                # Skip archive files
                if self._is_archive(file_path):
                    continue

                # Check by extension
                if suffix in platform_exts and suffix:
                    executables.append(file_path)
                # Check by execute permission (Unix-like systems)
                elif self.current_platform in ['Linux', 'Darwin']:
                    if os.access(file_path, os.X_OK) and file_path.is_file():
                        executables.append(file_path)

        return executables

    def run_executable(self, executable_path: Path) -> None:
        """Run an executable file."""
        try:
            print(f"\n{'='*60}")
            print(f"Running: {executable_path}")
            print(f"{'='*60}\n")

            # Check if we're in WSL (Windows Subsystem for Linux)
            is_wsl = self._is_wsl()

            # Detect Windows executable extensions
            windows_exts = {'.exe', '.bat', '.cmd', '.msi'}
            is_windows_exe = executable_path.suffix.lower() in windows_exts

            if self.current_platform == 'Windows':
                abs_path = executable_path.resolve()
                try:
                    subprocess.run([str(abs_path)], cwd=str(abs_path.parent))
                except (PermissionError, OSError) as e:
                    # WinError 740: elevation required - retry with runas
                    if getattr(e, 'winerror', None) == 740:
                        print("  Requesting administrator privileges...")
                        import ctypes
                        ctypes.windll.shell32.ShellExecuteW(
                            None, "runas", str(abs_path), None,
                            str(abs_path.parent), 1
                        )
                    else:
                        raise
            elif is_wsl and is_windows_exe:
                # In WSL, convert Linux path to Windows path and run with cmd.exe
                print("  ℹ Detected WSL environment - converting path for Windows execution")

                # Convert to absolute path first
                abs_path = executable_path.resolve()
                abs_cwd = abs_path.parent

                # Convert /mnt/c/path to C:\path
                win_path = str(abs_path)
                if win_path.startswith('/mnt/'):
                    drive = win_path[5].upper()
                    win_path = f"{drive}:{win_path[6:]}".replace('/', '\\')

                # Get working directory in Windows format
                win_cwd = str(abs_cwd)
                if win_cwd.startswith('/mnt/'):
                    drive = win_cwd[5].upper()
                    win_cwd = f"{drive}:{win_cwd[6:]}".replace('/', '\\')

                print(f"  → Windows path: {win_path}")
                print(f"  → Working directory: {win_cwd}")
                print()

                # Run using Windows cmd.exe
                subprocess.run(['cmd.exe', '/c', f'cd /d "{win_cwd}" && "{win_path}"'])
            else:
                # Make sure it's executable
                os.chmod(executable_path, os.stat(executable_path).st_mode | 0o111)
                subprocess.run([str(executable_path)], cwd=executable_path.parent)

        except Exception as e:
            print(f"\n✗ Error running executable: {e}")


def print_header():
    """Print application header."""
    print("\n" + "="*60)
    print("  PeelX - Archive Extractor & Runner")
    print("="*60 + "\n")


def select_folders(folders: List[Tuple[Path, bool]]) -> Tuple[List[Path], List[Path]]:
    """
    Display folders and let user select which ones to process for extraction.
    Returns tuple of (folders_to_extract, all_selected_folders).
    """
    if not folders:
        print("No folders found in the directory.")
        return [], []

    folders_with_archives = [f for f in folders if f[1]]
    folders_without_archives = [f for f in folders if not f[1]]

    # Show all folders
    print("\nFolders found:")
    print("-" * 60)

    if folders_with_archives:
        print("With archives to extract:")
        for folder, _ in folders_with_archives:
            print(f"  • {folder.name}")

    if folders_without_archives:
        print("\nWithout archives (already ready):")
        for folder, _ in folders_without_archives:
            print(f"  • {folder.name}")

    print("-" * 60)

    if not folders_with_archives:
        print("\nNo folders contain archives to extract.")
        print("All folders are already ready to use!")
        # Return all folders for executable scanning
        return [], [f[0] for f in folders]

    print("\nSelect folders with archives to extract:")
    print("-" * 60)

    for idx, (folder, _) in enumerate(folders_with_archives, 1):
        print(f"  [{idx}] {folder.name}")

    print(f"  [A] All folders with archives")
    print(f"  [0] Skip extraction")
    print("-" * 60)

    while True:
        choice = input("\nSelect folders to extract (e.g., 1,3,5 or A for all): ").strip().upper()

        if choice == '0':
            # Skip extraction but still include all folders for executable scanning
            return [], [f[0] for f in folders]

        if choice == 'A':
            # Extract all folders with archives, and include all folders for executable scanning
            return [f[0] for f in folders_with_archives], [f[0] for f in folders]

        try:
            indices = [int(x.strip()) for x in choice.split(',')]
            selected = []

            for idx in indices:
                if 1 <= idx <= len(folders_with_archives):
                    selected.append(folders_with_archives[idx - 1][0])
                else:
                    print(f"Invalid selection: {idx}")
                    break
            else:
                if selected:
                    # Return selected folders to extract + all folders for executable scanning
                    return selected, [f[0] for f in folders]
        except ValueError:
            print("Invalid input. Please enter numbers separated by commas, 'A' for all, or '0' to skip.")


def select_executable(executables: List[Path], base_dir: Path, use_interactive: bool = True) -> Path:
    """
    Display executables and let user select which one to run.
    Returns selected executable path or None.
    """
    if not executables:
        print("\nNo executables found in the processed folders.")
        return None

    # Try interactive mode first
    if use_interactive and _HAS_INTERACTIVE:
        try:
            print("\n" + "="*60)
            print("Starting Interactive Selector...")
            print("Use ↑/↓ arrow keys to navigate, ENTER to select, q to quit")
            print("="*60)
            import time
            time.sleep(1)  # Brief pause to read instructions

            selected = select_executable_interactive(executables, base_dir)
            if selected is not None:
                return selected
            # If user quit (None), fall through to simple mode
            print("\n" + "="*60)
            print("Exited interactive mode")
            print("="*60)
            return None
        except Exception as e:
            print(f"\n⚠ Interactive mode failed: {e}")
            print("Using simple selection instead...")
    elif use_interactive and not _HAS_INTERACTIVE:
        print(f"\n⚠ Interactive mode not available: {_INTERACTIVE_ERROR}")
        print("Using simple selection")

    # Fallback: Simple text-based selection
    print("\n" + "="*60)
    print("Available Executables:")
    print("-" * 60)

    for idx, exe in enumerate(executables, 1):
        # Show relative path from base directory
        try:
            rel_path = exe.relative_to(base_dir)
        except ValueError:
            rel_path = exe
        print(f"  [{idx}] {rel_path}")

    print(f"  [0] Exit without running")
    print("-" * 60)

    while True:
        try:
            choice = input("\nSelect executable to run (number): ").strip()
            idx = int(choice)

            if idx == 0:
                return None

            if 1 <= idx <= len(executables):
                return executables[idx - 1]
            else:
                print(f"Please enter a number between 0 and {len(executables)}")
        except ValueError:
            print("Invalid input. Please enter a number.")
        except (EOFError, KeyboardInterrupt):
            return None


def main():
    """Main application entry point."""
    import argparse

    parser = argparse.ArgumentParser(description='PeelX - Archive Extractor & Runner')
    parser.add_argument('directory', nargs='?', default='archives',
                       help='Directory to scan (default: archives)')
    parser.add_argument('--dry-run', action='store_true',
                       help='Preview actions without extracting or deleting anything')
    parser.add_argument('--backup', action='store_true',
                       help='Create backup before deleting archives')
    parser.add_argument('--no-interactive', action='store_true',
                       help='Disable interactive selector, use simple text menu')
    parser.add_argument('--debug', action='store_true',
                       help='Enable debug mode with detailed output (shows file names)')

    args = parser.parse_args()

    print_header()

    if args.dry_run:
        print("🔍 DRY-RUN MODE: No files will be modified")
        print("="*60 + "\n")

    if args.debug:
        print("🐛 DEBUG MODE: Detailed output enabled")
        print("="*60 + "\n")

    target_dir = args.directory
    user_specified_dir = target_dir != 'archives'

    # If using default 'archives' dir and it doesn't exist, ask the user
    if not user_specified_dir and not Path(target_dir).exists():
        print("No 'archives' folder found in the current directory.\n")
        print("What would you like to do?")
        print("-" * 60)
        print("  [1] Create an 'archives' folder (put your archives there)")
        print("  [2] Scan the current directory instead")
        print("  [0] Exit")
        print("-" * 60)

        while True:
            try:
                choice = input("\nSelect an option: ").strip()
                if choice == '1':
                    Path(target_dir).mkdir(parents=True, exist_ok=True)
                    print(f"\nCreated '{target_dir}' folder.")
                    print("Add your archive folders there and run this again.")
                    return
                elif choice == '2':
                    target_dir = '.'
                    break
                elif choice == '0':
                    return
                else:
                    print("Please enter 1, 2, or 0.")
            except (EOFError, KeyboardInterrupt):
                return

    extractor = PeelX(target_dir, dry_run=args.dry_run, debug=args.debug)

    print(f"Scanning directory: {extractor.base_dir.absolute()}\n")

    # Step 1: Scan for folders
    folders = extractor.scan_directories()

    if not folders:
        print("No folders found. Please add some folders to the directory.")
        return

    # Step 2: Let user select folders to process
    folders_to_extract, all_folders = select_folders(folders)

    if not all_folders:
        print("\nNo folders to process. Exiting.")
        return

    # Step 3: Extract archives recursively (only for folders that need extraction)
    if folders_to_extract:
        print("\n" + "="*60)
        print("Extracting Archives")
        print("="*60 + "\n")

        for folder in folders_to_extract:
            print(f"Processing: {folder.name}")
            extractor.extract_all_archives_recursive(folder)
            print()

        # Step 4: Backup archives (if requested)
        if args.backup and not args.dry_run:
            print("="*60)
            print("Backing Up Archives")
            print("="*60 + "\n")

            backup_dir = extractor.base_dir / '.backups'
            backup_dir.mkdir(exist_ok=True)

            total_backed_up = 0
            for folder in folders_to_extract:
                print(f"Backing up: {folder.name}")
                backed_up = extractor.backup_archives(folder, backup_dir)
                total_backed_up += backed_up
                print()

            print(f"Total archives backed up: {total_backed_up}\n")

        # Step 5: Delete archives
        print("="*60)
        print("Cleaning Up Archives")
        print("="*60 + "\n")

        total_deleted = 0
        for folder in folders_to_extract:
            print(f"Cleaning: {folder.name}")
            deleted = extractor.delete_archives(folder)
            total_deleted += deleted
            print()

        if args.dry_run:
            print(f"Total archives that would be deleted: {total_deleted}\n")
        else:
            print(f"Total archives deleted: {total_deleted}\n")
    else:
        print("\nNo extraction needed, proceeding to executable selection...\n")

    # Step 5: Find and let user select executable to run from ALL folders
    all_executables = []
    for folder in all_folders:
        executables = extractor.find_executables(folder)
        all_executables.extend(executables)

    if all_executables:
        use_interactive = not args.no_interactive
        selected_exe = select_executable(all_executables, extractor.base_dir, use_interactive)

        if selected_exe:
            extractor.run_executable(selected_exe)
        else:
            print("\nNo executable selected. Exiting.")
    else:
        print("\nNo executables found in the processed folders.")

    print("\n" + "="*60)
    print("Done!")
    print("="*60 + "\n")


if __name__ == '__main__':
    main()
