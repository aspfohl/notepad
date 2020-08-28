"""
This is windows Notepad implemented in python
"""
__version__ = "0.0.1"

import os

from pathlib import Path

import tkinter as tk
import tkinter.messagebox as tkm
import tkinter.filedialog as tkfd

from functools import partialmethod

APP_NAME = "Notepad"

DEFAULT_WINDOW_WIDTH = 600
DEFAULT_WINDOW_HEIGHT = 400
DEFAULT_WINDOW_ICON = "snake.png"
DEFAULT_UNNAMED_TITLE = "Untitled"

DEFAULT_FILE_EXTENSION = ".txt"
SUPPORTED_FILE_TYPES = [("All Files", "*.*"), ("Text Documents", f"*.{DEFAULT_FILE_EXTENSION}")]

FILE_DIALOG_DEFAULT_ARGS = {
    "defaultextension": DEFAULT_FILE_EXTENSION,
    "filetypes": SUPPORTED_FILE_TYPES,
}

MENU_LAYOUT = {
    "File": ("New", "Open", "Save", "Save As", "Exit"),
    "Edit": ("Copy", "Cut", "Paste"),
    "Help": ("About",),
}


def get_title(current: str = DEFAULT_UNNAMED_TITLE):
    return f"{current} - {APP_NAME}"


class WindowDimension:
    def __init__(self, *, width: int = DEFAULT_WINDOW_WIDTH, height: int = DEFAULT_WINDOW_HEIGHT):
        self.width = width
        self.height = height

    def left_alignment(self, *, screen_width: int) -> int:
        return (screen_width / 2) - (self.width / 2)

    def top_alignment(self, *, screen_height: int) -> int:
        return (screen_height / 2) - (self.height / 2)

    def get_geometry(self, *, screen_width: int, screen_height: int) -> str:
        left = self.left_alignment(screen_width=screen_width)
        top = self.top_alignment(screen_height=screen_height)
        return f"{self.width}x{self.height}+{left:.0f}+{top:.0f}"


class Notepad:

    _root = tk.Tk()
    _root.wm_iconbitmap(DEFAULT_WINDOW_ICON)
    _root.title(get_title())

    _menus = {}
    _file = None

    def __init__(self, window_dimension: WindowDimension = WindowDimension()):
        self.set_window_size(window_dimension)
        self.create_menu_bar()
        self.create_text()
        self.create_scrollbar()

    def set_window_size(self, window_dimension: WindowDimension):
        geometry = window_dimension.get_geometry(
            screen_width=self._root.winfo_screenwidth(),
            screen_height=self._root.winfo_screenheight(),
        )
        self._root.geometry(geometry)

    def create_menu_bar(self):
        self._menu_bar = tk.Menu(self._root)
        action_menu = self._collect_actions()
        for menu_label, options in MENU_LAYOUT.items():
            _menu = tk.Menu(self._menu_bar, tearoff=0)

            for option_label in options:
                lookup_key = f"{menu_label.lower()}_{option_label.lower().replace(' ','_')}"
                command = action_menu.get(lookup_key, self.action_not_implemented)
                _menu.add_command(label=option_label, command=command)

            self._menu_bar.add_cascade(label=menu_label, menu=_menu)
            self._menus[menu_label] = _menu  # for accessibility later

        self._root.config(menu=self._menu_bar)

    def create_text(self):
        self._root.grid_rowconfigure(0, weight=1)
        self._root.grid_columnconfigure(0, weight=1)
        self._text_area = tk.Text(self._root)
        self._text_area.grid(sticky=tk.N + tk.E + tk.S + tk.W)

    def create_scrollbar(self):
        scroll_bar = tk.Scrollbar(self._text_area)
        scroll_bar.pack(side=tk.RIGHT, fill=tk.Y)
        scroll_bar.config(command=self._text_area.yview)
        self._text_area.config(yscrollcommand=scroll_bar.set)

    def run(self):
        self._root.mainloop()

    def _collect_actions(self):
        return {
            name.replace(self._prefix_action_method, ""): getattr(self, name)
            for name in dir(self)
            if name.startswith(self._prefix_action_method) and callable(getattr(self, name))
        }

    def action_not_implemented(self):
        print("Warning: This does nothing!")
        # raise NotImplementedError()

    _prefix_action_method = "_action_"

    """
    Use `{PREFIX_ACTION_METHOD}{menu_bar_name}_{command}` naming convention to mark menu option commands
    (case insensitive)
    """

    def _helper_would_you_like_to_save(self, end_action):
        window = tk.Toplevel()
        tk.Label(
            window,
            text=f'Would you like to save changes to "{self._file or DEFAULT_UNNAMED_TITLE}"',
        ).pack(fill="x", padx=50, pady=5)

        def cancel():
            window.destroy()

        def dont_save():
            cancel()
            end_action()

        def save():
            cancel()
            self._action_file_save()
            end_action()

        tk.Button(window, text="Don't Save", command=dont_save).pack(side=tk.LEFT)
        tk.Button(window, text="Save", command=save).pack(side=tk.LEFT)
        tk.Button(window, text="Cancel", command=cancel).pack(side=tk.LEFT)

    def _action_file_new(self):
        def new():
            self._root.title(get_title())
            self._file = None
            self._text_area.delete(1.0, tk.END)

        self._helper_would_you_like_to_save(new)

    def _action_file_open(self):
        self._file = Path(tkfd.askopenfilename(**FILE_DIALOG_DEFAULT_ARGS))

        if not self._file:
            return

        self._text_area.delete(1.0, tk.END)
        with open(self._file, "r") as f:
            self._text_area.insert(1.0, f.read())

        self._root.title(get_title(self._file.name))

    def _helper_save_text(self, file: Path):
        if not file:
            return

        with open(file, "w") as f:
            f.write(self._text_area.get(1.0, tk.END))

        self._root.title(get_title(file.name))

    def _helper_ask_save_filename(self):
        return Path(
            tkfd.asksaveasfilename(
                initialfile=f"{DEFAULT_UNNAMED_TITLE}.{DEFAULT_FILE_EXTENSION}",
                **FILE_DIALOG_DEFAULT_ARGS,
            )
        )

    def _action_file_save(self,):
        if not self._file:
            self._file = self._helper_ask_save_filename()

        self._helper_save_text(self._file)

    def _action_file_save_as(self):
        self._file = self._helper_ask_save_filename()
        self._helper_save_text(self._file)

    def _action_file_exit(self):
        def exit():
            self._root.destroy()

        self._helper_would_you_like_to_save(exit)

    def _action_edit_cut(self):
        self._text_area.event_generate("<<Cut>>")

    def _action_edit_copy(self):
        self._text_area.event_generate("<<Copy>>")

    def _action_edit_paste(self):
        self._text_area.event_generate("<<Paste>>")

    def _action_help_about(self):
        system_info = f"""App name: {APP_NAME}
Version: {__version__}
"""
        tkm.showinfo(APP_NAME, system_info + __doc__)


# Run main application
notepad = Notepad()
notepad.run()

