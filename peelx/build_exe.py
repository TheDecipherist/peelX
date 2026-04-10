#!/usr/bin/env python3
"""
Build script to create a Windows executable of PeelX using PyInstaller.

Usage:
    python build_exe.py

Requires: pip install -r requirements.txt
Must be run on Windows (PyInstaller builds for the current platform).
"""

import os
import subprocess
import sys


def ensure_deps() -> None:
    """Install build dependencies if missing."""
    deps = ["pyinstaller", "rarfile", "py7zr"]
    if sys.platform == "win32":
        deps.append("windows-curses")

    for dep in deps:
        module = dep.replace("-", "_")
        try:
            __import__(module)
        except ImportError:
            print(f"Installing {dep}...")
            subprocess.check_call([sys.executable, "-m", "pip", "install", dep])


def main() -> int:
    """Build Windows executable with PyInstaller."""
    ensure_deps()

    # Verify curses works before building
    try:
        import curses  # noqa: F401
        print("curses module: OK")
    except ImportError:
        print("WARNING: curses module not available - interactive mode will be disabled in the build")

    # Remove stale spec file so PyInstaller uses our command-line args
    spec_file = "peelx.spec"
    if os.path.exists(spec_file):
        os.remove(spec_file)
        print(f"Removed old {spec_file}")

    cmd = [
        sys.executable, "-m", "PyInstaller",
        "--onefile",
        "--name", "peelx",
        # Force collection of peelx submodules that PyInstaller may miss
        "--hidden-import", "peelx.interactive_selector",
        "--hidden-import", "peelx.core",
        "--hidden-import", "peelx.auto",
        "--hidden-import", "rarfile",
        "--hidden-import", "py7zr",
        "--hidden-import", "curses",
        "--hidden-import", "_curses",
        "--console",
        "--clean",
        "run_peelx.py",
    ]

    print(f"\nRunning: {' '.join(cmd)}\n")
    result = subprocess.run(cmd)

    if result.returncode == 0:
        exe_name = "peelx.exe" if sys.platform == "win32" else "peelx"
        exe_path = os.path.join("dist", exe_name)
        print(f"\nBuild successful!")
        print(f"Executable: {exe_path}")
    else:
        print("\nBuild failed.", file=sys.stderr)

    return result.returncode


if __name__ == "__main__":
    sys.exit(main())
