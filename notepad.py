"""
This is windows Notepad implemented in python
"""
__version__ = "0.0.1"

from functools import wraps, partial
from pathlib import Path
from tkinter import ttk
import argparse
import inspect
import logging
import string
import sys
import typing
import tkinter as tk
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
    "File": ("New", "New Window", "Open", "Save", "Save As", "Exit"),
    "Edit": ("Undo", "Cut", "Copy", "Paste", "Select All"),
    "View": ("Status Bar",),
    "Help": ("About",),
}


class Shortcut:

    # can add more
    accepted_keys = set(string.ascii_lowercase) | {"shift", "ctrl"}
    # accepted_keys.union()
    abbreviation_mapping = {"ctrl": "Control"}

    def __init__(self, *keys):
        self.validate_keys(keys)
        self.keys = keys

    def validate_keys(self, keys: list):
        if not keys:
            raise ValueError("Shortcut must have at least one key")

        for key in keys:
            if key not in self.accepted_keys:
                raise ValueError(f"Shortcut key `{key}` not in {self.accepted_keys}")

    @property
    def accelerator(self) -> str:
        """How keybinding is displayed to a user"""
        return "+".join(k.capitalize() for k in self.keys)

    @property
    def key_binding(self) -> str:
        """Tkinter key binding"""
        bindings = []
        capitalize_next = False
        for key in self.keys:
            if key == "shift":
                capitalize_next = True
                continue

            binding = self.abbreviation_mapping.get(key, key)
            if capitalize_next:
                binding = binding.capitalize()
                capitalize_next = False

            bindings.append(binding)

        return f"<{'-'.join(bindings)}>"


SHORTCUTS = {
    "file_new": Shortcut("ctrl", "n"),
    "file_new_window": Shortcut("ctrl", "shift", "n"),
    "file_open": Shortcut("ctrl", "o"),
    "file_save": Shortcut("ctrl", "s"),
    "file_save_as": Shortcut("ctrl", "shift", "s"),
    "file_exit": Shortcut("ctrl", "q"),
    "edit_undo": Shortcut("ctrl", "z"),
    "edit_copy": Shortcut("ctrl", "c"),
    "edit_cut": Shortcut("ctrl", "x"),
    "edit_paste": Shortcut("ctrl", "v"),
    "edit_select_all": Shortcut("ctrl", "shift", "a"),
}


def _logger(func, level):
    @wraps(func)
    def wrapper(*args, **kwargs):
        level("Entering method %s", func.__name__)
        has_other_params_beside_self = len(args) > 1
        if has_other_params_beside_self or kwargs:
            level("Args %s kwargs %s", args, kwargs)
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
    _is_status_bar_visible = tk.BooleanVar()

    _menus: dict = {}
    _file: typing.Optional[Path] = None

    status_location = tk.StringVar()
    status_location.set(f"Ln 1, Col 1")

    status_zoom: str = "100%"  # todo
    status_platform: str = sys.platform
    status_encoding: str = "UTF-8"  # todo

    @log_info
    def __init__(
        self, root=None, window_dimension: WindowDimension = WindowDimension()
    ):
        """
        root: specify top level root. initiated by "File>New Window"
        window_dimension: specifically for window start up
        """
        self._initialize_root(root)
        self._set_window_size(window_dimension)
        self._create_menu_bar()
        self._create_text()
        self._create_scrollbar()
        self._create_status_bar()

    @log_debug
    def _initialize_root(self, root):
        if root:
            self._root = root
        self._root.wm_iconbitmap(DEFAULT_WINDOW_ICON)
        self._root.title(get_title())

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

                args = {"label": option_label, "command": command}
                shortcut = SHORTCUTS.get(lookup_key)
                if shortcut:
                    args["accelerator"] = shortcut.accelerator
                    self._root.bind_all(shortcut.key_binding, command)

                # Todo: less hardcoding
                if lookup_key == "view_status_bar":
                    _menu.add_checkbutton(
                        onvalue=True,
                        offvalue=False,
                        variable=self._is_status_bar_visible,
                        **args,
                    )
                else:
                    _menu.add_command(**args)

            self._menu_bar.add_cascade(label=menu_label, menu=_menu)

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
            try:
                padx = width - len(var)
                tk.Label(self._status_bar, text=var, bd=1).pack(
                    side=tk.RIGHT, padx=padx
                )
            except TypeError:  # tkinter variables
                padx = width - len(var.get())
                tk.Label(self._status_bar, textvariable=var, bd=1).pack(
                    side=tk.RIGHT, padx=padx
                )

            ttk.Separator(self._status_bar, orient=tk.VERTICAL).pack(
                side=tk.RIGHT, fill=tk.BOTH
            )

        self._status_bar.pack(side=tk.BOTTOM, fill=tk.X)
        self._is_status_bar_visible.set(True)

    def _update_location(self, *args, **kwargs):
        x, y = self._text_area.index(tk.INSERT).split(".")
        LOG.debug("Updating location (%s, %s) after %s", x, y, args)
        self.status_location.set(f"Ln {x}, Col {int(y) + 1}")

    @log_debug
    def _create_text(self):
        self._root.grid_rowconfigure(0, weight=1)
        self._root.grid_columnconfigure(0, weight=1)
        self._text_area = tk.Text(self._root)
        self._text_area.grid(sticky=tk.N + tk.E + tk.S + tk.W)

        self._text_area.bindtags(("Text", "post-class-bindings", ".", "all"))
        self._text_area.bind_class(
            "post-class-bindings", "<KeyPress>", self._update_location
        )
        self._text_area.bind_class(
            "post-class-bindings", "<Button-1>", self._update_location
        )

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

    def action_not_implemented(self, *args, **kwargs):
        LOG.warning("Warning: This does nothing!")
        # raise NotImplementedError()

    __prefix_action_method = "action_"

    """
    Use `{__prefix_action_method}{menu_bar_name}_{command}` naming convention to mark menu option commands
    (case insensitive)
    """

    @log_debug
    def _helper_would_you_like_to_save_before_performing_action(self, endaction):
        window = tk.Toplevel()
        tk.Label(
            window,
            text=f'Would you like to save changes to "{self._file or DEFAULT_UNNAMED_TITLE}"',
        ).pack(fill="x", padx=50, pady=5)

        def _destroy():
            window.destroy()

        def cancel():
            LOG.debug("You hit 'cancel'")
            _destroy()

        def dont_save():
            LOG.debug("You hit 'don't save'")
            _destroy()
            endaction()

        def save():
            LOG.debug("You hit 'save'")
            _destroy()
            self.action_file_save()
            endaction()

        tk.Button(window, text="Don't Save", command=dont_save).pack(side=tk.LEFT)
        tk.Button(window, text="Save", command=save).pack(side=tk.LEFT)
        tk.Button(window, text="Cancel", command=cancel).pack(side=tk.LEFT)

    @log_action
    def action_file_new(self, *args, **kwargs):
        def new():
            self._root.title(get_title())
            self._file = None
            self._text_area.delete(1.0, tk.END)

        self._helper_would_you_like_to_save_before_performing_action(new)

    @log_action
    def action_file_new_window(self, *args, **kwargs):
        orig_root = tk.Toplevel(self._root)
        new = Notepad(root=orig_root)
        new.run()

    @log_action
    def action_file_open(self, *args, **kwargs):
        file = tkfd.askopenfilename(**FILE_DIALOG_DEFAULT_ARGS)

        if not file:
            return

        self._file = Path(file)
        self._text_area.delete(1.0, tk.END)
        with open(self._file, "r") as f:
            self._text_area.insert(1.0, f.read())

        self._root.title(get_title(self._file.name))

    @log_debug
    def _helper_save_text(self, file: str):
        if not file:
            return

        self._file = Path(file)
        with open(self._file, "w") as f:
            f.write(self._text_area.get(1.0, tk.END))

        self._root.title(get_title(self._file.name))

    @log_debug
    def _helper_ask_save_filename(self) -> str:
        return tkfd.asksaveasfilename(
            initialfile=f"{DEFAULT_UNNAMED_TITLE}.{DEFAULT_FILE_EXTENSION}",
            **FILE_DIALOG_DEFAULT_ARGS,
        )

    @log_action
    def action_file_save(self, *args, **kwargs):
        if not self._file:
            self._file = self._helper_ask_save_filename()

        self._helper_save_text(self._file)

    @log_action
    def action_file_save_as(self, *args, **kwargs):
        self._file = self._helper_ask_save_filename()
        self._helper_save_text(self._file)

    @log_action
    def action_file_exit(self, *args, **kwargs):
        def exit():
            self._root.destroy()

        self._helper_would_you_like_to_save_before_performing_action(exit)

    @log_action
    def action_edit_undo(self, *args, **kwargs):
        self._text_area.event_generate("<<Undo>>")

    @log_action
    def action_edit_cut(self, *args, **kwargs):
        self._text_area.event_generate("<<Cut>>")

    @log_action
    def action_edit_copy(self, *args, **kwargs):
        self._text_area.event_generate("<<Copy>>")

    @log_action
    def action_edit_paste(self, *args, **kwargs):
        self._text_area.event_generate("<<Paste>>")

    @log_action
    def action_edit_select_all(self, *args, **kwargs):
        self._text_area.event_generate("<<SelectAll>>")

    @log_action
    def action_view_status_bar(self, *args, **kwargs):
        if self._is_status_bar_visible:
            self._status_bar.pack_forget()
        else:
            self._status_bar.pack(side=tk.BOTTOM, fill=tk.X)

        self._is_status_bar_visible = not self._is_status_bar_visible

    @log_action
    def action_help_about(self, *args, **kwargs):
        system_info = f"""App name: {APP_NAME}
Version: {__version__}
"""
        tkm.showinfo(APP_NAME, system_info + __doc__)


def configure_logging(verbose: int) -> bool:
    level = logging.WARN
    if verbose == 1:
        level = logging.INFO
    elif verbose >= 2:
        level = logging.DEBUG

    logging.basicConfig(level=level)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("-v", action="count", default=0)
    configure_logging(parser.parse_args().v)

    notepad = Notepad()
    notepad.run()
