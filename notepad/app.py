from functools import lru_cache
from pathlib import Path
from tkinter import ttk
import sys
import tkinter as tk
import tkinter.filedialog as tkfd
import tkinter.messagebox as tkm
import typing

import notepad
from notepad import constants, window, menu
from notepad.features import shortcuts, themes, logger

class Notepad:

    _root = tk.Tk()
    _is_status_bar_visible = tk.BooleanVar()
    _wrap_words = tk.BooleanVar()

    _file: typing.Optional[Path] = None

    status_location = tk.StringVar()
    status_location.set("Ln 1, Col 1")

    status_zoom: str = "100%"  # todo
    status_platform: str = sys.platform
    status_encoding: str = "UTF-8"  # todo

    theme = tk.StringVar()
    theme.set("light")  # because most developers love this

    variable_bindings = {
        "view_status_bar": _is_status_bar_visible,
        "format_wrap_words": _wrap_words,
    }

    @logger.log_info
    def __init__(self, root=None, window_dimension: window.WindowDimension = window.WindowDimension()):
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

    @logger.log_debug
    def _initialize_root(self, root):
        if root:
            self._root = root
        self._root.wm_iconbitmap(constants.DEFAULT_WINDOW_ICON)
        self._set_window_title()

    @logger.log_debug
    def _set_window_title(self, current: typing.Optional[str] = None):
        self._root.title(window.get_title(current))

    @logger.log_debug
    def _set_window_size(self, window_dimension: window.WindowDimension):
        geometry = window_dimension.get_geometry(
            screen_width=self._root.winfo_screenwidth(),
            screen_height=self._root.winfo_screenheight(),
        )
        self._root.geometry(geometry)

    def _helper_sub_menu(self, menu_label: str, options: tuple) -> tk.Menu:
        sub_menu = tk.Menu(self._menu_bar, tearoff=0)
        for option_label in options:
            option = menu.MenuOption(menu_label, option_label, self)

            if option.has_shortcut:
                self._root.bind_all(option.shortcut.key_binding, option.command)

            getattr(sub_menu, option.widget_function)(**option.args)
        return sub_menu

    @logger.log_debug
    def _create_menu_bar(self):
        self._menu_bar = tk.Menu(self._root)
        for menu_label, options in constants.MENU_LAYOUT.items():
            _sub_menu = self._helper_sub_menu(menu_label, options)
            self._menu_bar.add_cascade(label=menu_label, menu=_sub_menu)
        self._root.config(menu=self._menu_bar)

    @logger.log_debug
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
                tk.Label(self._status_bar, text=var, bd=1).pack(side=tk.RIGHT, padx=padx)
            except TypeError:  # tkinter variables
                padx = width - len(var.get())
                tk.Label(self._status_bar, textvariable=var, bd=1).pack(side=tk.RIGHT, padx=padx)

            ttk.Separator(self._status_bar, orient=tk.VERTICAL).pack(side=tk.RIGHT, fill=tk.BOTH)

        self._status_bar.pack(side=tk.BOTTOM, fill=tk.X)
        self._is_status_bar_visible.set(True)

    def _update_location(self, *args, **kwargs):
        x, y = self._text_area.index(tk.INSERT).split(".")
        logger.LOG.debug("Updating location (%s, %s) after %s", x, y, args)
        self.status_location.set(f"Ln {x}, Col {int(y) + 1}")

    @logger.log_debug
    def _create_text(self):
        self._root.grid_rowconfigure(0, weight=1)
        self._root.grid_columnconfigure(0, weight=1)
        self._text_area = tk.Text(self._root)
        self._text_area.grid(sticky=tk.N + tk.E + tk.S + tk.W)

        self._text_area.bindtags(("Text", "post-class-bindings", ".", "all"))
        self._text_area.bind_class("post-class-bindings", "<KeyPress>", self._update_location)
        self._text_area.bind_class("post-class-bindings", "<Button-1>", self._update_location)
        self._set_theme()

    @logger.log_info
    def _set_theme(self):
        theme = themes.get_theme(self.theme.get())
        self._text_area.configure(**theme.as_dict())

    @logger.log_debug
    def _create_scrollbar(self):
        scroll_bar = tk.Scrollbar(self._text_area)
        scroll_bar.pack(side=tk.RIGHT, fill=tk.Y)
        scroll_bar.config(command=self._text_area.yview)
        self._text_area.config(yscrollcommand=scroll_bar.set)

    def run(self):
        logger.LOG.info("Running app")
        self._root.mainloop()

    @lru_cache()
    def _collect_actions(self) -> set:
        actions = {
            name.replace(self.__PREFIX_ACTION_METHOD, ""): getattr(self, name)
            for name in dir(self)
            if name.startswith(self.__PREFIX_ACTION_METHOD) and callable(getattr(self, name))
        }
        logger.LOG.debug("Found %s actions: %s", len(actions.keys()), list(actions.keys()))
        return actions

    __PREFIX_ACTION_METHOD = "action_"

    """
    Use `{__prefix_action_method}{menu_bar_name}` naming convention to mark menu option commands
    (case insensitive)
    """

    @logger.log_debug
    def _helper_would_you_like_to_save_before_performing_action(self, endaction):
        w = tk.Toplevel()
        tk.Label(
            w,
            text=f'Would you like to save changes to "{self._file or constants.DEFAULT_UNNAMED_TITLE}"',
        ).pack(fill="x", padx=50, pady=5)

        def _destroy():
            w.destroy()

        def cancel():
            logger.LOG.debug("You hit 'cancel'")
            _destroy()

        def dont_save():
            logger.LOG.debug("You hit 'don't save'")
            _destroy()
            endaction()

        def save():
            logger.LOG.debug("You hit 'save'")
            _destroy()
            self.action_file_save()
            endaction()

        tk.Button(w, text="Don't Save", command=dont_save).pack(side=tk.LEFT)
        tk.Button(w, text="Save", command=save).pack(side=tk.LEFT)
        tk.Button(w, text="Cancel", command=cancel).pack(side=tk.LEFT)

    @logger.log_action
    def action_file_new(self, *args, **kwargs):
        def new():
            self._set_window_title()
            self._file = None
            self._text_area.delete(1.0, tk.END)

        self._helper_would_you_like_to_save_before_performing_action(new)

    @logger.log_action
    def action_file_new_window(self, *args, **kwargs):
        orig_root = tk.Toplevel(self._root)
        new = Notepad(root=orig_root)
        new.run()

    @logger.log_action
    def action_file_open(self, *args, **kwargs):
        file = tkfd.askopenfilename(**constants.FILE_DIALOG_DEFAULT_ARGS)

        if not file:
            return

        self._file = Path(file)
        self._text_area.delete(1.0, tk.END)
        with open(self._file, "r") as f:
            self._text_area.insert(1.0, f.read())

        self._set_window_title(self._file.name)

    @logger.log_debug
    def _helper_save_text(self, file: str):
        if not file:
            return

        self._file = Path(file)
        with open(self._file, "w") as f:
            f.write(self._text_area.get(1.0, tk.END))

        self._set_window_title(self._file.name)

    @logger.log_debug
    def _helper_ask_save_filename(self) -> str:
        return tkfd.asksaveasfilename(
            initialfile=f"{constants.DEFAULT_UNNAMED_TITLE}.{constants.DEFAULT_FILE_EXTENSION}",
            **constants.FILE_DIALOG_DEFAULT_ARGS,
        )

    @logger.log_action
    def action_file_save(self, *args, **kwargs):
        if not self._file:
            self._file = self._helper_ask_save_filename()

        self._helper_save_text(self._file)

    @logger.log_action
    def action_file_save_as(self, *args, **kwargs):
        self._file = self._helper_ask_save_filename()
        self._helper_save_text(self._file)

    @logger.log_action
    def action_file_exit(self, *args, **kwargs):
        def exit():
            self._root.destroy()

        self._helper_would_you_like_to_save_before_performing_action(exit)

    @logger.log_action
    def action_edit_undo(self, *args, **kwargs):
        self._text_area.event_generate("<<Undo>>")

    @logger.log_action
    def action_edit_cut(self, *args, **kwargs):
        self._text_area.event_generate("<<Cut>>")

    @logger.log_action
    def action_edit_copy(self, *args, **kwargs):
        self._text_area.event_generate("<<Copy>>")

    @logger.log_action
    def action_edit_paste(self, *args, **kwargs):
        self._text_area.event_generate("<<Paste>>")

    @logger.log_action
    def action_edit_delete(self, *args, **kwargs):
        self._text_area.event_generate("<<Clear>>")

    @logger.log_action
    def action_edit_select_all(self, *args, **kwargs):
        self._text_area.event_generate("<<SelectAll>>")

    @logger.log_action
    def action_format_theme(self, *args, **kwargs):
        popup = tk.Toplevel(self._root)
        tk.Label(popup, text="Choose a theme:", justify=tk.LEFT, padx=20).pack()

        for theme in themes.CUSTOM_THEME_PARAMS:
            tk.Radiobutton(
                popup,
                text=theme,
                padx=20,
                variable=self.theme,
                command=self._set_theme,
                value=theme,
            ).pack(anchor=tk.W)

        def _destroy():
            popup.destroy()

        tk.Button(popup, text="OK", command=_destroy).pack()

    @logger.log_action
    def action_format_wrap_words(self, *args, **kwargs):
        if self._wrap_words:
            self._text_area.configure(wrap=tk.WORD)
        else:
            self._text_area.configure(wrap=tk.CHAR)
        self._wrap_words = not self._wrap_words

    @logger.log_action
    def action_view_status_bar(self, *args, **kwargs):
        if self._is_status_bar_visible:
            self._status_bar.pack_forget()
        else:
            self._status_bar.pack(side=tk.BOTTOM, fill=tk.X)

        self._is_status_bar_visible = not self._is_status_bar_visible

    @logger.log_action
    def action_help_view_help(self, *args, **kwargs):
        help_text = f"""Please see main repo for additional help or to submit an issue:

https://github.com/aspfohl/notepad
"""
        tkm.showinfo(constants.APP_NAME, help_text)

    @logger.log_action
    def action_help_about(self, *args, **kwargs):
        system_info = f"""App name: {constants.APP_NAME}
Version: {notepad.__version__}
"""
        tkm.showinfo(constants.APP_NAME, system_info + notepad.__doc__)
