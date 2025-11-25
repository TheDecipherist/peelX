#!/usr/bin/env python3
"""Test NFO detection with real file structure similar to R2R releases."""

from pathlib import Path
import tempfile
import shutil
from interactive_selector import InteractiveSelector


def create_r2r_structure():
    """Create a structure similar to R2R releases."""
    temp_dir = Path(tempfile.mkdtemp(prefix="r2r_test_"))

    # Simulate R2R release structure
    release_dir = temp_dir / "KORG.Modwave.Native.v1.1.2-R2R"
    release_dir.mkdir()

    # Create files typical of R2R releases
    (release_dir / "R2R.nfo").write_text("""
    ╔═══════════════════════════════════════════════════════╗
    ║                   R2R  RELEASE                        ║
    ╠═══════════════════════════════════════════════════════╣
    ║                                                       ║
    ║  KORG Modwave Native v1.1.2                           ║
    ║                                                       ║
    ║  Release Date: 2024-01-26                             ║
    ║  Format: VSTi / AAX                                   ║
    ║                                                       ║
    ║  INSTALLATION:                                        ║
    ║  ═══════════════                                      ║
    ║  1. Run Setup.exe                                     ║
    ║  2. Follow installation wizard                        ║
    ║  3. Use provided keygen if needed                     ║
    ║                                                       ║
    ║  SYSTEM REQUIREMENTS:                                 ║
    ║  ═══════════════════                                  ║
    ║  - Windows 10 or higher                               ║
    ║  - VST3 compatible DAW                                ║
    ║  - 8GB RAM minimum                                    ║
    ║                                                       ║
    ╚═══════════════════════════════════════════════════════╝
    """)

    # Create executable
    (release_dir / "Setup modwave native v1.1.2.exe").write_text("Fake installer")

    # Create other typical R2R files
    (release_dir / "r2r.sfv").write_text("checksum file")

    return temp_dir, release_dir


def test_r2r_detection():
    """Test with R2R-style structure."""
    print("="*60)
    print("Testing R2R Release Structure")
    print("="*60)
    print()

    temp_dir, release_dir = create_r2r_structure()

    try:
        print("Created structure:")
        print(f"  {release_dir.name}/")
        for item in sorted(release_dir.iterdir()):
            print(f"    - {item.name}")
        print()

        # Find executables
        executables = []
        for item in release_dir.iterdir():
            if item.suffix.lower() == '.exe':
                executables.append(item)

        print(f"Found {len(executables)} executable(s):")
        for exe in executables:
            print(f"  - {exe.name}")
        print()

        # Test NFO detection
        if executables:
            exe = executables[0]
            print(f"Testing NFO detection for: {exe.name}")
            print("-" * 60)

            selector = InteractiveSelector(executables, temp_dir)
            found_nfo = selector.find_info_file(exe)

            if found_nfo:
                print(f"✓ SUCCESS: Found {found_nfo.name}")
                print()
                print("NFO Content Preview:")
                print("-" * 60)
                content = selector.read_info_file(found_nfo, max_lines=20)
                for line in content[:15]:
                    print(line)
                print("-" * 60)
            else:
                print("✗ FAILED: No NFO found")
                print("This should not happen!")

        print()
        print("="*60)
        print("Test Result:")
        print("="*60)
        if found_nfo:
            print("✓ R2R.nfo detection working correctly!")
            print(f"  Found: {found_nfo.name}")
            print(f"  For executable: {exe.name}")
        else:
            print("✗ Failed to detect R2R.nfo")

    finally:
        shutil.rmtree(temp_dir)
        print(f"\nCleaned up: {temp_dir}")


if __name__ == '__main__':
    test_r2r_detection()
