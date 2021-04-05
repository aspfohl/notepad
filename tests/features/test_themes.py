import random
from unittest import mock

import pytest

from notepad.features import themes


def test_theme():
    theme = themes.Theme("white", "black", font_style="webdings", font_size=5000)
    assert theme.background == "white"
    assert theme.foreground == "black"

    theme_dict = theme.as_dict()
    assert theme_dict.get("bg") == "white"
    assert theme_dict.get("fg") == "black"
    assert theme_dict.get("font") == ("webdings", 5000)


def test_generate_random_color():
    random.seed(123)
    color = themes.generate_random_color()

    assert color
    assert len(color) == 7
    assert color[0] == "#"
    assert color == "#182D83"


def test_generate_random_theme():
    random.seed(123)
    bg, fg, style, size = themes.generate_random_theme()

    assert bg == "#182D83"
    assert fg == "#1CAA15"
    assert style == "Courier New"
    assert size == 13


@mock.patch("notepad.features.themes.CUSTOM_THEME_PARAMS", {"explicit": ("red", "red")})
def test_get_theme__explicit():
    theme = themes.get_theme("explicit")
    assert theme.background == "red"
    assert theme.foreground == "red"


def callable_buzz():
    return ("black", "yellow")


@mock.patch("notepad.features.themes.CUSTOM_THEME_PARAMS", {"callable_buzz": callable_buzz})
def test_get_theme__callable():
    theme = themes.get_theme("callable_buzz")
    assert theme.background == "black"
    assert theme.foreground == "yellow"


@pytest.mark.parametrize("theme_key", themes.CUSTOM_THEME_PARAMS.keys())
def test_configured_themes(theme_key):
    """Any custom themes should work"""
    assert themes.get_theme(theme_key)
