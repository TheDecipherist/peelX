#!/usr/bin/env python3
"""Test NFO file detection with various naming patterns."""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

import pytest
import tempfile
import shutil
from interactive_selector import InteractiveSelector


@pytest.fixture
def temp_dir():
    d = Path(tempfile.mkdtemp(prefix="nfo_test_"))
    yield d
    shutil.rmtree(d)


def _make_exe(directory: Path, name: str = "setup.exe") -> Path:
    exe = directory / name
    exe.write_text("fake exe")
    return exe


class TestNfoDetection:
    """Tests for InteractiveSelector.find_info_file()."""

    def test_release_group_nfo(self, temp_dir: Path):
        """Should find R2R.nfo (release group naming pattern)."""
        test_dir = temp_dir / "release"
        test_dir.mkdir()
        exe = _make_exe(test_dir)
        (test_dir / "R2R.nfo").write_text("Release by R2R")

        selector = InteractiveSelector([exe], temp_dir)
        found = selector.find_info_file(exe)
        assert found is not None
        assert found.name == "R2R.nfo"

    def test_exact_name_match(self, temp_dir: Path):
        """Should find NFO matching executable name (setup.nfo for setup.exe)."""
        test_dir = temp_dir / "exact"
        test_dir.mkdir()
        exe = _make_exe(test_dir, "Setup.exe")
        (test_dir / "Setup.nfo").write_text("Setup instructions")

        selector = InteractiveSelector([exe], temp_dir)
        found = selector.find_info_file(exe)
        assert found is not None
        assert found.name == "Setup.nfo"

    def test_common_readme_name(self, temp_dir: Path):
        """Should find readme.txt as info file."""
        test_dir = temp_dir / "readme"
        test_dir.mkdir()
        exe = _make_exe(test_dir, "tool.exe")
        (test_dir / "readme.txt").write_text("README content")

        selector = InteractiveSelector([exe], temp_dir)
        found = selector.find_info_file(exe)
        assert found is not None
        assert found.name == "readme.txt"

    def test_no_nfo_returns_none(self, temp_dir: Path):
        """Should return None when no info file exists."""
        test_dir = temp_dir / "empty"
        test_dir.mkdir()
        exe = _make_exe(test_dir, "app.exe")

        selector = InteractiveSelector([exe], temp_dir)
        found = selector.find_info_file(exe)
        assert found is None

    def test_case_insensitive_extension(self, temp_dir: Path):
        """Should find .NFO files (uppercase extension)."""
        test_dir = temp_dir / "case"
        test_dir.mkdir()
        exe = _make_exe(test_dir, "game.exe")
        (test_dir / "Release.NFO").write_text("UPPERCASE NFO")

        selector = InteractiveSelector([exe], temp_dir)
        found = selector.find_info_file(exe)
        assert found is not None
        assert found.suffix.lower() == ".nfo"

    def test_parent_directory_search(self, temp_dir: Path):
        """Should find info file in parent directory when not in same dir."""
        parent_dir = temp_dir / "parent"
        parent_dir.mkdir()
        sub_dir = parent_dir / "bin"
        sub_dir.mkdir()
        exe = _make_exe(sub_dir, "game.exe")
        (parent_dir / "readme.nfo").write_text("Parent NFO")

        selector = InteractiveSelector([exe], temp_dir)
        found = selector.find_info_file(exe)
        assert found is not None
        assert found.name == "readme.nfo"

    def test_diz_extension(self, temp_dir: Path):
        """Should find .diz files."""
        test_dir = temp_dir / "diz"
        test_dir.mkdir()
        exe = _make_exe(test_dir, "app.exe")
        (test_dir / "file_id.diz").write_text("DIZ content")

        selector = InteractiveSelector([exe], temp_dir)
        found = selector.find_info_file(exe)
        assert found is not None
        assert found.suffix == ".diz"


class TestReadInfoFile:
    """Tests for InteractiveSelector.read_info_file()."""

    def test_utf8_content(self, temp_dir: Path):
        info_file = temp_dir / "test.nfo"
        info_file.write_text("Hello World\nLine 2\nLine 3", encoding='utf-8')

        selector = InteractiveSelector([], temp_dir)
        lines = selector.read_info_file(info_file)
        assert lines == ["Hello World", "Line 2", "Line 3"]

    def test_max_lines_truncation(self, temp_dir: Path):
        info_file = temp_dir / "long.nfo"
        info_file.write_text("\n".join(f"Line {i}" for i in range(200)), encoding='utf-8')

        selector = InteractiveSelector([], temp_dir)
        lines = selector.read_info_file(info_file, max_lines=10)
        assert len(lines) == 11  # 10 lines + truncation message
        assert "truncated" in lines[-1]

    def test_tab_expansion(self, temp_dir: Path):
        info_file = temp_dir / "tabs.nfo"
        info_file.write_text("col1\tcol2\tcol3", encoding='utf-8')

        selector = InteractiveSelector([], temp_dir)
        lines = selector.read_info_file(info_file)
        assert "\t" not in lines[0]  # Tabs should be expanded
