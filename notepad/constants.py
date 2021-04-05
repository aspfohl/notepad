"""
Notepad Constants
"""

APP_NAME = "PyNotepad"

DEFAULT_WINDOW_WIDTH = 600
DEFAULT_WINDOW_HEIGHT = 400
DEFAULT_WINDOW_ICON = "resources/snake.ico"
DEFAULT_UNNAMED_TITLE = "Untitled"
DEFAULT_FILE_EXTENSION = ".txt"

SUPPORTED_FILE_TYPES = [("All Files", "*.*"), ("Text Documents", f"*.{DEFAULT_FILE_EXTENSION}")]

FILE_DIALOG_DEFAULT_ARGS = {
    "defaultextension": DEFAULT_FILE_EXTENSION,
    "filetypes": SUPPORTED_FILE_TYPES,
}

MENU_LAYOUT = {
    "File": ("New", "New Window", "Open", "Save", "Save As", "Exit"),
    "Edit": ("Undo", "Cut", "Copy", "Paste", "Delete", "Select All"),
    "View": ("Status Bar",),
    "Format": ("Theme", "Wrap Words"),
    "Help": ("View Help", "About"),
}
