# notepad :ledger:
This is a simple notepad app implemented in pure python. Requirements: [python 3.6+](https://www.python.org/downloads/). 

Initialize:
```bash
python setup.py install
```

To run: 
```bash
python -m notepad
```

To test: 
```bash
pytest tests
```

For help:
```bash
python -m notepad --help
```

## Features 
* Standard file commands
* Standard clipboard commands
* Cursor detection & scrolling
* Keyboard shortcuts
* Status bar, with ability to hide
* Simple theming and "I'm feeling lucky" mode

For developing:
* Detailed & automated debug logging
* unit testing framework

## Philosophy

This is never meant to be a full functional text editor. Originally set out to clone [Windows Notepad](https://www.microsoft.com/en-us/p/windows-notepad/9msmlrh6lzf3) as an exercise:
* [Clean code](https://www.oreilly.com/library/view/clean-code-a/9780136083238/): small, maintainable functions that do only one thing. Independent classes to manage data structures & abstract away complexities. Descriptive names and no unnecessary documentation
* Don't reinvent the wheel (just notepad!). Tkinter is not the most friendly or fun to work with, so I started with [this tutorial](https://www.geeksforgeeks.org/make-notepad-using-tkinter/) as a base. Most of this is significantly refactored to remove 100 line __init__ methods.
* Timeboxed project for 5 hours & limited feature scope: Again, this is not a text editor that should be preferred over any other (yet!), so I didn't build it like one. [This article](https://www.zainrizvi.io/blog/do-more-by-doing-less/) really resonated with me. I listed out the most core features that I would need to consider this done in the [todo](todo) file. Along the way, I realized some simple theming was easy, and logging would save me significant time for debugging. Note there's still significant features & bugs left