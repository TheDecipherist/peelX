#!/usr/bin/env python3
"""Test NFO file detection with various naming patterns."""

from pathlib import Path
import tempfile
import shutil
from interactive_selector import InteractiveSelector


def test_nfo_detection():
    """Test that NFO files are found with various naming patterns."""
    print("Testing NFO file detection...\n")

    # Create temp directory
    temp_dir = Path(tempfile.mkdtemp(prefix="nfo_test_"))

    try:
        # Test Case 1: R2R.nfo pattern (release group naming)
        print("Test 1: Release group NFO (R2R.nfo)")
        print("-" * 60)
        test1_dir = temp_dir / "KORG.Modwave.Native"
        test1_dir.mkdir()

        exe1 = test1_dir / "Setup.exe"
        exe1.write_text("fake exe")

        nfo1 = test1_dir / "R2R.nfo"
        nfo1.write_text("Release by R2R\nThis is the NFO content")

        selector = InteractiveSelector([exe1], temp_dir)
        found = selector.find_info_file(exe1)

        if found:
            print(f"✓ Found: {found.name}")
            print(f"  Content preview: {found.read_text()[:50]}...")
        else:
            print("✗ NOT FOUND")
        print()

        # Test Case 2: Exact match (Setup.nfo)
        print("Test 2: Exact match (Setup.nfo)")
        print("-" * 60)
        test2_dir = temp_dir / "TestGame"
        test2_dir.mkdir()

        exe2 = test2_dir / "Setup.exe"
        exe2.write_text("fake exe")

        nfo2 = test2_dir / "Setup.nfo"
        nfo2.write_text("Setup instructions")

        selector = InteractiveSelector([exe2], temp_dir)
        found = selector.find_info_file(exe2)

        if found:
            print(f"✓ Found: {found.name}")
        else:
            print("✗ NOT FOUND")
        print()

        # Test Case 3: Common name (readme.txt)
        print("Test 3: Common name (readme.txt)")
        print("-" * 60)
        test3_dir = temp_dir / "TestTool"
        test3_dir.mkdir()

        exe3 = test3_dir / "tool.exe"
        exe3.write_text("fake exe")

        txt3 = test3_dir / "readme.txt"
        txt3.write_text("README content")

        selector = InteractiveSelector([exe3], temp_dir)
        found = selector.find_info_file(exe3)

        if found:
            print(f"✓ Found: {found.name}")
        else:
            print("✗ NOT FOUND")
        print()

        # Test Case 4: Multiple NFOs (should find first .nfo)
        print("Test 4: Multiple NFOs")
        print("-" * 60)
        test4_dir = temp_dir / "MultiNFO"
        test4_dir.mkdir()

        exe4 = test4_dir / "launcher.exe"
        exe4.write_text("fake exe")

        nfo4a = test4_dir / "release.nfo"
        nfo4a.write_text("Release NFO")

        nfo4b = test4_dir / "info.nfo"
        nfo4b.write_text("Info NFO")

        selector = InteractiveSelector([exe4], temp_dir)
        found = selector.find_info_file(exe4)

        if found:
            print(f"✓ Found: {found.name}")
            print(f"  (Note: Returns first .nfo found)")
        else:
            print("✗ NOT FOUND")
        print()

        # Test Case 5: No NFO
        print("Test 5: No NFO file")
        print("-" * 60)
        test5_dir = temp_dir / "NoNFO"
        test5_dir.mkdir()

        exe5 = test5_dir / "app.exe"
        exe5.write_text("fake exe")

        selector = InteractiveSelector([exe5], temp_dir)
        found = selector.find_info_file(exe5)

        if found:
            print(f"✗ Unexpected: {found.name}")
        else:
            print("✓ Correctly returned None (no NFO)")
        print()

        # Test Case 6: Case insensitive extension
        print("Test 6: Mixed case extension (.NFO)")
        print("-" * 60)
        test6_dir = temp_dir / "CaseSensitive"
        test6_dir.mkdir()

        exe6 = test6_dir / "game.exe"
        exe6.write_text("fake exe")

        nfo6 = test6_dir / "Release.NFO"
        nfo6.write_text("UPPERCASE NFO")

        selector = InteractiveSelector([exe6], temp_dir)
        found = selector.find_info_file(exe6)

        if found:
            print(f"✓ Found: {found.name}")
        else:
            print("✗ NOT FOUND (case sensitivity issue)")
        print()

        print("=" * 60)
        print("Summary: NFO detection should now find R2R.nfo files!")
        print("=" * 60)

    finally:
        # Cleanup
        shutil.rmtree(temp_dir)
        print(f"\nCleaned up: {temp_dir}")


if __name__ == '__main__':
    test_nfo_detection()
