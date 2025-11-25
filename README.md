# Archive Extractor and Executable Runner

A Python utility that scans directories, recursively extracts nested archives, and provides an interface to run executables.

## Features

- Scans a base directory for folders containing archives
- Supports multiple archive formats: ZIP, RAR, 7Z, TAR, GZ, BZ2, XZ, TGZ, TBZ2
- Recursively extracts nested archives (archives within archives)
- Interactive folder selection
- Automatic cleanup of archive files after extraction
- Cross-platform executable detection and running
- Clean command-line interface

## Requirements

### Core Requirements
- Python 3.6 or higher
- Standard library modules (included with Python):
  - `zipfile` (for ZIP files)
  - `tarfile` (for TAR files)
  - `gzip` (for GZ files)
  - `bz2` (for BZ2 files)

### Optional Dependencies

For RAR files:
```bash
pip install rarfile
```
Or install `unrar` system utility

For 7Z files:
```bash
pip install py7zr
```
Or install `7z` system utility

### Quick Install
```bash
pip install -r requirements.txt
```

## Usage

### Basic Usage

1. Create an `archives` directory in the same location as the script
2. Add folders containing archives to the `archives` directory
3. Run the script:

```bash
python archive_extractor.py
```

### Test Mode (Recommended for Development)

**Preview what will happen without modifying files:**
```bash
python archive_extractor.py --dry-run
```

**Create backups before deleting archives:**
```bash
python archive_extractor.py --backup
```

See [TEST_MODE.md](TEST_MODE.md) for detailed test mode documentation.

### Custom Directory

You can specify a custom directory to scan:

```bash
python archive_extractor.py /path/to/your/directory
```

### Workflow

The script follows this workflow:

1. **Scan**: Scans the base directory for folders
2. **Select**: Shows folders containing archives and lets you select which to process
3. **Extract**: Recursively extracts all archives (including nested ones)
4. **Cleanup**: Deletes all archive files, keeping extracted content
5. **Run**: Interactive selector with NFO/TXT preview to choose and run executables

### Interactive Executable Selector

The program features an interactive cursor-based interface for selecting executables:

**Features:**
- **Dual-mode interface** - Split-screen and full-screen preview modes
- **Full-screen preview** - Press → to expand preview to full terminal width
- **Scrollable preview** - Read long NFO/TXT files with full scroll support
- **Execution tracking** - Track which executables you've run (shown in GREEN with count)
- **Live NFO/TXT preview** - Shows readme/info files automatically
- **Automatic file detection** - Finds .nfo, .txt, .diz files near executables

**Keyboard shortcuts:**
- **Split-Screen**: `↑/↓` Navigate | `→` Full preview | `Enter` Run
- **Full-Screen Preview**: `↑/↓` Scroll | `←` Back to split | `PgUp/PgDn` Jump
- **Both Modes**: `Home/End` Jump to start/end | `Q/ESC` Quit

**Execution tracking:**
- Previously run executables shown in GREEN
- Execution count displayed: (2x), (5x), etc.
- Log saved to `executions.log`

**Disable interactive mode:**
```bash
python archive_extractor.py --no-interactive
```

## Example Directory Structure

```
archives/
├── game1/
│   ├── game.zip          # Will be extracted and deleted
│   └── (extracted files)
├── game2/
│   ├── setup.rar         # Will be extracted and deleted
│   │   └── installer.exe # (nested, will be extracted)
│   └── (extracted files)
└── tool/
    └── tool.exe          # No archive, folder left unchanged
```

## Supported Archive Formats

- **.zip** - ZIP archives
- **.rar** - RAR archives (requires rarfile or unrar)
- **.7z** - 7-Zip archives (requires py7zr or 7z command)
- **.tar** - TAR archives
- **.tar.gz, .tgz** - Gzipped TAR archives
- **.tar.bz2, .tbz2** - Bzipped TAR archives
- **.tar.xz** - XZ compressed TAR archives
- **.gz** - Gzip files
- **.bz2** - Bzip2 files

## Supported Executable Types

### Windows
- .exe
- .bat
- .cmd
- .msi

### Linux
- .sh
- .bin
- .run
- Any file with execute permissions

### macOS
- .app
- .sh
- .command
- Any file with execute permissions

## Notes

- Archives are extracted to their parent directory
- The script handles nested archives automatically (up to 50 levels deep)
- If extraction fails for an archive, it will be skipped
- Folders without archives are left unchanged
- The script runs executables from their parent directory

### What Gets Deleted

After successful extraction, the following files are deleted:
- **Archive files**: `.zip`, `.rar`, `.7z`, `.tar`, `.gz`, `.bz2`, etc.
- **Split archive parts**: `.r00`, `.r01`, `.z01`, `.001`, `.002`, etc.
- **Checksum files**: `.sfv`, `.md5`, `.sha1`, `.sha256`, `.crc`
- **Parity files**: `.par`, `.par2`

### What Gets Kept

These files are preserved after extraction:
- **Info files**: `.nfo`, `.txt`, `.diz`
- **Extracted content**: All files extracted from archives
- **Executables**: `.exe`, `.bat`, `.sh`, etc.

## Safety Features

- Only processes folders you explicitly select
- Archives are only deleted after successful extraction
- Maximum iteration limit prevents infinite loops with circular archive references
- Clear feedback for each operation

## Troubleshooting

### RAR files won't extract
Install either:
```bash
pip install rarfile
```
Or the system `unrar` utility:
- Ubuntu/Debian: `sudo apt-get install unrar`
- macOS: `brew install unrar`
- Windows: Download from rarlab.com

### 7Z files won't extract
Install either:
```bash
pip install py7zr
```
Or the system `7z` utility:
- Ubuntu/Debian: `sudo apt-get install p7zip-full`
- macOS: `brew install p7zip`
- Windows: Download from 7-zip.org

### Executable won't run on Linux/macOS
The script attempts to set execute permissions automatically, but you may need to do it manually:
```bash
chmod +x /path/to/executable
```

## License

This is free and unencumbered software released into the public domain.
