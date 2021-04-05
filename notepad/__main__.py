
import argparse

from notepad.features import logger
from notepad import app

import notepad

HELP_TEXT = f"""{notepad.__doc__}
VERSION: {notepad.__version__}"""


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=HELP_TEXT)
    parser.add_argument(
        "-v", action="count", default=0, help="Change log level. Default: no logging."
    )
    logger.configure_logging(parser.parse_args().v)

    notepad = app.Notepad()
    notepad.run()
