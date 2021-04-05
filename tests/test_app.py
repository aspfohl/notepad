
from notepad import app
from notepad.features import themes
from tests.common import my_notepad

def test_properties(my_notepad):
    assert my_notepad._is_status_bar_visible
    assert my_notepad._wrap_words
    assert my_notepad._file is None
    assert my_notepad.status_zoom ==  "100%"
    assert my_notepad.status_encoding ==  "UTF-8"
    assert my_notepad.theme.get() in themes.CUSTOM_THEME_PARAMS


def test_init_app(my_notepad):
    assert my_notepad._root is not None
    assert my_notepad._root.title() == "Untitled - PyNotepad"
    assert my_notepad._root.geometry() is not None
    assert my_notepad._menu_bar is not None
    assert my_notepad._status_bar is not None
    assert my_notepad._text_area is not None

def test_app_has_shortcuts():
    """
    All shortcuts defined in shortcuts.py have actions defined, or overlap is handled gracefully
    """
    raise NotImplementedError

def test__collect_actions(my_notepad):
    pass