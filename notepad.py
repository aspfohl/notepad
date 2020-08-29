"""
This is windows Notepad implemented in python
"""
__version__ = "0.0.1"

from functools import wraps, partial
from pathlib import Path
import inspect
import logging
import sys
import tkinter as tk
from tkinter import ttk
import tkinter.filedialog as tkfd
import tkinter.messagebox as tkm


APP_NAME = "PyNotepad"
LOG = logging.getLogger(__name__)


DEFAULT_WINDOW_WIDTH = 600
DEFAULT_WINDOW_HEIGHT = 400
DEFAULT_WINDOW_ICON = "snake.ico"
DEFAULT_UNNAMED_TITLE = "Untitled"

DEFAULT_FILE_EXTENSION = ".txt"
SUPPORTED_FILE_TYPES = [
    ("All Files", "*.*"),
    ("Text Documents", f"*.{DEFAULT_FILE_EXTENSION}"),
]

FILE_DIALOG_DEFAULT_ARGS = {
    "defaultextension": DEFAULT_FILE_EXTENSION,
    "filetypes": SUPPORTED_FILE_TYPES,
}

MENU_LAYOUT = {
    "File": ("New", "Open", "Save", "Save As", "Exit"),
    "Edit": ("Undo", "Copy", "Cut", "Paste", "Select All"),
    "View": ("Status Bar",),
    "Help": ("About",),
}


def _logger(func, level):
    @wraps(func)
    def wrapper(*args, **kwargs):
        level("Entering method %s", func.__name__)
        res = func(*args, **kwargs)
        level("Exiting method %s", func.__name__)
        return res

    return wrapper


log_info = partial(_logger, level=LOG.info)
log_debug = partial(_logger, level=LOG.debug)
log_action = log_info  # could have something more specific for actions


def get_title(current: str = DEFAULT_UNNAMED_TITLE):
    return f"{current} - {APP_NAME}"


class WindowDimension:
    def __init__(
        self, *, width: int = DEFAULT_WINDOW_WIDTH, height: int = DEFAULT_WINDOW_HEIGHT
    ):
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
    _is_status_bar_visible = tk.BooleanVar()

    _menus = {}
    _file = None

    # todo; move to stringvars, make dynamic
    status_location = "Ln 1, Col 1"
    status_zoom = "100%"
    status_platform = sys.platform
    status_encoding = "UTF-8"

    @log_info
    def __init__(self, window_dimension: WindowDimension = WindowDimension()):
        self._set_window_size(window_dimension)
        self._create_menu_bar()
        self._create_text()
        self._create_scrollbar()
        self._create_status_bar()

    @log_debug
    def _set_window_size(self, window_dimension: WindowDimension):
        geometry = window_dimension.get_geometry(
            screen_width=self._root.winfo_screenwidth(),
            screen_height=self._root.winfo_screenheight(),
        )
        self._root.geometry(geometry)

    @log_debug
    def _create_menu_bar(self):
        self._menu_bar = tk.Menu(self._root)
        action_menu = self._collectactions()
        for menu_label, options in MENU_LAYOUT.items():
            _menu = tk.Menu(self._menu_bar, tearoff=0)

            for option_label in options:
                lookup_key = (
                    f"{menu_label.lower()}_{option_label.lower().replace(' ','_')}"
                )
                command = action_menu.get(lookup_key, self.action_not_implemented)

                # Todo: less hardcoding
                if lookup_key == "view_status_bar":
                    _menu.add_checkbutton(
                        label=option_label,
                        command=command,
                        onvalue=True,
                        offvalue=False,
                        variable=self._is_status_bar_visible,
                    )
                else:
                    _menu.add_command(label=option_label, command=command)

            self._menu_bar.add_cascade(label=menu_label, menu=_menu)
            self._menus[menu_label] = _menu  # for accessibility later

        self._root.config(menu=self._menu_bar)

    @log_debug
    def _create_status_bar(self):
        self._status_bar = tk.Frame(self._text_area)

        for var, width in (
            (self.status_encoding, 50),
            (self.status_platform, 25),
            (self.status_zoom, 15),
            (self.status_location, 75),
        ):

            padx = width - len(var)
            tk.Label(self._status_bar, text=var, bd=1).pack(side=tk.RIGHT, padx=padx)
            ttk.Separator(self._status_bar, orient=tk.VERTICAL).pack(
                side=tk.RIGHT, fill=tk.BOTH
            )

        self._status_bar.pack(side=tk.BOTTOM, fill=tk.X)
        self._is_status_bar_visible.set(True)

    @log_debug
    def _create_text(self):
        self._root.grid_rowconfigure(0, weight=1)
        self._root.grid_columnconfigure(0, weight=1)
        self._text_area = tk.Text(self._root)
        self._text_area.grid(sticky=tk.N + tk.E + tk.S + tk.W)

    @log_debug
    def _create_scrollbar(self):
        scroll_bar = tk.Scrollbar(self._text_area)
        scroll_bar.pack(side=tk.RIGHT, fill=tk.Y)
        scroll_bar.config(command=self._text_area.yview)
        self._text_area.config(yscrollcommand=scroll_bar.set)

    def run(self):
        LOG.info("Running app")
        self._root.mainloop()

    @log_debug
    def _collectactions(self):
        actions = {
            name.replace(self.__prefix_action_method, ""): getattr(self, name)
            for name in dir(self)
            if name.startswith(self.__prefix_action_method)
            and callable(getattr(self, name))
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

    @log_debug
    def _helper_would_you_like_to_save(self, endaction):
        window = tk.Toplevel()
        tk.Label(
            window,
            text=f'Would you like to save changes to "{self._file or DEFAULT_UNNAMED_TITLE}"',
        ).pack(fill="x", padx=50, pady=5)

        def cancel():
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

    @log_action
    def action_file_new(self):
        def new():
            self._root.title(get_title())
            self._file = None
            self._text_area.delete(1.0, tk.END)

        self._helper_would_you_like_to_save(new)

    @log_action
    def action_file_open(self):
        self._file = Path(tkfd.askopenfilename(**FILE_DIALOG_DEFAULT_ARGS))

        if not self._file:
            return

        self._text_area.delete(1.0, tk.END)
        with open(self._file, "r") as f:
            self._text_area.insert(1.0, f.read())

        self._root.title(get_title(self._file.name))

    @log_debug
    def _helper_save_text(self, file: Path):
        if not file:
            return

        with open(file, "w") as f:
            f.write(self._text_area.get(1.0, tk.END))

        self._root.title(get_title(file.name))

    @log_debug
    def _helper_ask_save_filename(self):
        return Path(
            tkfd.asksaveasfilename(
                initialfile=f"{DEFAULT_UNNAMED_TITLE}.{DEFAULT_FILE_EXTENSION}",
                **FILE_DIALOG_DEFAULT_ARGS,
            )
        )

    @log_action
    def action_file_save(
        self,
    ):
        if not self._file:
            self._file = self._helper_ask_save_filename()

        self._helper_save_text(self._file)

    @log_action
    def action_file_save_as(self):
        self._file = self._helper_ask_save_filename()
        self._helper_save_text(self._file)

    @log_action
    def action_file_exit(self):
        def exit():
            self._root.destroy()

        self._helper_would_you_like_to_save(exit)

    @log_action
    def action_edit_undo(self):
        self._text_area.event_generate("<<Undo>>")

    @log_action
    def action_edit_cut(self):
        self._text_area.event_generate("<<Cut>>")

    @log_action
    def action_edit_copy(self):
        self._text_area.event_generate("<<Copy>>")

    @log_action
    def action_edit_paste(self):
        self._text_area.event_generate("<<Paste>>")

    @log_action
    def action_edit_select_all(self):
        self._text_area.event_generate("<<SelectAll>>")

    @log_action
    def action_view_status_bar(self):
        if self._is_status_bar_visible:
            self._status_bar.pack_forget()
        else:
            self._status_bar.pack(side=tk.BOTTOM, fill=tk.X)

        self._is_status_bar_visible = not self._is_status_bar_visible

    @log_action
    def action_help_about(self):
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
    configure_logging(2)
    notepad = Notepad()
    notepad.run()
