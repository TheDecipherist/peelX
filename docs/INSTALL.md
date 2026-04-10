# Installation Guide

## Required Tools for RAR and 7Z Support

PeelX needs external tools to handle RAR and 7Z files properly, especially split archives and files with advanced compression.

### Ubuntu/Debian/WSL

```bash
sudo apt-get update
sudo apt-get install -y unrar p7zip-full
```

### macOS

```bash
brew install unrar p7zip
```

### Windows

**Option 1: Using Chocolatey**
```powershell
choco install 7zip unrar
```

**Option 2: Manual Installation**
1. Download and install [7-Zip](https://www.7-zip.org/download.html)
2. Download and install [WinRAR](https://www.win-rar.com/download.html) or unrar
3. Add them to your PATH

### Verify Installation

Run the check script to verify everything is installed:

```bash
python check_dependencies.py
```

## Optional Python Libraries

While system tools are recommended, you can also install Python libraries:

```bash
pip install -r requirements.txt
```

**Note:** Python libraries have limitations:
- `rarfile` requires the `unrar` command anyway
- `py7zr` doesn't support all compression methods (like BCJ2)

System tools (`unrar` and `7z`) are more reliable and recommended.

## What Happens Without These Tools?

- **ZIP, TAR, GZ, BZ2**: Work out of the box with Python's standard library
- **RAR files**: Will fail to extract without `unrar` or `rarfile`
- **7Z files**: May fail with complex compression without `7z` command
- **Split archives**: Require system tools for proper handling

## Troubleshooting

### "Could not extract RAR"
Install unrar:
```bash
sudo apt-get install unrar
```

### "Could not extract 7z" or "BCJ2 filter not supported"
Install p7zip-full:
```bash
sudo apt-get install p7zip-full
```

### On WSL (Windows Subsystem for Linux)
The commands above should work. If you have permission issues, make sure you're running in a WSL terminal, not Windows CMD/PowerShell.

### Permission Issues
If you can't use `sudo`, ask your system administrator to install:
- `unrar`
- `p7zip-full` (provides the `7z` command)
