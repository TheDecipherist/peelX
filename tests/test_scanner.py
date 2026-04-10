#!/usr/bin/env python3
"""Test directory scanning and executable detection."""

import sys
import os
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

import pytest
import tempfile
import shutil
from peelx import PeelX


@pytest.fixture
def temp_base():
    d = Path(tempfile.mkdtemp(prefix="scanner_test_"))
    yield d
    shutil.rmtree(d)


class TestScanDirectories:
    """Tests for PeelX.scan_directories()."""

    def test_empty_directory_returns_empty(self, temp_base: Path):
        extractor = PeelX(str(temp_base))
        assert extractor.scan_directories() == []

    def test_creates_base_dir_if_missing(self, temp_base: Path):
        target = temp_base / "nonexistent"
        extractor = PeelX(str(target))
        result = extractor.scan_directories()
        assert result == []
        assert target.exists()

    def test_detects_folders_with_archives(self, temp_base: Path):
        folder = temp_base / "has_archives"
        folder.mkdir()
        (folder / "test.rar").write_text("fake")

        extractor = PeelX(str(temp_base))
        folders = extractor.scan_directories()
        assert len(folders) == 1
        assert folders[0] == (folder, True)

    def test_detects_folders_without_archives(self, temp_base: Path):
        folder = temp_base / "no_archives"
        folder.mkdir()
        (folder / "readme.txt").write_text("hello")

        extractor = PeelX(str(temp_base))
        folders = extractor.scan_directories()
        assert len(folders) == 1
        assert folders[0] == (folder, False)

    def test_skips_files_in_base_dir(self, temp_base: Path):
        """Files directly in base_dir should not appear as folders."""
        (temp_base / "stray_file.txt").write_text("test")
        extractor = PeelX(str(temp_base))
        assert extractor.scan_directories() == []

    def test_detects_split_archives(self, temp_base: Path):
        folder = temp_base / "splits"
        folder.mkdir()
        (folder / "game.rar").write_text("fake")
        (folder / "game.r00").write_text("fake")
        (folder / "game.r01").write_text("fake")

        extractor = PeelX(str(temp_base))
        folders = extractor.scan_directories()
        assert folders[0][1] is True


class TestFindExecutables:
    """Tests for PeelX.find_executables()."""

    def test_finds_exe_files(self, temp_base: Path):
        """On Linux, files need execute permission to be found."""
        folder = temp_base / "game"
        folder.mkdir()
        exe_file = folder / "setup.sh"
        exe_file.write_text("#!/bin/sh\necho hello")
        os.chmod(exe_file, 0o755)

        extractor = PeelX(str(temp_base))
        exes = extractor.find_executables(folder)
        assert len(exes) == 1
        assert exes[0].name == "setup.sh"

    def test_excludes_nfo_files(self, temp_base: Path):
        folder = temp_base / "game"
        folder.mkdir()
        (folder / "readme.nfo").write_text("info")
        exe_file = folder / "setup.sh"
        exe_file.write_text("#!/bin/sh")
        os.chmod(exe_file, 0o755)

        extractor = PeelX(str(temp_base))
        exes = extractor.find_executables(folder)
        assert all(e.suffix != ".nfo" for e in exes)

    def test_excludes_archive_files(self, temp_base: Path):
        folder = temp_base / "game"
        folder.mkdir()
        (folder / "data.rar").write_text("fake")
        exe_file = folder / "setup.sh"
        exe_file.write_text("#!/bin/sh")
        os.chmod(exe_file, 0o755)

        extractor = PeelX(str(temp_base))
        exes = extractor.find_executables(folder)
        assert all(e.suffix != ".rar" for e in exes)

    def test_finds_nested_executables(self, temp_base: Path):
        folder = temp_base / "game"
        subfolder = folder / "bin"
        subfolder.mkdir(parents=True)
        exe_file = subfolder / "game.sh"
        exe_file.write_text("#!/bin/sh")
        os.chmod(exe_file, 0o755)

        extractor = PeelX(str(temp_base))
        exes = extractor.find_executables(folder)
        assert len(exes) == 1
        assert exes[0].name == "game.sh"

    def test_empty_directory_returns_empty(self, temp_base: Path):
        folder = temp_base / "empty"
        folder.mkdir()

        extractor = PeelX(str(temp_base))
        assert extractor.find_executables(folder) == []
