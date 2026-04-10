#!/usr/bin/env python3
"""Test WSL executable path conversion."""

import os
from pathlib import Path

# Test path
test_path = Path("/mnt/c/ai_projects/PeelX/archives/Minimal.Audio.Current.v2.0.1.Incl.Keygen.READ.NFO-R2R/Setup Current v2.0.1.exe")

print("Test WSL Path Conversion")
print("="*60)
print(f"Linux path: {test_path}")
print(f"Exists: {test_path.exists()}")
print()

# Check WSL
is_wsl = os.path.exists('/proc/version') and 'microsoft' in open('/proc/version').read().lower()
print(f"Is WSL: {is_wsl}")
print()

# Convert path
win_path = str(test_path)
if win_path.startswith('/mnt/'):
    drive = win_path[5].upper()
    win_path = f"{drive}:{win_path[6:]}".replace('/', '\\')

win_cwd = str(test_path.parent)
if win_cwd.startswith('/mnt/'):
    drive = win_cwd[5].upper()
    win_cwd = f"{drive}:{win_cwd[6:]}".replace('/', '\\')

print(f"Windows path: {win_path}")
print(f"Windows CWD: {win_cwd}")
print()

# Test command that would be run
cmd = f'cd /d "{win_cwd}" && "{win_path}"'
print("Command that would be executed:")
print(f'cmd.exe /c {cmd}')
print()

# Just test if cmd.exe is accessible
print("Testing cmd.exe availability:")
import subprocess
try:
    result = subprocess.run(['cmd.exe', '/c', 'echo', 'WSL works!'],
                          capture_output=True, text=True, timeout=5)
    print(f"✓ cmd.exe is accessible: {result.stdout.strip()}")
except Exception as e:
    print(f"✗ Error: {e}")
