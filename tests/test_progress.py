#!/usr/bin/env python3
"""
Test script to demonstrate progress indicators.
Shows the difference between normal mode and debug mode.
"""

import time
import sys

def simulate_extraction(debug=False):
    """Simulate extraction with progress indicator."""
    print("\n" + "="*60)
    print("Simulating Extraction")
    print("="*60 + "\n")

    files = [
        "game.zip",
        "setup.rar",
        "installer.7z",
        "data.tar.gz",
        "assets.zip"
    ]

    total = len(files)

    for idx, filename in enumerate(files, 1):
        progress = int((idx / total) * 100)

        if debug:
            print(f"  [{progress}%] Extracting: {filename}")
        else:
            print(f"\r  Extracting: {progress}%", end='', flush=True)

        time.sleep(0.5)  # Simulate work

    if not debug:
        print(f"\r  Extracting: 100% ✓")

    print()

def simulate_cleanup(debug=False):
    """Simulate cleanup with progress indicator."""
    print("="*60)
    print("Simulating Cleanup")
    print("="*60 + "\n")

    files = [
        "game.zip",
        "game.r00",
        "game.r01",
        "setup.rar",
        "setup.sfv",
        "installer.7z",
        "data.tar.gz",
        "assets.zip"
    ]

    total = len(files)

    for idx, filename in enumerate(files, 1):
        progress = int((idx / total) * 100)

        if debug:
            print(f"  [{progress}%] Deleted: {filename}")
        else:
            print(f"\r  Cleaning up: {progress}%", end='', flush=True)

        time.sleep(0.3)  # Simulate work

    if not debug:
        print(f"\r  Cleaning up: 100% ✓")

    print()

def main():
    print("\n" + "="*60)
    print("  Progress Indicator Demo")
    print("="*60)

    # Normal mode (default)
    print("\n📊 NORMAL MODE (clean output with percentages):")
    print("-"*60)
    simulate_extraction(debug=False)
    simulate_cleanup(debug=False)

    time.sleep(1)

    # Debug mode
    print("\n🐛 DEBUG MODE (detailed file names):")
    print("-"*60)
    simulate_extraction(debug=True)
    simulate_cleanup(debug=True)

    print("="*60)
    print("Demo Complete!")
    print("="*60)
    print("\nUsage:")
    print("  python peelx.py              # Normal mode (clean)")
    print("  python peelx.py --debug      # Debug mode (detailed)")
    print()

if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        print("\n\nInterrupted by user.")
        sys.exit(0)
