#!/usr/bin/env python3
"""
Test the interactive selector with sample data.
"""

from pathlib import Path
from interactive_selector import select_executable_interactive
import tempfile
import os


def create_test_structure():
    """Create a temporary test structure with executables and NFO files."""
    # Create temp directory
    temp_dir = Path(tempfile.mkdtemp(prefix="archive_test_"))

    print(f"Creating test structure in: {temp_dir}\n")

    # Create folder structure
    game1_dir = temp_dir / "TestGame1"
    game1_dir.mkdir()

    # Create executable
    exe1 = game1_dir / "game.exe"
    exe1.write_text("Fake executable")

    # Create NFO file
    nfo1 = game1_dir / "readme.nfo"
    nfo_content = """
╔══════════════════════════════════════════════════════════╗
║                    TEST GAME v1.0                        ║
╠══════════════════════════════════════════════════════════╣
║                                                          ║
║  Release Date: 2025-01-25                                ║
║  Genre: Test / Demo                                      ║
║  Platform: Windows                                       ║
║                                                          ║
║  INSTALLATION:                                           ║
║  ============                                            ║
║  1. Extract all files                                    ║
║  2. Run game.exe                                         ║
║  3. Enjoy!                                               ║
║                                                          ║
║  SYSTEM REQUIREMENTS:                                    ║
║  ===================                                     ║
║  - OS: Windows 10 or higher                              ║
║  - RAM: 4GB minimum                                      ║
║  - Storage: 500MB                                        ║
║                                                          ║
║  NOTES:                                                  ║
║  ======                                                  ║
║  This is a test file for the interactive selector.      ║
║  Arrow keys: Navigate                                    ║
║  Enter: Select                                           ║
║  Q: Quit                                                 ║
║                                                          ║
╚══════════════════════════════════════════════════════════╝
"""
    nfo1.write_text(nfo_content)

    # Create second game
    game2_dir = temp_dir / "TestTool"
    game2_dir.mkdir()

    exe2 = game2_dir / "tool.exe"
    exe2.write_text("Fake tool")

    txt2 = game2_dir / "readme.txt"
    txt2.write_text("""TEST TOOL README
================

This is a simple test tool for demonstrating
the interactive selector with text file preview.

Features:
- Feature 1: Does something
- Feature 2: Does something else
- Feature 3: More features

Usage:
  tool.exe [options]

Options:
  --help     Show this help
  --version  Show version

For more information, visit:
https://example.com
""")

    # Create third game without NFO
    game3_dir = temp_dir / "NoNFOGame"
    game3_dir.mkdir()

    exe3 = game3_dir / "launcher.exe"
    exe3.write_text("Fake launcher")

    # Create nested executable
    subdir = game3_dir / "bin"
    subdir.mkdir()
    exe4 = subdir / "game_bin.exe"
    exe4.write_text("Nested executable")

    return temp_dir, [exe1, exe2, exe3, exe4]


def main():
    """Test the interactive selector."""
    print("="*60)
    print("  Interactive Selector Test")
    print("="*60)
    print()

    # Create test structure
    temp_dir, executables = create_test_structure()

    try:
        print("Created test executables:")
        for exe in executables:
            print(f"  - {exe.relative_to(temp_dir)}")

        print("\n" + "="*60)
        print("Launching Interactive Selector...")
        print("="*60)
        print()
        print("Instructions:")
        print("  ↑/↓  - Navigate up/down")
        print("  PgUp/PgDn - Jump 10 items")
        print("  Home/End - Jump to start/end")
        print("  Enter - Select executable")
        print("  Q or ESC - Quit")
        print()
        print("Press any key to continue...")
        input()

        # Run interactive selector
        selected = select_executable_interactive(executables, temp_dir)

        print("\n" + "="*60)
        print("Result:")
        print("="*60)

        if selected:
            print(f"\n✓ Selected: {selected.relative_to(temp_dir)}")
        else:
            print("\n  No selection (user quit)")

    finally:
        # Cleanup
        print("\n" + "="*60)
        print("Cleaning up test files...")
        print("="*60)
        import shutil
        shutil.rmtree(temp_dir)
        print(f"✓ Removed: {temp_dir}")

    print("\n" + "="*60)
    print("Test Complete!")
    print("="*60)


if __name__ == '__main__':
    main()
