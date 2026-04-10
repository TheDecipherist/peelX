# Progress Indicator Mode

## Overview

PeelX now features clean progress indicators that show percentage completion (1-100%) during extraction and cleanup operations. This provides a better user experience with less terminal clutter.

## Modes

### Normal Mode (Default)

Shows clean percentage-based progress:

```
Extracting: 75%
Cleaning up: 50%
```

**Benefits:**
- Clean, minimal output
- Easy to read at a glance
- No terminal spam
- Professional appearance
- Real-time updates with carriage return

**Usage:**
```bash
python peelx.py
```

### Debug Mode

Shows detailed file-by-file operations:

```
[75%] Extracting: game.zip
[76%] Extracting: setup.rar
[50%] Deleted: archive.rar
[51%] Deleted: archive.r00
```

**Benefits:**
- See exactly which file is being processed
- Useful for troubleshooting
- Track specific files
- Development and debugging

**Usage:**
```bash
python peelx.py --debug
```

## Visual Comparison

### Normal Mode
```
Processing: Game1
  Extracting: 100% ✓

Cleaning: Game1
  Cleaning up: 100% ✓
```

### Debug Mode
```
Processing: Game1
  Found 3 archive(s) to extract...
    [33%] Extracting: game.zip
    [66%] Extracting: setup.rar
    [100%] Extracting: data.7z

Cleaning: Game1
    [25%] Deleted: game.zip
    [50%] Deleted: setup.rar
    [75%] Deleted: data.7z
    [100%] Deleted: game.sfv
```

## Technical Details

### Progress Calculation
```python
progress = int((current_file / total_files) * 100)
```

### Display Method
- **Normal Mode**: Uses `\r` (carriage return) to overwrite the same line
- **Debug Mode**: Prints each file on a new line with percentage prefix

### Completion Indicator
Normal mode completes with a checkmark:
```
Extracting: 100% ✓
Cleaning up: 100% ✓
```

## When to Use Each Mode

### Use Normal Mode When:
- Running the program regularly
- You trust the extraction process
- You want clean, minimal output
- Terminal clutter is a concern
- You're showing the output to others

### Use Debug Mode When:
- Troubleshooting extraction issues
- Verifying specific files are processed
- Developing or testing the program
- You need detailed logs
- Tracking down problems with specific archives

## Examples

### Standard Operation (Normal Mode)
```bash
$ python peelx.py

============================================================
  PeelX - Archive Extractor and Executable Runner
============================================================

Scanning directory: /home/user/archives

Processing: Game1
  Extracting: 100% ✓

Cleaning: Game1
  Cleaning up: 100% ✓

Done!
```

### Detailed Operation (Debug Mode)
```bash
$ python peelx.py --debug

============================================================
  PeelX - Archive Extractor and Executable Runner
============================================================

🐛 DEBUG MODE: Detailed output enabled
============================================================

Scanning directory: /home/user/archives

Processing: Game1
  Found 2 archive(s) to extract...
    [50%] Extracting: game.zip
    [100%] Extracting: setup.rar
  Extracting: 100% ✓

Cleaning: Game1
    [33%] Deleted: game.zip
    [66%] Deleted: setup.rar
    [100%] Deleted: game.sfv
  Cleaning up: 100% ✓

Done!
```

## Combining with Other Flags

### Dry-Run with Normal Mode
```bash
python peelx.py --dry-run
# Shows: Extracting: 75% (but doesn't actually extract)
```

### Dry-Run with Debug Mode
```bash
python peelx.py --dry-run --debug
# Shows: [75%] [DRY-RUN] Would extract: game.zip
```

### Backup with Progress
```bash
python peelx.py --backup
# Normal progress indicators during extraction and cleanup
```

### All Safety Features
```bash
python peelx.py --dry-run --backup --debug
# Preview mode + backups + detailed output
```

## Performance

Progress indicators have minimal performance impact:
- Normal mode: Single line update (very fast)
- Debug mode: One print per file (negligible overhead)
- Progress calculation: Simple division operation

## Compatibility

Works on all platforms:
- **Windows**: Full support with cmd.exe and PowerShell
- **Linux**: Full support with bash, zsh, etc.
- **macOS**: Full support with Terminal.app
- **WSL**: Full support with Windows Terminal

## Testing

Test the progress indicators:

```bash
python test_progress.py
```

This demo script shows both modes side-by-side with simulated operations.

## See Also

- [README.md](README.md) - Main documentation
- [CHANGELOG.md](CHANGELOG.md) - Version history (see v1.5)
- [TEST_MODE.md](TEST_MODE.md) - Testing features
