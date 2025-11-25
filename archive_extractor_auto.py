#!/usr/bin/env python3
"""
Archive Extractor - Auto Mode
Automatically processes all folders with archives without user prompts.
Usage: python archive_extractor_auto.py [directory] [--no-delete] [--no-run]
"""

import sys
import argparse
from pathlib import Path
from archive_extractor import ArchiveExtractor


def main():
    """Main application entry point for auto mode."""
    parser = argparse.ArgumentParser(description='Archive Extractor - Automatic Mode')
    parser.add_argument('directory', nargs='?', default='archives',
                       help='Directory to scan (default: archives)')
    parser.add_argument('--no-delete', action='store_true',
                       help='Do not delete archives after extraction')
    parser.add_argument('--no-run', action='store_true',
                       help='Do not run executables, just extract')
    parser.add_argument('--list-only', action='store_true',
                       help='Only list folders and archives, do not extract')
    parser.add_argument('--dry-run', action='store_true',
                       help='Preview actions without extracting or deleting anything')
    parser.add_argument('--backup', action='store_true',
                       help='Create backup before deleting archives')
    parser.add_argument('--debug', action='store_true',
                       help='Enable debug mode with detailed output (shows file names)')

    args = parser.parse_args()

    print("\n" + "="*60)
    print("  Archive Extractor - Automatic Mode")
    print("="*60 + "\n")

    if args.dry_run:
        print("🔍 DRY-RUN MODE: No files will be modified")
        print("="*60 + "\n")

    if args.debug:
        print("🐛 DEBUG MODE: Detailed output enabled")
        print("="*60 + "\n")

    extractor = ArchiveExtractor(args.directory, dry_run=args.dry_run, debug=args.debug)

    print(f"Scanning directory: {extractor.base_dir.absolute()}\n")

    # Scan for folders
    folders = extractor.scan_directories()

    if not folders:
        print("No folders found.")
        return

    folders_with_archives = [f for f in folders if f[1]]

    if not folders_with_archives:
        print("No folders contain archives to extract.")
        return

    print("Folders found:")
    print("-" * 60)
    for folder, has_archives in folders:
        status = "[HAS ARCHIVES]" if has_archives else "[NO ARCHIVES]"
        print(f"  {status} {folder.name}")
    print("-" * 60)

    if args.list_only:
        print(f"\nTotal folders with archives: {len(folders_with_archives)}")
        return

    print(f"\nProcessing {len(folders_with_archives)} folder(s) with archives...\n")

    # Extract archives
    print("="*60)
    print("Extracting Archives")
    print("="*60 + "\n")

    for folder, _ in folders_with_archives:
        print(f"Processing: {folder.name}")
        extractor.extract_all_archives_recursive(folder)
        print()

    # Backup archives if requested
    if args.backup and not args.no_delete and not args.dry_run:
        print("="*60)
        print("Backing Up Archives")
        print("="*60 + "\n")

        backup_dir = extractor.base_dir / '.backups'
        backup_dir.mkdir(exist_ok=True)

        total_backed_up = 0
        for folder, _ in folders_with_archives:
            print(f"Backing up: {folder.name}")
            backed_up = extractor.backup_archives(folder, backup_dir)
            total_backed_up += backed_up
            print()

        print(f"Total archives backed up: {total_backed_up}\n")

    # Delete archives if requested
    if not args.no_delete:
        print("="*60)
        print("Cleaning Up Archives")
        print("="*60 + "\n")

        total_deleted = 0
        for folder, _ in folders_with_archives:
            print(f"Cleaning: {folder.name}")
            deleted = extractor.delete_archives(folder)
            total_deleted += deleted
            print()

        if args.dry_run:
            print(f"Total archives that would be deleted: {total_deleted}\n")
        else:
            print(f"Total archives deleted: {total_deleted}\n")
    else:
        print("\n--no-delete flag set, keeping archive files\n")

    # Find executables in ALL folders (not just those with archives)
    all_executables = []
    for folder, _ in folders:
        executables = extractor.find_executables(folder)
        all_executables.extend(executables)

    if all_executables:
        print("="*60)
        print("Executables Found")
        print("="*60 + "\n")

        for idx, exe in enumerate(all_executables, 1):
            try:
                rel_path = exe.relative_to(extractor.base_dir)
            except ValueError:
                rel_path = exe
            print(f"  [{idx}] {rel_path}")

        if not args.no_run:
            print("\nTo run executables, use interactive mode:")
            print("  python archive_extractor.py")
        print()
    else:
        print("\nNo executables found in the processed folders.\n")

    print("="*60)
    print("Done!")
    print("="*60 + "\n")


if __name__ == '__main__':
    main()
