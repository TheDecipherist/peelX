#!/usr/bin/env python3
"""Test that split archives will be deleted."""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

from archive_extractor import ArchiveExtractor

def test_archive_deletion_detection():
    """Test which files will be deleted as archives."""
    print("Testing which files will be marked for deletion...\n")

    extractor = ArchiveExtractor('archives')

    folders = extractor.scan_directories()

    for folder, has_archives in folders:
        print(f"\n{folder.name}:")
        print("=" * 60)

        if not has_archives:
            print("  No archives - folder will not be processed")
            continue

        archives_to_delete = []
        other_files = []

        for root, _, files in os.walk(folder):
            for file in files:
                file_path = Path(root) / file
                if extractor._is_archive(file_path):
                    archives_to_delete.append(file)
                else:
                    other_files.append(file)

        print(f"\n  Files to DELETE ({len(archives_to_delete)}):")
        for archive in sorted(archives_to_delete):
            print(f"    ✗ {archive}")

        print(f"\n  Files to KEEP ({len(other_files)}):")
        for file in sorted(other_files):
            print(f"    ✓ {file}")

if __name__ == '__main__':
    import os
    test_archive_deletion_detection()
