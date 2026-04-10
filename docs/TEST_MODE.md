# Test Mode and Backup Features

## Overview

PeelX includes safety features to help you test and recover from failed extractions:

1. **Dry-Run Mode** - Preview what will happen without modifying any files
2. **Backup Mode** - Create backups before deleting archives
3. **Restore Tool** - Restore archives from backups if something goes wrong

## Dry-Run Mode

Preview all actions without actually extracting or deleting anything.

### Usage

**Interactive Mode:**
```bash
python peelx.py --dry-run
```

**Automatic Mode:**
```bash
python peelx_auto.py --dry-run
```

### What It Shows

The dry-run will show:
- ✓ Which archives would be extracted
- ✓ Which files would be deleted
- ✓ Which executables would be available
- ✗ NO files are actually modified

### Example Output

```
🔍 DRY-RUN MODE: No files will be modified
============================================================

Processing: MyGame
  Found 3 archive(s) to extract...
    [DRY-RUN] Would extract: game.rar

Cleaning Up Archives
  [DRY-RUN] Would delete: game.rar
  [DRY-RUN] Would delete: game.r00
  [DRY-RUN] Would delete: game.r01

Total archives that would be deleted: 3
```

## Backup Mode

Create backups of all archives before deletion. This allows you to restore them if extraction fails.

### Usage

**Interactive Mode:**
```bash
python peelx.py --backup
```

**Automatic Mode:**
```bash
python peelx_auto.py --backup
```

### Where Backups Are Stored

Backups are saved in: `archives/.backups/`

Each backup includes:
- Folder name
- Timestamp
- All archive files from that folder

Example structure:
```
archives/
├── .backups/
│   ├── MyGame_20250125_143052/
│   │   ├── game.rar
│   │   ├── game.r00
│   │   └── game.r01
│   └── AnotherApp_20250125_143055/
│       └── app.7z
├── MyGame/
│   └── (extracted files)
└── AnotherApp/
    └── (extracted files)
```

### Example Output

```
============================================================
Backing Up Archives
============================================================

Backing up: MyGame
    Backed up: game.rar
    Backed up: game.r00
    Backed up: game.r01

  📦 Backup saved to: archives/.backups/MyGame_20250125_143052

Total archives backed up: 3
```

## Restore Tool

Use this if extraction failed and you need to recover the original archives.

### List Available Backups

```bash
python restore_backup.py --list
```

Example output:
```
Available backups in archives/.backups:

  [1] MyGame
      Date: 2025-01-25 14:30:52
      Path: archives/.backups/MyGame_20250125_143052

  [2] AnotherApp
      Date: 2025-01-25 14:30:55
      Path: archives/.backups/AnotherApp_20250125_143055
```

### Restore Latest Backup

```bash
python restore_backup.py --latest
```

### Restore Specific Backup

**By name:**
```bash
python restore_backup.py --backup MyGame
```

**Interactive selection:**
```bash
python restore_backup.py
```

Then select from the numbered list.

### Example Restore

```
============================================================
  Archive Restore Tool
============================================================

Restoring from: MyGame_20250125_143052
To: archives/MyGame
------------------------------------------------------------
  Restored: game.rar
  Restored: game.r00
  Restored: game.r01

Total files restored: 3

✓ Restore completed successfully!
```

## Recommended Development Workflow

### First Time Testing

1. **Run dry-run first:**
   ```bash
   python peelx_auto.py --dry-run
   ```

2. **Review the output** to see what will happen

3. **Run with backup:**
   ```bash
   python peelx_auto.py --backup
   ```

4. **If something fails, restore:**
   ```bash
   python restore_backup.py --latest
   ```

### Regular Development

**Option 1: Dry-run for quick testing**
```bash
# See what would happen
python peelx_auto.py --dry-run

# If it looks good, run for real
python peelx_auto.py
```

**Option 2: Always use backup during development**
```bash
# Always create backups
python peelx_auto.py --backup
```

**Option 3: Keep archives, don't delete**
```bash
# Extract but keep archives
python peelx_auto.py --no-delete
```

## Combining Flags

You can combine multiple flags:

```bash
# Dry-run with backup flag (backup won't happen in dry-run)
python peelx_auto.py --dry-run --backup

# Extract, backup, but keep archives
python peelx_auto.py --backup --no-delete

# Just list what's there
python peelx_auto.py --list-only
```

## Safety Tips

1. **Always dry-run first** when testing changes to the extraction code
2. **Use --backup** until you're confident extraction works correctly
3. **Keep backups** until you've verified extracted files work properly
4. **Test with one folder** before processing many folders
5. **Check available disk space** - backups will double the space used by archives

## Cleaning Up Backups

Backups are kept indefinitely. To clean up old backups:

```bash
# Remove all backups
rm -rf archives/.backups

# Remove specific backup
rm -rf archives/.backups/MyGame_20250125_143052
```

## Troubleshooting

### "No backups found"
- Make sure you ran with `--backup` flag
- Check that `archives/.backups/` directory exists
- Backups are only created when archives are deleted (not with `--no-delete`)

### "Backup not found"
- Use `--list` to see available backups
- Check the exact folder name
- Backups are named: `FolderName_YYYYMMDD_HHMMSS`

### Dry-run shows extraction but nothing happens
- That's correct! Dry-run doesn't actually extract
- Remove `--dry-run` flag to perform actual extraction

### Restore overwrites existing files
- Yes, that's intentional
- Restore will overwrite any files with the same names
- Make sure you want to restore before confirming
