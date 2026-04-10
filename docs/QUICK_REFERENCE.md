# Quick Reference Guide

## Command Line Options

### Interactive Mode

```bash
# Basic usage (with interactive selector)
python peelx.py

# Disable interactive selector
python peelx.py --no-interactive

# Preview without changes (recommended first)
python peelx.py --dry-run

# Create backups before deleting
python peelx.py --backup

# Custom directory
python peelx.py /path/to/directory

# Combine options
python peelx.py --dry-run --backup --no-interactive
```

### Automatic Mode

```bash
# Process all folders automatically
python peelx_auto.py

# Preview only (dry-run)
python peelx_auto.py --dry-run

# Create backups
python peelx_auto.py --backup

# Keep archives (don't delete)
python peelx_auto.py --no-delete

# List folders only (no extraction)
python peelx_auto.py --list-only

# Skip executable running
python peelx_auto.py --no-run
```

### Restore Backups

```bash
# List available backups
python restore_backup.py --list

# Restore latest backup
python restore_backup.py --latest

# Restore specific backup
python restore_backup.py --backup FolderName

# Interactive restore
python restore_backup.py
```

### Utility Scripts

```bash
# Check dependencies
python check_dependencies.py

# Create example archives for testing
python create_example.py

# Test archive detection
python test_scanner.py
```

## Common Workflows

### Development/Testing

```bash
# 1. Preview first
python peelx_auto.py --dry-run

# 2. If looks good, run with backup
python peelx_auto.py --backup

# 3. If fails, restore
python restore_backup.py --latest
```

### Production Use

```bash
# Extract and clean up
python peelx.py
```

### Safe Mode

```bash
# Extract but keep archives
python peelx_auto.py --no-delete
```

## File Structure

```
peelx/
├── peelx.py                       # Main interactive program
├── peelx_auto.py                  # Automatic batch mode
├── restore_backup.py              # Restore tool
├── check_dependencies.py          # Dependency checker
├── create_example.py              # Create test archives
├── test_scanner.py                # Test executable detection
├── archives/                      # Your archive folders
│   ├── .backups/                  # Backup storage
│   ├── folder1/
│   ├── folder2/
│   └── folder3/
├── README.md                      # Main documentation
├── TEST_MODE.md                   # Test mode guide
├── INSTALL.md                     # Installation instructions
├── QUICKSTART.md                  # Quick start guide
└── requirements.txt               # Python dependencies
```

## Supported Archive Formats

| Format | Extension | Support |
|--------|-----------|---------|
| ZIP | .zip | ✓ Built-in |
| TAR | .tar, .tar.gz, .tgz, .tar.bz2, .tbz2, .tar.xz | ✓ Built-in |
| GZIP | .gz | ✓ Built-in |
| BZIP2 | .bz2 | ✓ Built-in |
| RAR | .rar, .r00, .r01, etc. | Requires `unrar` |
| 7Z | .7z | Requires `7z` |

**Split Archives:**
- RAR: `.rar` + `.r00`, `.r01`, `.r02`, etc.
- ZIP: `.zip` + `.z01`, `.z02`, etc.
- 7Z: `.7z` + `.7z.001`, `.7z.002`, etc.
- Generic: `.001`, `.002`, `.003`, etc.

## Flags Summary

| Flag | Interactive | Auto | Description |
|------|------------|------|-------------|
| `--dry-run` | ✓ | ✓ | Preview without changes |
| `--backup` | ✓ | ✓ | Backup before delete |
| `--no-interactive` | ✓ | ✗ | Disable interactive selector |
| `--no-delete` | ✗ | ✓ | Keep archive files |
| `--no-run` | ✗ | ✓ | Skip executable running |
| `--list-only` | ✗ | ✓ | List folders only |
| `--list` | ✗ | ✗ | List backups (restore tool) |
| `--latest` | ✗ | ✗ | Restore latest (restore tool) |

## Important Notes

1. **Split archives**: Only the main archive file (.rar) needs to be extracted - it automatically uses the split parts (.r00, .r01)

2. **All split parts are deleted**: After extraction, both the main archive and all split parts are removed

3. **Dry-run is safe**: Use it as often as you want - it never modifies files

4. **Backups use disk space**: Backups duplicate archive files, ensure you have enough space

5. **System tools preferred**: Install `unrar` and `7z` for best compatibility

## Troubleshooting

| Problem | Solution |
|---------|----------|
| "Could not extract RAR" | Install `unrar`: `sudo apt-get install unrar` |
| "BCJ2 filter not supported" | Install `7z`: `sudo apt-get install p7zip-full` |
| Files corrupted after extraction | Use `--backup` and restore with `restore_backup.py` |
| Want to test safely | Use `--dry-run` first |
| Need to undo deletion | Use `restore_backup.py` if you ran with `--backup` |

## Getting Help

```bash
# Main program help
python peelx.py --help

# Auto mode help
python peelx_auto.py --help

# Restore tool help
python restore_backup.py --help
```

## Quick Install

```bash
# Install system dependencies (Ubuntu/WSL)
sudo apt-get update
sudo apt-get install -y unrar p7zip-full

# Install Python dependencies (optional)
pip install -r requirements.txt

# Check everything is installed
python check_dependencies.py
```
