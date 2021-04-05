
import typing

from notepad import constants

def get_title(current: typing.Optional[str] = None):
    if not current:
        current = constants.DEFAULT_UNNAMED_TITLE

    return f"{current} - {constants.APP_NAME}"


class WindowDimension:
    def __init__(
        self,
        *,
        width: int = constants.DEFAULT_WINDOW_WIDTH,
        height: int = constants.DEFAULT_WINDOW_HEIGHT,
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
