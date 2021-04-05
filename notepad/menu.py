from notepad.features import shortcuts, logger


class MenuOption:
    def __init__(self, menu_label: str, option_label: str, notepad: "Notepad"):
        self.menu_label = menu_label
        self.option_label = option_label
        self.actions = notepad._collect_actions()
        self.variable_bindings = notepad.variable_bindings

    @property
    def lookup_key(self) -> str:
        return f"{self.menu_label.lower()}_{self.option_label.lower().replace(' ','_')}"

    def action_not_implemented(self, *args, **kwargs):
        logger.LOG.warning("Warning: This does nothing!")

    @property
    def command(self) -> str:
        return self.actions.get(self.lookup_key, self.action_not_implemented)

    @property
    def _default_args(self) -> dict:
        return {"label": self.option_label, "command": self.command}

    @property
    def has_shortcut(self) -> bool:
        return self.lookup_key in shortcuts.SHORTCUTS

    @property
    def shortcut(self) -> shortcuts.Shortcut:
        return shortcuts.SHORTCUTS[self.lookup_key]

    @property
    def has_variable_binding(self) -> bool:
        return self.lookup_key in self.variable_bindings

    @property
    def args(self) -> dict:
        args = self._default_args.copy()
        if self.has_shortcut:
            args["accelerator"] = self.shortcut.accelerator

        if self.has_variable_binding:
            args["variable"] = self.variable_bindings[self.lookup_key]
            args["onvalue"] = True
            args["offvalue"] = False

        return args

    @property
    def widget_function(self) -> str:
        if self.has_variable_binding:
            return "add_checkbutton"
        return "add_command"
