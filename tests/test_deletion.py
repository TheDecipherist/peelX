#!/usr/bin/env python3
"""Test archive deletion and cleanup logic."""

import sys
import os
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

import pytest
import tempfile
import shutil
from peelx import PeelX


@pytest.fixture
def temp_dir():
    d = Path(tempfile.mkdtemp(prefix="deletion_test_"))
    yield d
    shutil.rmtree(d)


@pytest.fixture
def extractor(temp_dir: Path) -> PeelX:
    return PeelX(str(temp_dir), dry_run=True)


def _create_test_files(directory: Path) -> dict:
    """Create a mix of archive and non-archive files."""
    files = {
        'archives': ['game.rar', 'data.zip', 'pkg.7z'],
        'splits': ['game.r00', 'game.r01', 'game.r02'],
        'metadata': ['game.sfv', 'checksums.md5', 'recover.par2'],
        'keep': ['setup.exe', 'readme.nfo', 'info.txt', 'image.jpg'],
    }
    for group in files.values():
        for name in group:
            (directory / name).write_text("test")
    return files


class TestDeletionDetection:
    """Tests for determining which files should be deleted."""

    def test_archives_detected_for_deletion(self, temp_dir: Path, extractor: PeelX):
        files = _create_test_files(temp_dir)
        for name in files['archives']:
            assert extractor._is_archive(temp_dir / name), f"{name} should be detected as archive"

    def test_splits_detected_for_deletion(self, temp_dir: Path, extractor: PeelX):
        files = _create_test_files(temp_dir)
        for name in files['splits']:
            assert extractor._is_archive(temp_dir / name), f"{name} should be detected for deletion"

    def test_metadata_detected_for_deletion(self, temp_dir: Path, extractor: PeelX):
        files = _create_test_files(temp_dir)
        for name in files['metadata']:
            assert extractor._is_archive(temp_dir / name), f"{name} should be detected for deletion"

    def test_non_archives_preserved(self, temp_dir: Path, extractor: PeelX):
        files = _create_test_files(temp_dir)
        for name in files['keep']:
            assert not extractor._is_archive(temp_dir / name), f"{name} should NOT be detected for deletion"


class TestDeleteArchives:
    """Tests for the delete_archives() method."""

    def test_dry_run_counts_without_deleting(self, temp_dir: Path):
        _create_test_files(temp_dir)
        extractor = PeelX(str(temp_dir.parent), dry_run=True)
        count = extractor.delete_archives(temp_dir)
        assert count == 9  # 3 archives + 3 splits + 3 metadata
        # Verify files still exist
        assert (temp_dir / "game.rar").exists()

    def test_actual_deletion_removes_archives(self, temp_dir: Path):
        _create_test_files(temp_dir)
        extractor = PeelX(str(temp_dir.parent), dry_run=False)
        count = extractor.delete_archives(temp_dir)
        assert count == 9
        # Archives should be gone
        assert not (temp_dir / "game.rar").exists()
        assert not (temp_dir / "game.r00").exists()
        assert not (temp_dir / "game.sfv").exists()
        # Keep files should remain
        assert (temp_dir / "setup.exe").exists()
        assert (temp_dir / "readme.nfo").exists()

    def test_empty_directory_returns_zero(self, temp_dir: Path):
        extractor = PeelX(str(temp_dir.parent), dry_run=False)
        assert extractor.delete_archives(temp_dir) == 0
