# Quick Start Guide

## Try the Demo

1. Create example archives:
   ```bash
   python create_example.py
   ```

2. Run the extractor:
   ```bash
   python peelx.py
   ```

3. Follow the prompts:
   - Select which folders to extract (try selecting all with 'A')
   - Watch as archives are extracted and nested archives are handled automatically
   - Select an executable to run from the menu

## Use With Your Own Files

1. Create the `archives` folder (if it doesn't exist)

2. Add your folders with archives to the `archives` directory:
   ```
   archives/
   ├── my_game/
   │   └── game.zip
   ├── my_tool/
   │   └── installer.rar
   └── my_app/
       └── app.7z
   ```

3. Run the script:
   ```bash
   python peelx.py
   ```

4. Select folders to process, and the script will:
   - Extract all archives (including nested ones)
   - Delete the archive files
   - Show you available executables to run

## Custom Directory

To use a different directory instead of `archives`:

```bash
python peelx.py /path/to/your/directory
```

## Install Optional Dependencies

For RAR and 7Z support:

```bash
pip install -r requirements.txt
```

Or install system utilities:
- RAR: `unrar` command
- 7Z: `7z` command

## Tips

- Only folders you select will be processed
- Archives are only deleted after successful extraction
- Folders without archives are left untouched
- The script handles nested archives automatically
- Executables are detected based on your operating system
