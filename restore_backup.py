#!/usr/bin/env python3
"""
Restore archives from backup.
Use this if extraction failed and you need to restore the original archive files.
"""

import os
import sys
import shutil
from pathlib import Path
from datetime import datetime


def list_backups(backup_dir: Path):
    """List all available backups."""
    if not backup_dir.exists():
        print(f"No backup directory found at: {backup_dir}")
        return []

    backups = [d for d in backup_dir.iterdir() if d.is_dir()]
    backups.sort(key=lambda x: x.name, reverse=True)

    return backups


def restore_backup(backup_path: Path, target_dir: Path):
    """Restore a backup to the target directory."""
    if not backup_path.exists():
        print(f"Backup not found: {backup_path}")
        return False

    print(f"\nRestoring from: {backup_path.name}")
    print(f"To: {target_dir}")
    print("-" * 60)

    restored_count = 0

    for root, _, files in os.walk(backup_path):
        for file in files:
            src_file = Path(root) / file
            rel_path = src_file.relative_to(backup_path)
            dest_file = target_dir / rel_path

            dest_file.parent.mkdir(parents=True, exist_ok=True)

            try:
                shutil.copy2(src_file, dest_file)
                restored_count += 1
                print(f"  Restored: {rel_path}")
            except Exception as e:
                print(f"  ✗ Failed to restore {rel_path}: {e}")

    print(f"\nTotal files restored: {restored_count}")
    return restored_count > 0


def main():
    """Main restore function."""
    import argparse

    parser = argparse.ArgumentParser(description='Restore archives from backup')
    parser.add_argument('directory', nargs='?', default='archives',
                       help='Base directory (default: archives)')
    parser.add_argument('--list', action='store_true',
                       help='List available backups')
    parser.add_argument('--backup', type=str,
                       help='Backup folder name to restore')
    parser.add_argument('--latest', action='store_true',
                       help='Restore the most recent backup')

    args = parser.parse_args()

    base_dir = Path(args.directory)
    backup_dir = base_dir / '.backups'

    print("\n" + "="*60)
    print("  Archive Restore Tool")
    print("="*60 + "\n")

    backups = list_backups(backup_dir)

    if not backups:
        print("No backups found.")
        print(f"Backup directory: {backup_dir}")
        return

    if args.list:
        print(f"Available backups in {backup_dir}:\n")
        for idx, backup in enumerate(backups, 1):
            folder_name = backup.name
            # Parse timestamp if present
            if '_' in folder_name:
                parts = folder_name.rsplit('_', 2)
                if len(parts) == 3:
                    name, date, time = parts
                    try:
                        dt = datetime.strptime(f"{date}_{time}", "%Y%m%d_%H%M%S")
                        print(f"  [{idx}] {name}")
                        print(f"      Date: {dt.strftime('%Y-%m-%d %H:%M:%S')}")
                        print(f"      Path: {backup}")
                        print()
                        continue
                    except ValueError:
                        pass
            print(f"  [{idx}] {folder_name}")
            print(f"      Path: {backup}")
            print()
        return

    if args.latest:
        if backups:
            backup_to_restore = backups[0]
            print(f"Restoring latest backup: {backup_to_restore.name}\n")
        else:
            print("No backups available.")
            return
    elif args.backup:
        # Find backup by name
        backup_to_restore = None
        for backup in backups:
            if args.backup in backup.name:
                backup_to_restore = backup
                break

        if not backup_to_restore:
            print(f"Backup not found: {args.backup}")
            print("\nUse --list to see available backups")
            return
    else:
        # Interactive selection
        print("Available backups:\n")
        for idx, backup in enumerate(backups, 1):
            print(f"  [{idx}] {backup.name}")

        print()
        try:
            choice = int(input("Select backup to restore (number): "))
            if 1 <= choice <= len(backups):
                backup_to_restore = backups[choice - 1]
            else:
                print("Invalid selection.")
                return
        except (ValueError, EOFError):
            print("Invalid input.")
            return

    # Extract folder name from backup
    backup_name = backup_to_restore.name
    if '_' in backup_name:
        original_folder = backup_name.rsplit('_', 2)[0]
    else:
        original_folder = backup_name

    target_dir = base_dir / original_folder

    print(f"\n⚠ Warning: This will restore archive files to:")
    print(f"  {target_dir}")
    print("\nAny existing files with the same names will be overwritten.")

    try:
        confirm = input("\nContinue? (yes/no): ").strip().lower()
        if confirm not in ['yes', 'y']:
            print("Restore cancelled.")
            return
    except EOFError:
        print("\nRestore cancelled.")
        return

    if restore_backup(backup_to_restore, target_dir):
        print("\n✓ Restore completed successfully!")
    else:
        print("\n✗ Restore failed.")

    print("\n" + "="*60)


if __name__ == '__main__':
    main()
