"""
This is windows Notepad implemented in python
"""
__version__ = "0.0.1"

import os

import tkinter as tk
import tkinter.messagebox as tkm
import tkinter.filedialog as tkfd

from functools import partialmethod

APP_NAME = "Notepad"

DEFAULT_WINDOW_WIDTH = 600
DEFAULT_WINDOW_HEIGHT = 400
DEFAULT_WINDOW_ICON = "snake.png"
DEFAULT_UNNAMED_TITLE = "Untitled"

MENU_LAYOUT = {
    "File": ("New", "Open", "Save", "Exit"),
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
                lookup_key = f"{menu_label.lower()}_{option_label.lower()}"
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

    _prefix_action_method = "_action_"

    """
    Use `{PREFIX_ACTION_METHOD}{menu_bar_name}_{command}` naming convention to mark menu option commands
    (case insensitive)
    """

    def action_not_implemented(self):
        print("Warning: This does nothing!")
        # raise NotImplementedError()

    def _action_file_new(self):
        window = tk.Toplevel()

        label = tk.Label(
            window,
            text=f'Would you like to save changes to "{self._file or DEFAULT_UNNAMED_TITLE}"',
        )
        label.pack(fill="x", padx=50, pady=5)

        def cancel():
            window.destroy()

        def new():
            self._root.title(get_title())
            self._file = None
            self._text_area.delete(1.0, tk.END)

        def dont_save():
            cancel()
            new()

        def save():
            cancel()
            self._action_file_save()
            new()

        tk.Button(window, text="Don't Save", command=dont_save).pack(side=tk.LEFT)
        tk.Button(window, text="Save", command=save).pack(side=tk.LEFT)
        tk.Button(window, text="Cancel", command=cancel).pack(side=tk.LEFT)

    def _action_file_open(self):
        # todo: refactor, use pathlib
        self._file = tkfd.askopenfilename(
            defaultextension=".txt", filetypes=[("All Files", "*.*"), ("Text Documents", "*.txt")]
        )

        if self._file == "":

            # no file to open
            self._file = None
        else:

            # Try to open the file
            # set the window title
            self._root.title(get_title(os.path.basename(self._file)))
            self._text_area.delete(1.0, tk.END)

            file = open(self._file, "r")

            self._text_area.insert(1.0, file.read())

            file.close()

    def _action_file_save(self):
        # todo: refactor, use pathlib

        if self._file == None:
            # Save as new file
            self._file = tkfd.asksaveasfilename(
                initialfile=f"{DEFAULT_UNNAMED_TITLE}.txt",
                defaultextension=".txt",
                filetypes=[("All Files", "*.*"), ("Text Documents", "*.txt")],
            )

            if self._file == "":
                self._file = None
            else:

                # Try to save the file
                file = open(self._file, "w")
                file.write(self._text_area.get(1.0, tk.END))
                file.close()

                # Change the window title
                self._root.title(get_title(os.path.basename(self._file)))

        else:
            file = open(self._file, "w")
            file.write(self._text_area.get(1.0, tk.END))
            file.close()

    def _action_file_exit(self):
        self._root.destroy()

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

