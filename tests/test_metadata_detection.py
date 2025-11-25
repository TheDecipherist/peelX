#!/usr/bin/env python3
"""Test metadata file detection."""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

from archive_extractor import ArchiveExtractor

def test_metadata_detection():
    """Test that metadata files are detected correctly."""
    print("Testing metadata file detection...\n")

    extractor = ArchiveExtractor('archives')

    # Test files
    test_files = [
        # Archives
        'file.rar',
        'file.zip',
        'file.7z',
        # Split archives
        'file.r00',
        'file.r01',
        # Metadata files
        'file.sfv',
        'checksums.md5',
        'hashes.sha1',
        'verify.sha256',
        'recovery.par2',
        'backup.crc',
        # Keep files
        'readme.txt',
        'info.nfo',
        'program.exe',
        'image.jpg'
    ]

    print("Testing _is_archive_or_metadata method:")
    print("-" * 60)

    archives = []
    metadata = []
    keep = []

    for filename in test_files:
        file_path = Path(filename)
        is_archive_meta = extractor._is_archive_or_metadata(file_path)

        if is_archive_meta:
            ext = file_path.suffix.lower()
            if ext in extractor.ARCHIVE_METADATA_EXTENSIONS:
                status = "✗ METADATA"
                metadata.append(filename)
            else:
                status = "✗ ARCHIVE"
                archives.append(filename)
            print(f"  {status}: {filename}")
        else:
            status = "✓ KEEP"
            keep.append(filename)
            print(f"  {status}: {filename}")

    print("\n" + "=" * 60)
    print("Summary:")
    print("=" * 60)
    print(f"\nArchives to delete: {len(archives)}")
    for f in archives:
        print(f"  - {f}")

    print(f"\nMetadata to delete: {len(metadata)}")
    for f in metadata:
        print(f"  - {f}")

    print(f"\nFiles to keep: {len(keep)}")
    for f in keep:
        print(f"  - {f}")

if __name__ == '__main__':
    test_metadata_detection()
