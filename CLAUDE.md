# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

PeelX is a Python utility that scans directories, recursively extracts nested archives, and provides an interactive interface to run executables. It's designed for handling software releases that come packaged in nested archive formats (common in scene releases).

## Running and Testing

### Basic Usage
```bash
# Interactive mode (default) - extracts archives and shows interactive selector
python peelx.py

# Auto mode - processes all folders without prompts
python peelx_auto.py

# Preview mode (recommended for testing changes)
python peelx.py --dry-run

# Debug mode with detailed output
python peelx.py --debug

# Disable interactive selector (use simple text menu)
python peelx.py --no-interactive
```

### Testing
```bash
# Run individual test files
python test_scanner.py          # Test directory scanning
python test_split_detection.py  # Test split archive detection
python test_deletion.py         # Test file cleanup logic
python test_interactive.py      # Test interactive selector UI
python test_nfo_detection.py    # Test NFO file detection
python test_wsl_exec.py         # Test WSL executable handling

# Create example archive structure for testing
python create_example.py
```

## Architecture

### Core Class: PeelX (peelx.py)

The `PeelX` class is the heart of the application:

- **Scanning**: `scan_directories()` finds folders containing archives
- **Archive Detection**:
  - `_is_archive_or_metadata()` - identifies archives and related files to delete
  - `_is_extractable_archive()` - identifies archives to extract (excludes split parts like .r00, .r01)
  - `_is_split_archive()` - detects split archive parts (.r00, .z01, .001, etc.)
- **Extraction**: `extract_all_archives_recursive()` handles nested archives up to 50 levels deep
- **Cleanup**: `delete_archives()` removes archives, split parts, checksums (.sfv, .md5), and parity files (.par2)
- **Executable Management**: `find_executables()` and `run_executable()` with cross-platform support

### Interactive Selector (interactive_selector.py)

The `InteractiveSelector` class provides a dual-mode curses-based UI:

- **Two Display Modes**:
  - Split-screen: List of executables + preview panel
  - Full-screen: Expanded preview mode (press → to enter, ← to exit)
- **ExecutionTracker**: Tracks which executables have been run (stored in executions.log as JSON)
- **NFO Preview**: Automatically finds and displays .nfo, .txt, .diz, .readme files
- **File Detection Priority**:
  1. Exact match with executable name
  2. Common readme names in same directory
  3. ANY .nfo/.txt file in same directory (catches R2R.nfo, release.nfo, etc.)
  4. Search parent directory with same logic
- **Encoding Support**: Tries UTF-8, Latin-1, CP437, CP1252, ISO-8859-1 in order

### Entry Points

- `peelx.py` - Main interactive workflow with user prompts
- `peelx_auto.py` - Automatic processing without prompts (imports PeelX class)

### Platform-Specific Handling

**WSL Detection** (peelx.py:438-467):
- Detects WSL by checking `/proc/version` for 'microsoft'
- Converts Linux paths (`/mnt/c/`) to Windows paths (`C:\`)
- Runs Windows executables using `cmd.exe /c` from WSL

## Important Implementation Details

### Archive Processing Logic

1. **Extraction**: Only extracts main archive files, NOT split parts (.r00, .r01). The main archive (.rar) handles split parts automatically.
2. **Cleanup**: After extraction, deletes ALL archive-related files:
   - Archive files (.zip, .rar, .7z, etc.)
   - Split parts (.r00, .r01, .z01, .001, etc.)
   - Checksums (.sfv, .md5, .sha1, .sha256, .crc)
   - Parity files (.par, .par2)
3. **Preservation**: Keeps .nfo, .txt, .diz files and all extracted content

### Progress Display

- By default: Shows clean progress indicators (1-100%)
- With `--debug`: Shows detailed file names during operations
- Uses `\r` carriage return for updating progress in place

### Nested Archive Handling

`extract_all_archives_recursive()` uses an iterative approach with `processed` set to track extracted archives and prevent re-extraction. Maximum 50 iterations to prevent infinite loops.

## Development Guidelines

### Adding New Archive Format Support

1. Add extension to `ARCHIVE_EXTENSIONS` set (line 22)
2. Add extraction logic in `extract_archive()` method (line 155)
3. Consider whether it's a main archive or split part in `_is_extractable_archive()` (line 140)

### Modifying File Detection Logic

- **Executables**: Modify `find_executables()` - uses platform-specific extension lists
- **Info Files**: Modify `find_info_file()` in interactive_selector.py - uses priority-based search
- **Archives**: Modify `_has_archives()` or split detection regex patterns

### Testing Changes Safely

Always use `--dry-run` flag when testing deletion/extraction logic:
```bash
python peelx.py --dry-run --debug
```

This shows what would happen without modifying files.

## Dependencies

**Required**: Python 3.6+ with standard library (zipfile, tarfile, gzip, bz2, curses)

**Optional** (install via `pip install -r requirements.txt`):
- `rarfile` - RAR extraction (or use system `unrar`)
- `py7zr` - 7z extraction (or use system `7z`)

**System utilities** (alternative to Python libraries):
- `unrar` - RAR support
- `7z` or `p7zip` - 7z support

## Common Tasks

### Run tests without modifying files
```bash
python peelx.py --dry-run --debug
```

### Create test data
```bash
python create_example.py
```

### Check dependencies
```bash
python check_dependencies.py
```

### Restore from backup (if --backup flag was used)
```bash
python restore_backup.py
```
