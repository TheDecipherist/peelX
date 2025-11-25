#!/usr/bin/env python3
"""Quick test to verify all folders are scanned for executables."""

from archive_extractor import ArchiveExtractor
from pathlib import Path

def test_executable_scanning():
    """Test that executables are found in all folders."""
    print("Testing executable scanning...\n")

    extractor = ArchiveExtractor('archives')

    # Scan all directories
    folders = extractor.scan_directories()

    print(f"Found {len(folders)} folders:")
    for folder, has_archives in folders:
        status = "HAS ARCHIVES" if has_archives else "NO ARCHIVES"
        print(f"  [{status}] {folder.name}")

    print("\nScanning for executables in ALL folders:\n")

    all_executables = []
    for folder, _ in folders:
        executables = extractor.find_executables(folder)
        if executables:
            print(f"  {folder.name}:")
            for exe in executables:
                rel_path = exe.relative_to(folder)
                print(f"    - {rel_path}")
        all_executables.extend(executables)

    print(f"\nTotal executables found: {len(all_executables)}")

    if all_executables:
        print("\n✓ SUCCESS: Executables found in folders (including those without archives)")
    else:
        print("\n✗ No executables found")

if __name__ == '__main__':
    test_executable_scanning()
