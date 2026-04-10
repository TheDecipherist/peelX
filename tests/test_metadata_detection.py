#!/usr/bin/env python3
"""Test metadata file detection."""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

import pytest
from peelx import PeelX


@pytest.fixture
def extractor():
    return PeelX('archives', dry_run=True)


class TestMetadataDetection:
    """Tests for archive metadata file detection."""

    @pytest.mark.parametrize("filename", [
        "file.sfv",
        "checksums.md5",
        "hashes.sha1",
        "verify.sha256",
        "recovery.par2",
        "backup.par",
        "backup.crc",
    ])
    def test_metadata_files_detected(self, extractor: PeelX, filename: str):
        assert extractor._is_archive_or_metadata(Path(filename)) is True

    @pytest.mark.parametrize("filename", [
        "readme.txt",
        "info.nfo",
        "program.exe",
        "image.jpg",
        "document.pdf",
    ])
    def test_non_metadata_files_not_detected(self, extractor: PeelX, filename: str):
        assert extractor._is_archive_or_metadata(Path(filename)) is False

    def test_metadata_extensions_constant(self, extractor: PeelX):
        """ARCHIVE_METADATA_EXTENSIONS should include all checksum/parity types."""
        expected = {'.sfv', '.md5', '.sha1', '.sha256', '.crc', '.par2', '.par'}
        assert extractor.ARCHIVE_METADATA_EXTENSIONS == expected
