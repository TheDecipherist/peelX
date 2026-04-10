#!/usr/bin/env python3
"""Test split archive detection."""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

import pytest
from peelx import PeelX


@pytest.fixture
def extractor():
    return PeelX('archives', dry_run=True)


class TestSplitArchiveDetection:
    """Tests for _is_split_archive() method."""

    @pytest.mark.parametrize("filename,expected", [
        ("file.r00", True),
        ("file.r01", True),
        ("file.r99", True),
        ("archive.z01", True),
        ("archive.z02", True),
        ("data.001", True),
        ("data.002", True),
        ("data.099", True),
        ("package.7z.001", True),
        ("package.7z.002", True),
        ("main.rar", False),
        ("test.zip", False),
        ("document.txt", False),
        ("program.exe", False),
        ("file.r0", False),  # Too few digits
    ])
    def test_split_detection(self, extractor: PeelX, filename: str, expected: bool):
        assert extractor._is_split_archive(filename) == expected


class TestArchiveDetection:
    """Tests for _is_archive_or_metadata() and _is_extractable_archive()."""

    @pytest.mark.parametrize("filename,expected", [
        ("file.rar", True),
        ("file.zip", True),
        ("file.7z", True),
        ("file.tar", True),
        ("file.gz", True),
        ("file.r00", True),   # Split part
        ("file.r01", True),   # Split part
        ("file.sfv", True),   # Metadata
        ("checksums.md5", True),
        ("hashes.sha1", True),
        ("verify.sha256", True),
        ("recovery.par2", True),
        ("backup.crc", True),
        ("readme.txt", False),  # Keep
        ("info.nfo", False),    # Keep
        ("program.exe", False),
        ("image.jpg", False),
    ])
    def test_is_archive_or_metadata(self, extractor: PeelX, filename: str, expected: bool):
        assert extractor._is_archive_or_metadata(Path(filename)) == expected

    @pytest.mark.parametrize("filename,expected", [
        ("file.rar", True),
        ("file.zip", True),
        ("file.7z", True),
        ("file.r00", False),  # Split part — should NOT be extracted
        ("file.z01", False),  # Split part
        ("file.001", False),  # Split part
    ])
    def test_is_extractable_archive(self, extractor: PeelX, filename: str, expected: bool):
        assert extractor._is_extractable_archive(Path(filename)) == expected

    def test_backward_compat_is_archive(self, extractor: PeelX):
        """_is_archive() should delegate to _is_archive_or_metadata()."""
        test_file = Path("test.rar")
        assert extractor._is_archive(test_file) == extractor._is_archive_or_metadata(test_file)
