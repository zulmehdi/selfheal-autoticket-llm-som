"""Readable, agent-labelled terminal output without extra dependencies."""

import os
import re
import shutil
import sys
import textwrap


COLORS = {
    "System": "90",           # Gray
    "Incident Reporter": "96", # Cyan
    "Incident Responder": "94", # Blue
    "Architect": "95",        # Magenta
    "Engineer": "93",         # Yellow
    "Tester": "92",           # Green
}


def configure_console(no_color=False):
    global _use_color
    _use_color = not no_color and "NO_COLOR" not in os.environ and (
        sys.stdout.isatty() or bool(os.getenv("FORCE_COLOR"))
    )
    if _use_color and os.name == "nt" and sys.stdout.isatty():
        # Enable ANSI colors in Windows console hosts.
        import ctypes
        from ctypes import wintypes

        kernel = ctypes.WinDLL("kernel32", use_last_error=True)
        kernel.GetStdHandle.argtypes = [wintypes.DWORD]
        kernel.GetStdHandle.restype = wintypes.HANDLE
        handle = kernel.GetStdHandle(-11 & 0xFFFFFFFF)
        mode = wintypes.DWORD()
        if kernel.GetConsoleMode(handle, ctypes.byref(mode)):
            kernel.SetConsoleMode(handle, mode.value | 0x0004)


_use_color = False
configure_console()


def _clean(value):
    # Keep terminal control sequences from model output out of the display.
    return re.sub(r"[\x00-\x08\x0b-\x1f\x7f]", "", str(value))


def _label(key):
    if str(key).startswith("INC-"):
        return str(key)
    return " ".join("ID" if word.lower() == "id" else word for word in
                    str(key).replace("_", " ").capitalize().split())


def _lines(value, indent=2):
    prefix = " " * indent
    if isinstance(value, dict):
        for key, item in value.items():
            label = _label(key)
            if isinstance(item, (dict, list)):
                yield prefix + label + ":"
                yield from _lines(item, indent + 2)
            else:
                yield prefix + label + ": " + ("Yes" if item is True else "No" if item is False else _clean(item))
    elif isinstance(value, list):
        for index, item in enumerate(value, 1):
            if isinstance(item, dict) and item.get("type") == "text":
                yield from _lines(item.get("text", ""), indent)
            elif isinstance(item, (dict, list)):
                yield prefix + f"{index}."
                yield from _lines(item, indent + 2)
            else:
                yield prefix + f"{index}. " + _clean(item)
    else:
        for line in _clean(value).splitlines():
            yield prefix + line


def emit(agent, title, content=None):
    """Print a colored [Agent Name] header and indented, wrapped content."""
    heading = f"[{agent}] {_clean(title)}"
    if _use_color:
        heading = f"\033[1;{COLORS.get(agent, '97')}m{heading}\033[0m"
    print("\n" + heading, flush=True)
    width = max(40, min(shutil.get_terminal_size((100, 24)).columns, 110))
    if content is not None:
        for line in _lines(content):
            indent = len(line) - len(line.lstrip())
            print(textwrap.fill(
                line, width=width, subsequent_indent=" " * (indent + 2),
                break_long_words=False, break_on_hyphens=False,
            ) if line.strip() else "")
