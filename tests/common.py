
import logging
import tkinter as tk
import sys

import pytest

from notepad import app

LOG = logging.getLogger(__name__)

@pytest.fixture()
def my_notepad():
    n = app.Notepad(root=tk.Tk())
    yield n
    n._root.destroy()

@pytest.fixture()
def log_stream():
    ls = logging.StreamHandler(sys.stdout)
    LOG.addHandler(ls)
    yield ls
    LOG.removeHandler(ls)
