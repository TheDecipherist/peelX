#!/usr/bin/env python3
"""
Interactive executable selector with NFO/TXT preview.
Uses cursor keys for navigation and displays info files in a side panel.
"""

import curses
import json
from pathlib import Path
from typing import List, Optional, Tuple, Dict
from datetime import datetime


class ExecutionTracker:
    """Track executable execution history."""

    def __init__(self, log_file: Path = None):
        if log_file is None:
            log_file = Path.cwd() / "executions.log"
        self.log_file = log_file
        self.executions = self._load_log()

    def _load_log(self) -> Dict:
        """Load execution log from file."""
        if self.log_file.exists():
            try:
                with open(self.log_file, 'r') as f:
                    return json.load(f)
            except (json.JSONDecodeError, IOError):
                return {}
        return {}

    def _save_log(self):
        """Save execution log to file."""
        try:
            with open(self.log_file, 'w') as f:
                json.dump(self.executions, f, indent=2)
        except IOError:
            pass

    def record_execution(self, executable_path: str):
        """Record an execution."""
        if executable_path not in self.executions:
            self.executions[executable_path] = {
                'count': 0,
                'first_run': None,
                'last_run': None
            }

        self.executions[executable_path]['count'] += 1
        now = datetime.now().isoformat()

        if self.executions[executable_path]['first_run'] is None:
            self.executions[executable_path]['first_run'] = now

        self.executions[executable_path]['last_run'] = now
        self._save_log()

    def get_execution_count(self, executable_path: str) -> int:
        """Get execution count for an executable."""
        return self.executions.get(executable_path, {}).get('count', 0)

    def has_been_run(self, executable_path: str) -> bool:
        """Check if executable has been run before."""
        return executable_path in self.executions and self.executions[executable_path]['count'] > 0


class InteractiveSelector:
    """Interactive selector with preview panel."""

    def __init__(self, executables: List[Path], base_dir: Path):
        self.executables = executables
        self.base_dir = base_dir
        self.current_index = 0
        self.scroll_offset = 0
        self.preview_scroll = 0
        self.active_pane = 'list'  # 'list' or 'preview'
        self.tracker = ExecutionTracker()

    def find_info_file(self, executable: Path) -> Optional[Path]:
        """
        Find associated NFO or TXT file near the executable.
        Searches in the same directory and parent directories.
        """
        search_dir = executable.parent

        # Priority order for extensions
        info_extensions = ['.nfo', '.txt', '.diz', '.readme', '.md']

        # 1. Try exact match with executable name
        base_name = executable.stem
        for ext in info_extensions:
            info_file = search_dir / f"{base_name}{ext}"
            if info_file.exists() and info_file.is_file():
                return info_file

        # 2. Try common readme names
        for ext in info_extensions:
            for common_name in ['readme', 'info', 'read_me', 'read me', 'information']:
                info_file = search_dir / f"{common_name}{ext}"
                if info_file.exists() and info_file.is_file():
                    return info_file

        # 3. Find ANY file with info extension in the same directory
        # This catches files like "R2R.nfo", "release.nfo", etc.
        for ext in info_extensions:
            try:
                # Try lowercase
                for file_path in search_dir.glob(f"*{ext}"):
                    if file_path.is_file():
                        return file_path
                # Try uppercase (for case-sensitive filesystems)
                for file_path in search_dir.glob(f"*{ext.upper()}"):
                    if file_path.is_file():
                        return file_path
            except (OSError, PermissionError):
                continue

        # 4. Search parent directory
        if search_dir.parent != search_dir:
            for ext in info_extensions:
                for common_name in ['readme', 'info', 'read_me', 'read me']:
                    info_file = search_dir.parent / f"{common_name}{ext}"
                    if info_file.exists() and info_file.is_file():
                        return info_file

            # 5. Find ANY info file in parent directory
            for ext in info_extensions:
                try:
                    # Try lowercase
                    for file_path in search_dir.parent.glob(f"*{ext}"):
                        if file_path.is_file():
                            return file_path
                    # Try uppercase
                    for file_path in search_dir.parent.glob(f"*{ext.upper()}"):
                        if file_path.is_file():
                            return file_path
                except (OSError, PermissionError):
                    continue

        return None

    def read_info_file(self, info_file: Path, max_lines: int = 100) -> List[str]:
        """Read info file content, handling different encodings."""
        encodings = ['utf-8', 'latin-1', 'cp437', 'cp1252', 'iso-8859-1']

        for encoding in encodings:
            try:
                with open(info_file, 'r', encoding=encoding) as f:
                    lines = []
                    for i, line in enumerate(f):
                        if i >= max_lines:
                            lines.append(f"... (truncated, showing first {max_lines} lines)")
                            break
                        # Remove trailing whitespace but keep line structure
                        lines.append(line.rstrip())
                    return lines
            except (UnicodeDecodeError, UnicodeError):
                continue
            except Exception as e:
                return [f"Error reading file: {e}"]

        return ["Could not decode file (unknown encoding)"]

    def draw_header(self, stdscr, width: int):
        """Draw the header."""
        if self.active_pane == 'preview':
            header = "Archive Extractor - Preview Mode (Full Screen)"
            help_text = "↑/↓: Scroll | PgUp/PgDn: Fast Scroll | Home/End | ←: Back to List | ENTER: Run | q: Quit"
        else:
            header = "Archive Extractor - Select Executable to Run"
            help_text = "↑/↓: Navigate | →: Full Preview | ENTER: Run | q: Quit"

        try:
            stdscr.addstr(0, 0, header[:width], curses.A_BOLD | curses.A_REVERSE)
            stdscr.addstr(1, 0, help_text[:width], curses.A_DIM)
        except curses.error:
            pass

    def draw_executable_list(self, stdscr, height: int, width: int, list_width: int):
        """Draw the list of executables."""
        # Draw border
        try:
            stdscr.addstr(3, 0, "─" * list_width)
            stdscr.addstr(3, 0, " Executables ", curses.A_BOLD)
        except curses.error:
            pass

        # Calculate visible range
        visible_height = height - 5
        max_scroll = max(0, len(self.executables) - visible_height)
        self.scroll_offset = max(0, min(self.scroll_offset, max_scroll))

        # Adjust scroll to keep current item visible
        if self.current_index < self.scroll_offset:
            self.scroll_offset = self.current_index
        elif self.current_index >= self.scroll_offset + visible_height:
            self.scroll_offset = self.current_index - visible_height + 1

        # Draw executables
        for i in range(visible_height):
            idx = i + self.scroll_offset
            if idx >= len(self.executables):
                break

            exe = self.executables[idx]
            try:
                rel_path = exe.relative_to(self.base_dir)
            except ValueError:
                rel_path = exe

            # Check execution status
            exe_str = str(exe.absolute())
            exec_count = self.tracker.get_execution_count(exe_str)
            has_run = self.tracker.has_been_run(exe_str)

            # Truncate if too long
            display_text = str(rel_path)
            max_text_width = list_width - 4
            if has_run:
                # Add execution count indicator
                count_indicator = f"({exec_count}x) "
                max_text_width -= len(count_indicator)
                display_text = count_indicator + display_text

            if len(display_text) > max_text_width:
                display_text = "..." + display_text[-(max_text_width-3):]

            # Format: [number] path
            line_num = f"[{idx+1}]".ljust(6)
            line_text = f"{line_num}{display_text}"

            # Determine color/style
            y_pos = 4 + i
            try:
                if idx == self.current_index:
                    # Current selection - reverse video
                    if has_run:
                        # Already run - green background when selected
                        stdscr.addstr(y_pos, 0, line_text[:list_width],
                                    curses.A_REVERSE | curses.A_BOLD | curses.color_pair(2))
                    else:
                        # Not run - normal reverse
                        stdscr.addstr(y_pos, 0, line_text[:list_width],
                                    curses.A_REVERSE | curses.A_BOLD)
                else:
                    # Not selected
                    if has_run:
                        # Already run - show in green/dim
                        stdscr.addstr(y_pos, 0, line_text[:list_width],
                                    curses.color_pair(2))
                    else:
                        # Not run - normal
                        stdscr.addstr(y_pos, 0, line_text[:list_width])
            except curses.error:
                pass

        # Draw scrollbar indicator
        if len(self.executables) > visible_height:
            scroll_pos = int((self.scroll_offset / max_scroll) * (visible_height - 1)) if max_scroll > 0 else 0
            try:
                for i in range(visible_height):
                    y_pos = 4 + i
                    if i == scroll_pos:
                        stdscr.addstr(y_pos, list_width - 1, "█")
                    else:
                        stdscr.addstr(y_pos, list_width - 1, "│")
            except curses.error:
                pass

    def draw_preview_panel(self, stdscr, height: int, width: int, list_width: int):
        """Draw the preview panel with NFO/TXT content."""
        panel_x = list_width + 1
        panel_width = width - panel_x

        if panel_width < 20:
            return  # Not enough space for preview

        # Draw border with active indicator
        border_char = "━" if self.active_pane == 'preview' else "─"
        try:
            stdscr.addstr(3, panel_x, border_char * (panel_width - 1))
            preview_label = " Preview "
            if self.active_pane == 'preview':
                preview_label = " Preview [ACTIVE] "
            stdscr.addstr(3, panel_x, preview_label, curses.A_BOLD)
        except curses.error:
            pass

        # Get current executable
        if 0 <= self.current_index < len(self.executables):
            exe = self.executables[self.current_index]
            info_file = self.find_info_file(exe)

            if info_file:
                # Read content
                content = self.read_info_file(info_file)
                visible_height = height - 6

                # Calculate scroll limits
                max_scroll = max(0, len(content) - visible_height)
                self.preview_scroll = max(0, min(self.preview_scroll, max_scroll))

                # Show info file name and scroll position
                try:
                    file_label = f"[{info_file.name}]"
                    if len(content) > visible_height:
                        scroll_info = f" ({self.preview_scroll + 1}-{min(self.preview_scroll + visible_height, len(content))}/{len(content)})"
                        file_label += scroll_info
                    stdscr.addstr(4, panel_x, file_label[:panel_width-1], curses.A_DIM)
                except curses.error:
                    pass

                # Display content with scroll offset
                for i in range(visible_height):
                    content_idx = i + self.preview_scroll
                    if content_idx >= len(content):
                        break

                    y_pos = 5 + i
                    line = content[content_idx]
                    # Truncate line to fit panel
                    display_line = line[:panel_width-2]
                    try:
                        stdscr.addstr(y_pos, panel_x, display_line)
                    except curses.error:
                        pass

                # Draw scroll indicator if needed
                if len(content) > visible_height:
                    scroll_pos = int((self.preview_scroll / max_scroll) * (visible_height - 1)) if max_scroll > 0 else 0
                    try:
                        for i in range(visible_height):
                            y_pos = 5 + i
                            if i == scroll_pos:
                                stdscr.addstr(y_pos, width - 1, "█")
                            else:
                                stdscr.addstr(y_pos, width - 1, "│")
                    except curses.error:
                        pass
            else:
                # No info file found
                try:
                    stdscr.addstr(5, panel_x, "No NFO available", curses.A_DIM)
                    stdscr.addstr(7, panel_x, "No readme or info file found", curses.A_DIM)
                    stdscr.addstr(8, panel_x, "in the executable's directory.", curses.A_DIM)
                except curses.error:
                    pass

    def draw_preview_fullscreen(self, stdscr, height: int, width: int):
        """Draw the preview panel in full-screen mode."""
        # Get current executable
        if not (0 <= self.current_index < len(self.executables)):
            return

        exe = self.executables[self.current_index]
        info_file = self.find_info_file(exe)

        if info_file:
            # Read content
            content = self.read_info_file(info_file, max_lines=1000)  # Allow more lines in full screen
            visible_height = height - 5  # Account for header, border, info line, footer

            # Calculate scroll limits
            max_scroll = max(0, len(content) - visible_height)
            self.preview_scroll = max(0, min(self.preview_scroll, max_scroll))

            # Draw border and title
            try:
                stdscr.addstr(2, 0, "═" * width, curses.A_BOLD)

                # File info line
                try:
                    rel_path = exe.relative_to(self.base_dir)
                except ValueError:
                    rel_path = exe

                info_line = f" File: {info_file.name} | Executable: {rel_path} "
                if len(content) > visible_height:
                    scroll_info = f" | Lines: {self.preview_scroll + 1}-{min(self.preview_scroll + visible_height, len(content))}/{len(content)} "
                    info_line += scroll_info

                stdscr.addstr(2, 2, info_line[:width-4], curses.A_BOLD | curses.color_pair(3))
                stdscr.addstr(3, 0, "─" * width)
            except curses.error:
                pass

            # Display content with scroll offset
            for i in range(visible_height):
                content_idx = i + self.preview_scroll
                if content_idx >= len(content):
                    break

                y_pos = 4 + i
                line = content[content_idx]

                # Don't truncate - show full width
                display_line = line[:width-1]
                try:
                    stdscr.addstr(y_pos, 0, display_line)
                except curses.error:
                    pass

            # Draw scroll indicator if needed
            if len(content) > visible_height and width > 1:
                scroll_pos = int((self.preview_scroll / max_scroll) * (visible_height - 1)) if max_scroll > 0 else 0
                try:
                    for i in range(visible_height):
                        y_pos = 4 + i
                        if i == scroll_pos:
                            stdscr.addstr(y_pos, width - 1, "█", curses.A_BOLD)
                        else:
                            stdscr.addstr(y_pos, width - 1, "│", curses.A_DIM)
                except curses.error:
                    pass
        else:
            # No info file found - show message
            try:
                stdscr.addstr(2, 0, "═" * width, curses.A_BOLD)
                stdscr.addstr(2, 2, " No Preview Available ", curses.A_BOLD)
                stdscr.addstr(3, 0, "─" * width)

                try:
                    rel_path = exe.relative_to(self.base_dir)
                except ValueError:
                    rel_path = exe

                stdscr.addstr(5, 2, f"Executable: {rel_path}", curses.A_DIM)
                stdscr.addstr(7, 2, "No NFO, TXT, or README file found", curses.A_DIM)
                stdscr.addstr(8, 2, "in the executable's directory.", curses.A_DIM)
                stdscr.addstr(10, 2, "Press ← (left arrow) to return to list", curses.A_DIM)
            except curses.error:
                pass

    def draw_footer(self, stdscr, height: int, width: int):
        """Draw the footer with current selection info."""
        if 0 <= self.current_index < len(self.executables):
            exe = self.executables[self.current_index]

            if self.active_pane == 'preview':
                footer = f"[PREVIEW MODE] {exe.name} | Press ← to return to list | q: Quit"
            else:
                footer = f"Selected: {exe.name}"

            try:
                stdscr.addstr(height - 1, 0, footer[:width], curses.A_REVERSE)
            except curses.error:
                pass

    def run(self, stdscr) -> Optional[Path]:
        """
        Run the interactive selector.
        Returns the selected executable or None if cancelled.
        """
        # Initialize curses
        curses.curs_set(0)  # Hide cursor
        stdscr.clear()

        # Initialize colors if available
        if curses.has_colors():
            curses.init_pair(1, curses.COLOR_BLACK, curses.COLOR_WHITE)
            curses.init_pair(2, curses.COLOR_GREEN, curses.COLOR_BLACK)
            curses.init_pair(3, curses.COLOR_CYAN, curses.COLOR_BLACK)

        while True:
            stdscr.clear()
            height, width = stdscr.getmaxyx()

            # Draw all components
            self.draw_header(stdscr, width)

            if self.active_pane == 'preview':
                # Full-screen preview mode
                self.draw_preview_fullscreen(stdscr, height, width)
            else:
                # Split-screen mode (list + preview)
                list_width = min(60, width // 2)
                self.draw_executable_list(stdscr, height, width, list_width)
                self.draw_preview_panel(stdscr, height, width, list_width)

            self.draw_footer(stdscr, height, width)

            stdscr.refresh()

            # Handle input
            try:
                key = stdscr.getch()
            except KeyboardInterrupt:
                return None

            if key == curses.KEY_LEFT:
                # Move to list pane
                self.active_pane = 'list'
                self.preview_scroll = 0  # Reset preview scroll when leaving

            elif key == curses.KEY_RIGHT:
                # Move to preview pane (if there's a preview)
                if 0 <= self.current_index < len(self.executables):
                    exe = self.executables[self.current_index]
                    if self.find_info_file(exe):
                        self.active_pane = 'preview'

            elif key == curses.KEY_UP:
                if self.active_pane == 'list':
                    # Navigate executable list
                    if self.current_index > 0:
                        self.current_index -= 1
                        self.preview_scroll = 0  # Reset preview scroll when changing selection
                else:
                    # Scroll preview up
                    if self.preview_scroll > 0:
                        self.preview_scroll -= 1

            elif key == curses.KEY_DOWN:
                if self.active_pane == 'list':
                    # Navigate executable list
                    if self.current_index < len(self.executables) - 1:
                        self.current_index += 1
                        self.preview_scroll = 0  # Reset preview scroll when changing selection
                else:
                    # Scroll preview down
                    self.preview_scroll += 1

            elif key == curses.KEY_PPAGE:  # Page Up
                if self.active_pane == 'list':
                    self.current_index = max(0, self.current_index - 10)
                    self.preview_scroll = 0
                else:
                    # Scroll preview up by 10 lines
                    self.preview_scroll = max(0, self.preview_scroll - 10)

            elif key == curses.KEY_NPAGE:  # Page Down
                if self.active_pane == 'list':
                    self.current_index = min(len(self.executables) - 1, self.current_index + 10)
                    self.preview_scroll = 0
                else:
                    # Scroll preview down by 10 lines
                    self.preview_scroll += 10

            elif key == curses.KEY_HOME:
                if self.active_pane == 'list':
                    self.current_index = 0
                    self.preview_scroll = 0
                else:
                    # Go to top of preview
                    self.preview_scroll = 0

            elif key == curses.KEY_END:
                if self.active_pane == 'list':
                    self.current_index = len(self.executables) - 1
                    self.preview_scroll = 0
                else:
                    # Go to bottom of preview (set to large number, will be clamped)
                    self.preview_scroll = 999999

            elif key in [ord('\n'), ord('\r'), curses.KEY_ENTER]:
                # Enter pressed - record execution and return selected executable
                selected = self.executables[self.current_index]
                self.tracker.record_execution(str(selected.absolute()))
                return selected

            elif key in [ord('q'), ord('Q'), 27]:  # q or ESC
                return None


def select_executable_interactive(executables: List[Path], base_dir: Path) -> Optional[Path]:
    """
    Show interactive selector for executables.
    Returns selected executable or None if cancelled.
    """
    if not executables:
        return None

    selector = InteractiveSelector(executables, base_dir)
    try:
        return curses.wrapper(selector.run)
    except Exception as e:
        print(f"\n✗ Error in interactive selector: {e}")
        print("Falling back to simple selection...")
        return None
