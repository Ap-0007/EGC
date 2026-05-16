import os
import platform
import subprocess
from urllib.parse import quote
from urllib.request import pathname2url

def normalize_path(path: str) -> str:
    """Normalize path separators for the current OS."""
    return os.path.normpath(path)

def to_portable_path(path: str) -> str:
    """Convert path to forward-slash format for JSON/storage."""
    return path.replace(os.sep, '/')

def from_portable_path(path: str) -> str:
    """Convert portable forward-slash path to native OS path."""
    return os.path.normpath(path.replace('/', os.sep))

def get_file_uri(path: str) -> str:
    """Generate a safe file:// URI for hyperlinks."""
    abs_path = os.path.abspath(path)
    return 'file://' + pathname2url(abs_path)

def open_in_explorer(path: str):
    """Open a path in the system file explorer (cross-platform)."""
    if not os.path.exists(path):
        return False
        
    system = platform.system()
    try:
        if system == 'Windows':
            os.startfile(path)
        elif system == 'Darwin':
            subprocess.Popen(['open', path])
        else:
            subprocess.Popen(['xdg-open', path])
        return True
    except Exception:
        return False
