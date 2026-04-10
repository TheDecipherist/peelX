# Interactive Mode Guide

## Overview

The interactive mode provides a cursor-based interface for selecting executables with live NFO/TXT file preview.

## Features

### Dual-Mode Interface

The interactive selector has **two display modes**:

#### Split-Screen Mode (Default)
```
┌─────────────────────────────────┬──────────────────────────────────┐
│     Executables List            │         Preview Panel            │
│                                 │                                  │
│  [1] Game1/game.exe            │  [readme.nfo]                    │
│  [2] Game2/launcher.exe        │                                  │
│ >[3] Tool/setup.exe     <─     │  ╔════════════════════╗          │
│  [4] App/install.exe           │  ║   Tool Info v1.0   ║          │
│  [5] Utility/run.exe           │  ╠════════════════════╣          │
│                                 │  ║ Installation:      ║          │
│  ↑/↓: Navigate                 │  ║ 1. Extract files   ║          │
│  →: Full Preview               │  ║ 2. Run setup.exe   ║          │
│  Enter: Select                 │  ║ 3. Follow prompts  ║          │
│  q: Quit                       │  ╚════════════════════╝          │
└─────────────────────────────────┴──────────────────────────────────┘
```

#### Full-Screen Preview Mode (Press → to enter)
```
┌────────────────────────────────────────────────────────────────────┐
│         PeelX - Preview Mode (Full Screen)             │
│                                                                    │
│  File: Tool/setup.exe | readme.nfo | Lines: 1-25/150              │
│                                                                    │
│  ╔════════════════════════════════════════════════════════════╗   │
│  ║                    Tool Info v1.0                          ║   │
│  ╠════════════════════════════════════════════════════════════╣   │
│  ║                                                            ║   │
│  ║  Installation Instructions:                                ║   │
│  ║  1. Extract all files to a directory                       ║   │
│  ║  2. Run setup.exe as administrator                         ║   │
│  ║  3. Follow the installation wizard                         ║   │
│  ║  4. Restart your computer when prompted                    ║   │
│  ║                                                            ║   │
│  ║  System Requirements:                                      ║   │
│  ║  - Windows 10 or higher                                    ║   │
│  ║  - 4GB RAM minimum                                         ║   │
│  ║  - 500MB disk space                                        ║  █│
│  ║                                                            ║  ││
│  ╚════════════════════════════════════════════════════════════╝  ││
│                                                                   ││
│  ↑/↓: Scroll | PgUp/PgDn: Fast | Home/End | ←: Back | ENTER: Run │
└────────────────────────────────────────────────────────────────────┘
```

**Mode Switching**:
- **→** (Right Arrow) - Enter full-screen preview mode
- **←** (Left Arrow) - Return to split-screen mode

### Navigation

**Split-Screen Mode (List Active):**
- **↑/↓** - Move selection up/down
- **PgUp/PgDn** - Jump 10 items
- **Home/End** - Jump to first/last item
- **→** - Enter full-screen preview mode
- **Enter** - Select and run highlighted executable
- **Q or ESC** - Quit without selecting

**Full-Screen Preview Mode:**
- **↑/↓** - Scroll preview up/down
- **PgUp/PgDn** - Jump 10 lines
- **Home/End** - Jump to top/bottom
- **←** - Return to split-screen mode
- **Enter** - Select and run current executable
- **Q or ESC** - Quit without selecting

### Preview Panel

The preview automatically displays:
1. NFO files (`.nfo`)
2. Text files (`.txt`)
3. DIZ files (`.diz`)
4. Readme files (`.readme`, `.md`)

**Display Modes:**
- **Split-Screen** - Preview shown in right panel (truncated to fit)
- **Full-Screen** - Preview uses entire terminal width (press → to enter)

**Features:**
- **Scrollable content** - Use arrow keys in full-screen mode
- **Line counter** - Shows current position (e.g., "1-25/150")
- **Mode indicator** - Header shows "Preview Mode (Full Screen)" when active
- **Scroll bar** - Visual indicator of position in long files (right edge)

**Search Priority:**
1. Files with same name as executable (e.g., `game.exe` → `game.nfo`)
2. Common names in same directory (`readme.txt`, `info.nfo`)
3. Common names in parent directory

**Encoding Support:**
- UTF-8
- Latin-1 (ISO-8859-1)
- CP437 (DOS)
- CP1252 (Windows)

### Execution Tracking

The selector tracks which executables you've run:

**Features:**
- **Execution counter** - Shows (2x), (5x), etc. for run count
- **Color coding** - Run executables appear in GREEN
- **Persistent log** - Saved to `executions.log` in JSON format
- **Statistics** - Tracks first run, last run, and total count

**Visual Indicators:**
- Normal: White text (not run yet)
- Green: Executable has been run before
- Counter: `(3x)` means run 3 times

**Log File Format:**
```json
{
  "/path/to/game.exe": {
    "count": 3,
    "first_run": "2025-01-25T14:30:00",
    "last_run": "2025-01-25T16:45:00"
  }
}
```

The log is automatically updated each time you select and run an executable.

## Usage

### Enable Interactive Mode (Default)

```bash
python peelx.py
```

The interactive selector will launch automatically when executables are found.

### Disable Interactive Mode

```bash
python peelx.py --no-interactive
```

Uses simple numbered menu instead.

### Test Interactive Mode

```bash
python test_interactive.py
```

Creates sample files and demonstrates the interface.

## Examples

### Example 1: Game with NFO

```
Directory Structure:
  Game/
    ├── game.exe
    └── readme.nfo

Preview Shows:
  [readme.nfo]
  ╔═══════════════════════════════╗
  ║        GAME v1.0              ║
  ╠═══════════════════════════════╣
  ║ Installation instructions...  ║
  ╚═══════════════════════════════╝
```

### Example 2: Tool with TXT

```
Directory Structure:
  Tool/
    ├── setup.exe
    └── README.txt

Preview Shows:
  [README.txt]

  Tool Installation Guide
  =======================
  1. Run setup.exe
  2. Follow the wizard...
```

### Example 3: No Info File

```
Directory Structure:
  App/
    └── launcher.exe

Preview Shows:
  No NFO available

  No readme or info file found
  in the executable's directory.
```

## Keyboard Shortcuts

| Key | Split-Screen Mode | Full-Screen Preview Mode |
|-----|-------------------|--------------------------|
| ↑ | Move selection up | Scroll preview up |
| ↓ | Move selection down | Scroll preview down |
| → | Enter full-screen preview | (No effect) |
| ← | (No effect) | Return to split-screen |
| PgUp | Jump up 10 items | Scroll up 10 lines |
| PgDn | Jump down 10 items | Scroll down 10 lines |
| Home | Jump to first item | Jump to top of preview |
| End | Jump to last item | Jump to bottom of preview |
| Enter | Select and run executable | Select and run executable |
| Q | Quit | Quit |
| ESC | Quit | Quit |

## Visual Indicators

### Selection Highlight

The currently selected executable is shown in reverse video (dark text on light background).

### Scroll Bar

When there are more items than fit on screen, a scrollbar appears on the right:
```
│
█  ← Current position
│
│
```

### File Count

Top of executable list shows: `[number] path`

## Fallback Behavior

If interactive mode fails (e.g., terminal doesn't support curses), the program automatically falls back to simple text menu:

```
Available Executables:
------------------------------------------------------------
  [1] Game/game.exe
  [2] Tool/setup.exe
  [3] App/launcher.exe
  [0] Exit without running
------------------------------------------------------------

Select executable to run (number): _
```

## Tips

1. **Wide Terminal Recommended** - At least 80 characters wide for best experience
2. **Resize Terminal** - Interface adapts to terminal size changes
3. **NFO Art** - CP437 encoding handles ASCII art NFO files correctly
4. **Long Lists** - Use PgUp/PgDn for faster navigation
5. **Cancel Anytime** - Press Q or ESC to exit without running anything

## Troubleshooting

### "Interactive mode not available"
- Your terminal may not support curses
- Try running in a different terminal
- Use `--no-interactive` flag for simple menu

### "Interactive mode failed"
- Check terminal compatibility
- Ensure terminal is not in restricted mode
- Program will automatically fall back to simple menu

### NFO looks garbled
- Try a terminal with better encoding support
- Use `--no-interactive` for simple view
- The program tries multiple encodings automatically

### Can't see preview panel
- Terminal may be too narrow
- Resize terminal to at least 80 characters wide
- Preview requires minimum 60 characters for executable list + 20 for preview

### Selection doesn't highlight
- Terminal may not support reverse video
- Try a different terminal emulator
- Functionality still works even if highlighting doesn't show

## Technical Details

### Requirements
- Python 3.6+
- Terminal with curses support (most Unix terminals, Windows Terminal, WSL)
- Minimum 60 character width recommended

### File Detection Logic

The selector searches in this priority order:

1. **Exact match**: `{executable_name}.nfo`, `{executable_name}.txt`, etc.
2. **Common names**: `readme.nfo`, `info.txt`, etc. in same directory
3. **Any .nfo file**: Finds files like `R2R.nfo`, `release.nfo`, etc. ← **NEW!**
4. **Parent directory**: Searches parent folder using same logic
5. **Case insensitive**: Works with `.NFO`, `.TXT`, `.Nfo`, etc.

**Extension priority**: `.nfo`, `.txt`, `.diz`, `.readme`, `.md`

This ensures R2R-style releases with `R2R.nfo` are properly detected!

### Encoding Detection

Tries encodings in order:
1. UTF-8 (modern standard)
2. Latin-1 (ISO-8859-1)
3. CP437 (DOS/NFO art)
4. CP1252 (Windows)
5. ISO-8859-1

### Performance

- Files are read on-demand when selected
- Preview truncated at 100 lines for performance
- Smooth scrolling with offset calculation
- Efficient screen updates

## Comparison

| Feature | Interactive Mode | Simple Mode |
|---------|-----------------|-------------|
| Navigation | Arrow keys | Number input |
| Preview | Live NFO/TXT | None |
| Speed | Fast browsing | Type numbers |
| Accessibility | Visual | Screen reader friendly |
| Compatibility | Curses required | Works everywhere |

## See Also

- [README.md](README.md) - Main documentation
- [QUICK_REFERENCE.md](QUICK_REFERENCE.md) - Command reference
- `test_interactive.py` - Interactive mode demo
