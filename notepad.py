"""
This is windows Notepad implemented in python
"""
__version__ = "0.0.1"

import os

from pathlib import Path

import tkinter as tk
import tkinter.messagebox as tkm
import tkinter.filedialog as tkfd

import logging

APP_NAME = "Notepad"
LOG = logging.getLogger(__name__)


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
    "Edit": ("Undo", "Copy", "Cut", "Paste", "Select All"),
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
        LOG.info("Initializing Notepad")
        self._set_window_size(window_dimension)
        self._create_menu_bar()
        self._create_text()
        self._create_scrollbar()

    def _set_window_size(self, window_dimension: WindowDimension):
        geometry = window_dimension.get_geometry(
            screen_width=self._root.winfo_screenwidth(),
            screen_height=self._root.winfo_screenheight(),
        )
        self._root.geometry(geometry)

    def _create_menu_bar(self):
        self._menu_bar = tk.Menu(self._root)
        action_menu = self._collectactions()
        for menu_label, options in MENU_LAYOUT.items():
            _menu = tk.Menu(self._menu_bar, tearoff=0)

            for option_label in options:
                lookup_key = f"{menu_label.lower()}_{option_label.lower().replace(' ','_')}"
                command = action_menu.get(lookup_key, self.action_not_implemented)
                _menu.add_command(label=option_label, command=command)

            self._menu_bar.add_cascade(label=menu_label, menu=_menu)
            self._menus[menu_label] = _menu  # for accessibility later

        self._root.config(menu=self._menu_bar)

    def _create_text(self):
        self._root.grid_rowconfigure(0, weight=1)
        self._root.grid_columnconfigure(0, weight=1)
        self._text_area = tk.Text(self._root)
        self._text_area.grid(sticky=tk.N + tk.E + tk.S + tk.W)

    def _create_scrollbar(self):
        scroll_bar = tk.Scrollbar(self._text_area)
        scroll_bar.pack(side=tk.RIGHT, fill=tk.Y)
        scroll_bar.config(command=self._text_area.yview)
        self._text_area.config(yscrollcommand=scroll_bar.set)

    def run(self):
        LOG.info("Running app")
        self._root.mainloop()

    def _collectactions(self):
        actions = {
            name.replace(self.__prefix_action_method, ""): getattr(self, name)
            for name in dir(self)
            if name.startswith(self.__prefix_action_method) and callable(getattr(self, name))
        }
        LOG.debug("Found %s actions: %s", len(actions.keys()), list(actions.keys()))
        return actions

    def action_not_implemented(self):
        LOG.warning("Warning: This does nothing!")
        # raise NotImplementedError()

    __prefix_action_method = "action_"

    """
    Use `{__prefix_action_method}{menu_bar_name}_{command}` naming convention to mark menu option commands
    (case insensitive)
    """

    def _helper_would_you_like_to_save(self, endaction):
        LOG.debug("Inside 'would you like to save'")
        window = tk.Toplevel()
        tk.Label(
            window,
            text=f'Would you like to save changes to "{self._file or DEFAULT_UNNAMED_TITLE}"',
        ).pack(fill="x", padx=50, pady=5)

        def cancel():
            LOG.debug("You hit cancel")
            window.destroy()

        def dont_save():
            LOG.debug("You hit 'don't save'")
            cancel()
            endaction()

        def save():
            LOG.debug("You hit 'save'")
            cancel()
            self.action_file_save()
            endaction()

        tk.Button(window, text="Don't Save", command=dont_save).pack(side=tk.LEFT)
        tk.Button(window, text="Save", command=save).pack(side=tk.LEFT)
        tk.Button(window, text="Cancel", command=cancel).pack(side=tk.LEFT)

    def action_file_new(self):
        LOG.info("Menu: new file")
        def new():
            self._root.title(get_title())
            self._file = None
            self._text_area.delete(1.0, tk.END)

        self._helper_would_you_like_to_save(new)

    def action_file_open(self):
        LOG.info("Menu: open file")
        self._file = Path(tkfd.askopenfilename(**FILE_DIALOG_DEFAULT_ARGS))

        if not self._file:
            return

        self._text_area.delete(1.0, tk.END)
        with open(self._file, "r") as f:
            self._text_area.insert(1.0, f.read())

        self._root.title(get_title(self._file.name))

    def _helper_save_text(self, file: Path):
        LOG.debug("Saving text to file %s", str(file))
        if not file:
            return

        with open(file, "w") as f:
            f.write(self._text_area.get(1.0, tk.END))

        self._root.title(get_title(file.name))

    def _helper_ask_save_filename(self):
        LOG.debug("Asking save filename")
        return Path(
            tkfd.asksaveasfilename(
                initialfile=f"{DEFAULT_UNNAMED_TITLE}.{DEFAULT_FILE_EXTENSION}",
                **FILE_DIALOG_DEFAULT_ARGS,
            )
        )

    def action_file_save(self,):
        LOG.info("Menu: save file")
        if not self._file:
            self._file = self._helper_ask_save_filename()

        self._helper_save_text(self._file)

    def action_file_save_as(self):
        LOG.info("Menu: save file as")
        self._file = self._helper_ask_save_filename()
        self._helper_save_text(self._file)

    def action_file_exit(self):
        LOG.info("Menu: file exit")
        def exit():
            self._root.destroy()

        self._helper_would_you_like_to_save(exit)

    def action_edit_undo(self):
        LOG.info("Menu: edit undo")
        self._text_area.event_generate("<<Undo>>")

    def action_edit_cut(self):
        LOG.info("Menu: edit cut")
        self._text_area.event_generate("<<Cut>>")

    def action_edit_copy(self):
        LOG.info("Menu: edit copy")
        self._text_area.event_generate("<<Copy>>")

    def action_edit_paste(self):
        LOG.info("Menu: edit paste")
        self._text_area.event_generate("<<Paste>>")

    def action_edit_select_all(self):
        LOG.info("Menu: edit select all")
        self._text_area.event_generate("<<SelectAll>>")

    def action_help_about(self):
        LOG.info("Menu: help about")
        system_info = f"""App name: {APP_NAME}
Version: {__version__}
"""
        tkm.showinfo(APP_NAME, system_info + __doc__)


def configure_logging(verbose: int = 1) -> bool:
    level = logging.WARN
    if verbose == 1:
        level = logging.INFO
    elif verbose >= 2:
        level = logging.DEBUG

    logging.basicConfig(level=level)

 
if __name__ == "__main__":
    configure_logging()
    notepad = Notepad()
    notepad.run()

