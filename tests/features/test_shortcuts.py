import pytest

from notepad.features import shortcuts


def test_shortcut():
    keys = ("ctrl", "shift", "a")
    my_shortcut = shortcuts.Shortcut(*keys)

    assert my_shortcut.keys == keys
    assert my_shortcut.accelerator == "Ctrl+Shift+A"
    assert my_shortcut.key_binding == "<Control-A>"


def test_shortcut_raises():

    with pytest.raises(ValueError, match="at least one key"):
        shortcuts.Shortcut()

    with pytest.raises(ValueError, match="`foo` not in"):
        shortcuts.Shortcut("ctrl", "shift", "foo")


def test_short_cut_overlap():
    """No two shortcuts should be used twice"""
    values = tuple(s.key_binding for s in shortcuts.SHORTCUTS.values())
    assert len(values) == len(set(values))
