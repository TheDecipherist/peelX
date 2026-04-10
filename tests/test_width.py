#!/usr/bin/env python3
"""
Test script to debug width issues in curses.
This is an interactive diagnostic tool — not a pytest test.
Run directly: python tests/test_width.py
"""
import curses
import pytest


# Skip in automated test runs — requires interactive terminal
pytestmark = pytest.mark.skip(reason="Interactive curses test — run directly with python")


def test_width(stdscr):
    curses.curs_set(0)
    stdscr.clear()

    height, width = stdscr.getmaxyx()

    stdscr.addstr(0, 0, f"Terminal dimensions: height={height}, width={width}")
    stdscr.addstr(2, 0, "Testing full width lines:")

    stdscr.addstr(4, 0, "=" * width)
    stdscr.addstr(5, 0, f"This line has {width} '=' characters")

    stdscr.addstr(7, 0, "=" * (width - 1))
    stdscr.addstr(8, 0, f"This line has {width-1} '=' characters")

    test_content = "A" * 200
    stdscr.addstr(10, 0, f"Content truncated to width-1: {len(test_content[:width-1])} chars")
    stdscr.addstr(11, 0, test_content[:width-1])

    stdscr.addstr(13, 0, f"Content truncated to width-2: {len(test_content[:width-2])} chars")
    stdscr.addstr(14, 0, test_content[:width-2])

    stdscr.addstr(height-1, 0, "Press any key to exit")
    stdscr.refresh()
    stdscr.getch()


if __name__ == "__main__":
    curses.wrapper(test_width)
