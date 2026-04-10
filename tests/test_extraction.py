#!/usr/bin/env python3
"""Test archive extraction logic."""

import sys
import os
import zipfile
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

import pytest
import tempfile
import shutil
from peelx import PeelX


@pytest.fixture
def temp_base():
    d = Path(tempfile.mkdtemp(prefix="extract_test_"))
    yield d
    shutil.rmtree(d)


def _create_test_zip(directory: Path, name: str = "test.zip", contents: dict = None) -> Path:
    """Create a test zip archive with given contents."""
    if contents is None:
        contents = {"hello.txt": "Hello World", "data/nested.txt": "Nested content"}
    zip_path = directory / name
    with zipfile.ZipFile(zip_path, 'w') as zf:
        for fname, content in contents.items():
            zf.writestr(fname, content)
    return zip_path


class TestExtractArchive:
    """Tests for PeelX.extract_archive()."""

    def test_extract_zip(self, temp_base: Path):
        folder = temp_base / "game"
        folder.mkdir()
        zip_path = _create_test_zip(folder)

        extractor = PeelX(str(temp_base))
        result = extractor.extract_archive(zip_path, folder)

        assert result is True
        assert (folder / "hello.txt").exists()
        assert (folder / "hello.txt").read_text() == "Hello World"
        assert (folder / "data" / "nested.txt").exists()

    def test_extract_unsupported_format(self, temp_base: Path):
        folder = temp_base / "game"
        folder.mkdir()
        fake = folder / "test.xyz"
        fake.write_text("not an archive")

        extractor = PeelX(str(temp_base))
        result = extractor.extract_archive(fake, folder)
        assert result is False

    def test_zip_slip_prevention(self, temp_base: Path):
        """Zip with path traversal entries should be rejected."""
        folder = temp_base / "game"
        folder.mkdir()
        zip_path = folder / "malicious.zip"
        with zipfile.ZipFile(zip_path, 'w') as zf:
            zf.writestr("../../../etc/evil.txt", "malicious content")

        extractor = PeelX(str(temp_base))
        result = extractor.extract_archive(zip_path, folder)
        assert result is False
        assert not (temp_base / "etc" / "evil.txt").exists()


class TestRecursiveExtraction:
    """Tests for extract_all_archives_recursive()."""

    def test_extracts_single_zip(self, temp_base: Path):
        folder = temp_base / "game"
        folder.mkdir()
        _create_test_zip(folder, contents={"readme.txt": "Hello"})

        extractor = PeelX(str(temp_base))
        extractor.extract_all_archives_recursive(folder)

        assert (folder / "readme.txt").exists()

    def test_nested_zip_extraction(self, temp_base: Path):
        """Should extract archives found inside extracted archives."""
        folder = temp_base / "game"
        folder.mkdir()

        # Create inner zip
        inner_zip = temp_base / "inner.zip"
        with zipfile.ZipFile(inner_zip, 'w') as zf:
            zf.writestr("deep.txt", "Deep content")

        # Create outer zip containing the inner zip
        outer_zip = folder / "outer.zip"
        with zipfile.ZipFile(outer_zip, 'w') as zf:
            zf.write(inner_zip, "inner.zip")

        inner_zip.unlink()  # Clean up temp inner zip

        extractor = PeelX(str(temp_base))
        extractor.extract_all_archives_recursive(folder)

        assert (folder / "deep.txt").exists()

    def test_dry_run_does_not_extract(self, temp_base: Path):
        folder = temp_base / "game"
        folder.mkdir()
        _create_test_zip(folder, contents={"data.txt": "test"})

        extractor = PeelX(str(temp_base), dry_run=True)
        extractor.extract_all_archives_recursive(folder)

        assert not (folder / "data.txt").exists()

    def test_processed_set_prevents_reextraction(self, temp_base: Path):
        folder = temp_base / "game"
        folder.mkdir()
        zip_path = _create_test_zip(folder)

        extractor = PeelX(str(temp_base))
        processed = {str(zip_path)}  # Pre-mark as processed
        extractor.extract_all_archives_recursive(folder, processed=processed)

        # File should NOT be extracted since it's in the processed set
        assert not (folder / "hello.txt").exists()
