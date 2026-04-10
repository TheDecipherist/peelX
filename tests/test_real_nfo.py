#!/usr/bin/env python3
"""Test NFO detection with real file structure similar to R2R releases."""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

import pytest
import tempfile
import shutil
from interactive_selector import InteractiveSelector


@pytest.fixture
def r2r_release():
    """Create a structure similar to R2R releases."""
    temp_dir = Path(tempfile.mkdtemp(prefix="r2r_test_"))
    release_dir = temp_dir / "KORG.Modwave.Native.v1.1.2-R2R"
    release_dir.mkdir()

    (release_dir / "R2R.nfo").write_text(
        "╔═══════════════════════════╗\n"
        "║   R2R RELEASE             ║\n"
        "╚═══════════════════════════╝\n"
    )
    (release_dir / "Setup modwave native v1.1.2.exe").write_text("Fake installer")
    (release_dir / "r2r.sfv").write_text("checksum file")

    yield temp_dir, release_dir
    shutil.rmtree(temp_dir)


class TestR2RDetection:
    """Tests for R2R-style release structure."""

    def test_r2r_nfo_found(self, r2r_release):
        temp_dir, release_dir = r2r_release
        exe = release_dir / "Setup modwave native v1.1.2.exe"
        selector = InteractiveSelector([exe], temp_dir)

        found = selector.find_info_file(exe)
        assert found is not None
        assert found.name == "R2R.nfo"

    def test_r2r_nfo_content_readable(self, r2r_release):
        temp_dir, release_dir = r2r_release
        exe = release_dir / "Setup modwave native v1.1.2.exe"
        selector = InteractiveSelector([exe], temp_dir)

        found = selector.find_info_file(exe)
        content = selector.read_info_file(found)
        assert len(content) > 0
        assert any("R2R" in line for line in content)
