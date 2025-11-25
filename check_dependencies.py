#!/usr/bin/env python3
"""
Check if required dependencies are installed for archive extraction.
"""

import subprocess
import sys
from pathlib import Path


def check_command(command):
    """Check if a command is available."""
    try:
        subprocess.run([command, '--version'], capture_output=True, check=True)
        return True
    except (FileNotFoundError, subprocess.CalledProcessError):
        try:
            subprocess.run([command, '-h'], capture_output=True, check=True)
            return True
        except (FileNotFoundError, subprocess.CalledProcessError):
            return False


def check_python_library(library_name):
    """Check if a Python library is installed."""
    try:
        __import__(library_name)
        return True
    except ImportError:
        return False


def main():
    """Check all dependencies."""
    print("="*60)
    print("  Archive Extractor - Dependency Check")
    print("="*60 + "\n")

    # Check Python version
    print(f"Python version: {sys.version.split()[0]}")

    # Check system commands
    print("\nSystem Commands:")
    print("-" * 60)

    commands = {
        'unrar': 'Extract RAR and split RAR archives',
        '7z': 'Extract 7Z files with advanced compression',
        '7za': 'Alternative 7z command (p7zip-full)',
    }

    critical_missing = []
    for cmd, description in commands.items():
        status = "✓" if check_command(cmd) else "✗"
        installed = check_command(cmd)
        print(f"  [{status}] {cmd:10s} - {description}")
        if not installed and cmd in ['unrar', '7z', '7za']:
            if cmd == '7za':
                if not check_command('7z'):
                    critical_missing.append(cmd)
            else:
                critical_missing.append(cmd)

    # Check Python libraries
    print("\nPython Libraries (Optional):")
    print("-" * 60)

    libraries = {
        'rarfile': 'RAR extraction (requires unrar command)',
        'py7zr': '7Z extraction (limited compression support)',
    }

    for lib, description in libraries.items():
        status = "✓" if check_python_library(lib) else "○"
        print(f"  [{status}] {lib:10s} - {description}")

    # Built-in support
    print("\nBuilt-in Support (Python Standard Library):")
    print("-" * 60)
    print("  [✓] zipfile   - ZIP archives")
    print("  [✓] tarfile   - TAR, TAR.GZ, TAR.BZ2, TAR.XZ archives")
    print("  [✓] gzip      - GZ files")
    print("  [✓] bz2       - BZ2 files")

    # Summary
    print("\n" + "="*60)
    print("Summary:")
    print("="*60)

    if not critical_missing:
        print("\n✓ All critical dependencies are installed!")
        print("  You can extract all supported archive formats.")
    else:
        print("\n⚠ Missing critical dependencies:")
        for cmd in critical_missing:
            if cmd == 'unrar':
                print(f"\n  Install {cmd} to extract RAR files:")
                print("    Ubuntu/Debian: sudo apt-get install unrar")
                print("    macOS:         brew install unrar")
                print("    Windows:       choco install unrar")
            elif cmd in ['7z', '7za']:
                print(f"\n  Install 7z to extract 7Z files:")
                print("    Ubuntu/Debian: sudo apt-get install p7zip-full")
                print("    macOS:         brew install p7zip")
                print("    Windows:       choco install 7zip")

    print("\n" + "="*60)
    print("For detailed installation instructions, see INSTALL.md")
    print("="*60 + "\n")


if __name__ == '__main__':
    main()
