"""
Shortcut mapping for notepad
"""

import string

from notepad import constants


class Shortcut:
    """
    Keyboard shortcut configuration
    """

    # this is not complete: can add more
    accepted_keys = set(string.ascii_lowercase) | {"shift", "ctrl"}
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

# menu_bar_name: shortcut
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
