import typing
import random


DEFAULT_FONT = "Courier New"


class Theme(typing.NamedTuple):

    background: str
    foreground: str

    ## Other tkinter parameters to explore
    # highlightbackground: The color of the focus highlight when the text widget does not have focus.
    # highlightcolor: The color of the focus highlight when the text widget has the focus.
    # highlightthickness: The thickness of the focus highlight. Default is 1. Set highlightthickness=0 to suppress display of the focus highlight.
    # insertbackground: The color of the insertion cursor. Default is black.
    # insertofftime: The number of milliseconds the insertion cursor is off during its blink cycle. Set this option to zero to suppress blinking. Default is 300.

    # optional params use system default
    font_style: typing.Optional[int] = None
    font_size: typing.Optional[int] = 20

    def as_dict(self):
        res = {"bg": self.background, "fg": self.foreground}

        font = tuple(i for i in (self.font_style, self.font_size) if i)
        if font:
            res["font"] = font
        return res


def generate_random_color():
    return f"#{''.join([random.choice('0123456789ABCDEF') for j in range(6)])}"


def generate_random_theme():
    # this could be more crazy
    return (generate_random_color(), generate_random_color(), DEFAULT_FONT, random.randint(5, 50))


CUSTOM_THEME_PARAMS = {
    "dark": ("black", "green", DEFAULT_FONT),
    "light": ("white", "black"),
    "im_feeling_lucky": generate_random_theme,
}

def get_theme(theme_key: str) -> Theme:
    theme_args = CUSTOM_THEME_PARAMS[theme_key]
    if callable(theme_args):
        theme_args = theme_args()
    
    return Theme(*theme_args)