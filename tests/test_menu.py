from unittest import mock
import tkinter as tk
import pytest

from notepad import menu
from notepad.features import shortcuts
from tests.common import my_notepad


@pytest.fixture()
def my_notepad_with_bindings(my_notepad):
    def mocked_collect_actions():
        return {}

    my_notepad._collect_actions = mocked_collect_actions

    my_binding = tk.BooleanVar() 

    my_notepad._my_binding = my_binding
    my_notepad.variable_bindings = {"foo_variable_binding": my_binding}
    yield my_notepad


@mock.patch("notepad.features.shortcuts.SHORTCUTS", {})
def test_menu_option_simple(my_notepad_with_bindings):
    mo = menu.MenuOption("foo", "baz", my_notepad_with_bindings)

    assert mo.menu_label == "foo"
    assert mo.option_label == "baz"
    assert mo.actions == {}
    assert mo.lookup_key == "foo_baz"
    assert mo.command == mo.action_not_implemented
    assert mo._default_args.get("label") == "baz"
    assert mo.has_shortcut is False

    with pytest.raises(KeyError):
        mo.shortcut

    assert mo.has_variable_binding is False
    assert mo.args == mo._default_args
    assert mo.widget_function == "add_command"

    # this shouldn't raise errors (yet)
    mo.action_not_implemented()


@mock.patch(
    "notepad.features.shortcuts.SHORTCUTS", {"foo_shortcut": shortcuts.Shortcut("ctrl", "f")}
)
def test_menu_option_with_shortcut(my_notepad_with_bindings):
    mo = menu.MenuOption("foo", "shortcut", my_notepad_with_bindings)

    assert mo.has_shortcut is True
    assert isinstance(mo.shortcut, shortcuts.Shortcut)
    assert mo.shortcut.keys == ("ctrl", "f")
    assert set(mo.args.keys()) == {"label", "command", "accelerator"}
    assert mo.args.get("accelerator")
    assert mo.widget_function == "add_command"


@mock.patch("notepad.features.shortcuts.SHORTCUTS", {})
def test_menu_option_with_variable_binding(my_notepad_with_bindings):
    mo = menu.MenuOption("foo", "variable binding", my_notepad_with_bindings)

    assert mo.lookup_key == "foo_variable_binding"
    assert mo.has_shortcut is False
    assert set(mo.args.keys()) == {"label", "command", "variable", "onvalue", "offvalue"}
    assert mo.args.get("variable") == my_notepad_with_bindings._my_binding
    assert mo.args.get("onvalue") is True
    assert mo.args.get("offvalue") is False
    assert mo.widget_function == "add_checkbutton"
