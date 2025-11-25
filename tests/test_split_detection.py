#!/usr/bin/env python3
"""Test split archive detection."""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

from archive_extractor import ArchiveExtractor

def test_split_detection():
    """Test that split archives are detected correctly."""
    print("Testing split archive detection...\n")

    extractor = ArchiveExtractor('archives')

    # Test files
    test_files = [
        'file.r00',
        'file.r01',
        'file.r99',
        'archive.z01',
        'data.001',
        'data.002',
        'package.7z.001',
        'main.rar',
        'test.zip',
        'document.txt',
        'program.exe'
    ]

    print("Testing _is_split_archive method:")
    print("-" * 60)
    for filename in test_files:
        is_split = extractor._is_split_archive(filename)
        status = "✓ SPLIT" if is_split else "  regular"
        print(f"  {status}: {filename}")

    print("\n" + "-" * 60)
    print("\nTesting _is_archive method (includes split archives):")
    print("-" * 60)
    for filename in test_files:
        file_path = Path(filename)
        is_archive = extractor._is_archive(file_path)
        status = "✓ ARCHIVE" if is_archive else "  regular"
        print(f"  {status}: {filename}")

    print("\n" + "=" * 60)
    print("Testing with actual files in archives directory...")
    print("=" * 60 + "\n")

    folders = extractor.scan_directories()

    for folder, has_archives in folders:
        print(f"\n{folder.name}:")
        print(f"  Has archives: {has_archives}")

        archives_found = []
        for root, _, files in os.walk(folder):
            for file in files:
                file_path = Path(root) / file
                if extractor._is_archive(file_path):
                    archives_found.append(file)

        if archives_found:
            print(f"  Archives found ({len(archives_found)}):")
            for archive in sorted(archives_found)[:10]:  # Show first 10
                print(f"    - {archive}")
            if len(archives_found) > 10:
                print(f"    ... and {len(archives_found) - 10} more")
        else:
            print("  No archives found")

if __name__ == '__main__':
    import os
    test_split_detection()
