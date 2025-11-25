#!/usr/bin/env python3
"""
Creates example archives to demonstrate the archive_extractor.py functionality.
Run this script to set up a test environment.
"""

import os
import zipfile
from pathlib import Path


def create_example_structure():
    """Create example directory structure with nested archives."""

    base_dir = Path('archives')
    base_dir.mkdir(exist_ok=True)

    # Example 1: Simple game folder with a single zip
    game1_dir = base_dir / 'example_game1'
    game1_dir.mkdir(exist_ok=True)

    # Create a simple script
    script_content = '''#!/usr/bin/env python3
print("=" * 50)
print("Example Game 1 - Running!")
print("=" * 50)
print("This is a simple example executable.")
print("In a real scenario, this would be your game or application.")
input("Press Enter to exit...")
'''

    # Create files to zip
    temp_dir = game1_dir / 'temp_game1'
    temp_dir.mkdir(exist_ok=True)

    (temp_dir / 'game1.py').write_text(script_content)
    (temp_dir / 'README.txt').write_text('This is Example Game 1\nExtracted from a ZIP file!')

    # Create ZIP file
    zip_path = game1_dir / 'game1.zip'
    with zipfile.ZipFile(zip_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
        zipf.write(temp_dir / 'game1.py', 'game1.py')
        zipf.write(temp_dir / 'README.txt', 'README.txt')

    # Clean up temp directory
    import shutil
    shutil.rmtree(temp_dir)

    print(f"Created: {game1_dir}")

    # Example 2: Nested archive (zip within zip)
    game2_dir = base_dir / 'example_game2_nested'
    game2_dir.mkdir(exist_ok=True)

    # Create inner content
    temp_inner = game2_dir / 'temp_inner'
    temp_inner.mkdir(exist_ok=True)

    script2_content = '''#!/usr/bin/env python3
print("=" * 50)
print("Example Game 2 - Nested Archive Demo")
print("=" * 50)
print("This file was inside a nested archive!")
print("(A ZIP file that was inside another ZIP file)")
input("Press Enter to exit...")
'''

    (temp_inner / 'game2.py').write_text(script2_content)
    (temp_inner / 'data.txt').write_text('Important game data from nested archive')

    # Create inner ZIP
    inner_zip = game2_dir / 'temp_inner.zip'
    with zipfile.ZipFile(inner_zip, 'w', zipfile.ZIP_DEFLATED) as zipf:
        zipf.write(temp_inner / 'game2.py', 'game2.py')
        zipf.write(temp_inner / 'data.txt', 'data.txt')

    # Create outer ZIP containing the inner ZIP
    outer_zip = game2_dir / 'game2_package.zip'
    with zipfile.ZipFile(outer_zip, 'w', zipfile.ZIP_DEFLATED) as zipf:
        zipf.write(inner_zip, 'installer.zip')
        zipf.writestr('install_instructions.txt', 'Extract installer.zip to get the game files!')

    # Clean up temp files
    shutil.rmtree(temp_inner)
    inner_zip.unlink()

    print(f"Created: {game2_dir}")

    # Example 3: Folder with no archives (just an executable)
    tool_dir = base_dir / 'example_tool_no_archive'
    tool_dir.mkdir(exist_ok=True)

    tool_content = '''#!/usr/bin/env python3
print("=" * 50)
print("Example Tool - No Archive Version")
print("=" * 50)
print("This folder had no archives, so nothing was extracted.")
print("The tool was ready to run directly!")
input("Press Enter to exit...")
'''

    (tool_dir / 'tool.py').write_text(tool_content)
    (tool_dir / 'config.txt').write_text('Tool configuration file')

    print(f"Created: {tool_dir}")

    print("\n" + "=" * 60)
    print("Example structure created successfully!")
    print("=" * 60)
    print("\nYou can now run:")
    print("  python archive_extractor.py")
    print("\nThis will demonstrate:")
    print("  1. Extracting a simple ZIP file")
    print("  2. Extracting nested archives (ZIP in ZIP)")
    print("  3. Leaving folders without archives unchanged")
    print("\nAfter extraction, you can run the example Python scripts.")


if __name__ == '__main__':
    create_example_structure()
