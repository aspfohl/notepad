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
* Unit testing framework

## Philosophy

This is never meant to be a full functional text editor. I originally started this project as an exercise, focusing on purely cloning [Windows Notepad](https://www.microsoft.com/en-us/p/windows-notepad/9msmlrh6lzf3). Along the way, I tried to focus on:
* **Clean**: Inspired by a recent reread of [Clean code](https://www.oreilly.com/library/view/clean-code-a/9780136083238/), I strived for (1) small, maintainable functions that do only one thing, (2) independent classes to manage data structures & abstract away complexities and (3) descriptive names and no unnecessary documentation
* **Effort**: (Don't reinvent the wheel!) Tkinter is not the most friendly or fun to work with, so I started with [this tutorial](https://www.geeksforgeeks.org/make-notepad-using-tkinter/) as a base. Most of this is significantly refactored to remove 100 line __init__ methods.
* **Simple**: For other projects I would create a virtual environment and set up library management. As a challenge, I purposely avoided anything outside of the standard python library, and restricted the code to [notepad.py](notepad.py), which includes all supporting classes, methods, testing framework, and documentation. 
* **MVP First**: As I have many projects that I've started but never finished, I wanted to try out a small project using the philosophies in [this article](https://www.zainrizvi.io/blog/do-more-by-doing-less/). I timeboxed project for 5 hours & limited feature scope. Again, this is not a text editor that should be preferred over any other (yet!), so I didn't build it like one. . I listed out the most core features that I would need to consider this done in the [todo](todo) file. Along the way, I realized some simple theming was easy, and logging would save me significant time for debugging. Note there's still significant features & bugs left
