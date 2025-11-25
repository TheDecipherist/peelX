# Changelog

## Version 1.5 - Full-Screen Preview Mode & WSL Support

### Added
- **Full-screen preview mode** - Preview takes over entire terminal
  - Press → to enter full-screen preview (from split-screen)
  - Press ← to return to split-screen mode
  - Uses full terminal width for better NFO/TXT reading
  - Scrollbar on right edge shows position
  - Header shows "Preview Mode (Full Screen)" when active

- **WSL (Windows Subsystem for Linux) support** - Run Windows executables from WSL
  - Automatic WSL environment detection
  - Path conversion from Linux (`/mnt/c/`) to Windows (`C:\`) format
  - Windows executables (.exe, .bat, .cmd, .msi) run through `cmd.exe`
  - Proper working directory handling

- **Progress indicators** - Clean percentage-based progress display
  - Extraction progress: "Extracting: 75%"
  - Cleanup progress: "Cleaning up: 50%"
  - Real-time updates using carriage return for smooth display
  - Completes with checkmark: "Extracting: 100% ✓"

- **Debug mode** - Detailed output for troubleshooting
  - `--debug` flag shows individual file names during operations
  - Default mode shows only percentage progress (cleaner UX)
  - Available in both interactive and auto modes
  - Useful for development and debugging

### Enhanced
- **Dual-mode interface** - Switch seamlessly between split-screen and full-screen
  - Split-screen: List on left, compact preview on right
  - Full-screen: Preview uses entire terminal width
  - Context-sensitive keyboard controls adapt to active mode
- **Better readability** - No text truncation in full-screen mode
- **Mode indicators** - Clear visual feedback in header and footer
- **Cross-platform execution** - Improved executable running on Windows, Linux, macOS, and WSL
- **Cleaner output** - Progress indicators reduce terminal clutter by default

## Version 1.4 - Two-Pane Navigation & Execution Tracking

### Added
- **Two-pane navigation** - Switch between list and preview with arrow keys
  - Press → to move to preview pane
  - Press ← to return to list pane
  - Active pane indicated with bold border

- **Scrollable preview panel** - Full NFO/TXT scrolling support
  - ↑/↓ to scroll line by line
  - PgUp/PgDn for 10-line jumps
  - Home/End to jump to top/bottom
  - Line counter shows position (e.g., "1-20/150")
  - Visual scrollbar indicator

- **Execution tracking system** - Track which executables you've run
  - Automatic logging to `executions.log`
  - Execution count displayed: (2x), (5x), etc.
  - GREEN color for previously run executables
  - Persistent JSON log with timestamps
  - Tracks count, first run, and last run

### Enhanced
- Context-sensitive help text changes based on active pane
- Better visual feedback for active/inactive panes
- Execution count integrated into executable list display

## Version 1.3 - Interactive Selector with NFO Preview

### Added
- **Interactive Executable Selector** - New cursor-based interface
  - Arrow key navigation (↑/↓, PgUp/PgDn, Home/End)
  - Live NFO/TXT/DIZ file preview in side panel
  - Automatic detection of readme files near executables
  - Smooth scrolling with visual indicators
  - Falls back to simple menu if curses unavailable

- **NFO Preview Panel** - Real-time file preview
  - Shows .nfo, .txt, .diz, .readme, .md files
  - Searches executable directory and parent
  - Handles multiple encodings (UTF-8, Latin-1, CP437, etc.)
  - Displays "No NFO available" when not found

### Enhanced
- **Improved NFO detection** - Now finds ANY .nfo file in directory
  - Detects R2R.nfo, release.nfo, etc. (not just executable-named files)
  - Case-insensitive extension matching (.nfo, .NFO, .Nfo)
  - Comprehensive search in current and parent directories
- Added `--no-interactive` flag to disable new UI
- Improved error handling with graceful fallback
- Better user experience with visual feedback

### Fixed
- NFO files with non-standard names (like R2R.nfo) are now detected
- Case sensitivity issues on Linux/Unix filesystems

## Version 1.2 - Test Mode and Backup Features

### Added
- **Dry-Run Mode** - Preview all actions without modifying files
  - Use `--dry-run` flag to test before running
  - Shows what archives would be extracted and deleted
  - Perfect for development and testing

- **Backup System** - Create backups before deleting archives
  - Use `--backup` flag to backup archives before deletion
  - Backups saved to `archives/.backups/` with timestamps
  - Allows recovery if extraction fails

- **Restore Tool** - Recover from failed extractions
  - `restore_backup.py` script to restore archives
  - List, select, and restore backups interactively
  - Supports `--latest`, `--backup name`, and `--list` options

- **Checksum File Cleanup** - Archive metadata files are now deleted
  - `.sfv` (Simple File Verification) files deleted with archives
  - Also deletes `.md5`, `.sha1`, `.sha256`, `.crc` files
  - Parity files (`.par`, `.par2`) also cleaned up

### Enhanced
- All modes (interactive and auto) support new flags
- Clear visual indicators for dry-run mode
- Timestamped backups for easy identification
- `.nfo` files are preserved (not deleted with archives)

## Version 1.1 - Split Archive Support

### Fixed
- **Split archive files are now properly deleted** after extraction
  - Added detection for RAR split archives (`.r00`, `.r01`, `.r02`, etc.)
  - Added detection for ZIP split archives (`.z01`, `.z02`, etc.)
  - Added detection for generic numbered splits (`.001`, `.002`, `.003`, etc.)
  - Added detection for 7z split archives (`.7z.001`, `.7z.002`, etc.)

- **Improved executable detection**
  - Excluded non-executable file types (`.nfo`, `.sfv`, `.txt`, `.log`, etc.)
  - Excluded archive files from executable list
  - Now only shows actual executable files (`.exe`, `.bat`, `.sh`, etc.)

- **Fixed folder selection**
  - All folders are now displayed, not just those with archives
  - Folders without archives are shown as "already ready"
  - Executables from all folders (including those without archives) are available to run
  - User can skip extraction and go directly to executable selection

### Technical Details

**Split Archive Detection:**
```python
# Now detects these patterns as archives:
- *.r00, *.r01, *.r99    # RAR splits
- *.z01, *.z02           # ZIP splits
- *.001, *.002, *.003    # Generic splits
- *.7z.001, *.7z.002     # 7z splits
```

**Files Excluded from Executables:**
```
.nfo, .txt, .md, .sfv, .diz, .readme,
.log, .ini, .cfg, .conf, .json, .xml,
.jpg, .jpeg, .png, .gif, .bmp,
.mp3, .wav, .flac, .ogg,
.pdf, .doc, .docx
```

### Example

**Before:**
```
After extraction, split files remained:
- r2r12979.rar
- r2r12979.r00  ← Not deleted
- r2r12979.r01  ← Not deleted
```

**After:**
```
After extraction, all archive parts are deleted:
✓ Deleted: r2r12979.rar
✓ Deleted: r2r12979.r00
✓ Deleted: r2r12979.r01

Kept:
- R2R.nfo
- r2r12979.sfv
- (extracted content)
```

## Version 1.0 - Initial Release

### Features
- Directory scanning for archives
- Recursive archive extraction (handles nested archives)
- Support for ZIP, RAR, 7Z, TAR, GZ, BZ2, XZ formats
- Interactive folder selection
- Archive cleanup after extraction
- Cross-platform executable detection and running
- Command-line interface
