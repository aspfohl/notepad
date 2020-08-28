import os

import tkinter as tk
import tkinter.messagebox as tkm
import tkinter.filedialog as tkfd


DEFAULT_WINDOW_WIDTH = 300
DEFAULT_WINDOW_HEIGHT = 300


class Notepad:

    _root = tk.Tk()

    _window_width = DEFAULT_WINDOW_WIDTH
    _window_height = DEFAULT_WINDOW_HEIGHT
    _text_area = tk.Text(_root)
    _menu_bar = tk.Menu(_root)
    _file_menu = tk.Menu(_menu_bar, tearoff=0)
    _edit_menu = tk.Menu(_menu_bar, tearoff=0)
    _help_menu = tk.Menu(_menu_bar, tearoff=0)
    _scroll_bar = tk.Scrollbar(_text_area)
    _file = None

    def __init__(self, **kwargs):

        try:
            self._root.wm_iconbitmap("Notepad.ico")
        except tk.TclError:
            pass

        # Set window size (the default is 300x300)

        try:
            self._window_width = kwargs.get("width", DEFAULT_WINDOW_WIDTH)
        except KeyError:
            pass

        try:
            self._window_height = kwargs["height"]
        except KeyError:
            pass

        # Set the window text
        self._root.title("Untitled - Notepad")

        # Center the window
        screenWidth = self._root.winfo_screenwidth()
        screenHeight = self._root.winfo_screenheight()

        # For left-alling
        left = (screenWidth / 2) - (self._window_width / 2)

        # For right-allign
        top = (screenHeight / 2) - (self._window_height / 2)

        # For top and bottom
        self._root.geometry("%dx%d+%d+%d" % (self._window_width, self._window_height, left, top))

        # To make the textarea auto resizable
        self._root.grid_rowconfigure(0, weight=1)
        self._root.grid_columnconfigure(0, weight=1)

        # Add controls (widget)
        self._text_area.grid(sticky=tk.N + tk.E + tk.S + tk.W)

        # To open new file
        self._file_menu.add_command(label="New", command=self.__newFile)

        # To open a already existing file
        self._file_menu.add_command(label="Open", command=self.__openFile)

        # To save current file
        self._file_menu.add_command(label="Save", command=self.__saveFile)

        # To create a line in the dialog
        self._file_menu.add_separator()
        self._file_menu.add_command(label="Exit", command=self.__quitApplication)
        self._menu_bar.add_cascade(label="File", menu=self._file_menu)

        # To give a feature of cut
        self._edit_menu.add_command(label="Cut", command=self.__cut)

        # to give a feature of copy
        self._edit_menu.add_command(label="Copy", command=self.__copy)

        # To give a feature of paste
        self._edit_menu.add_command(label="Paste", command=self.__paste)

        # To give a feature of editing
        self._menu_bar.add_cascade(label="Edit", menu=self._edit_menu)

        # To create a feature of description of the notepad
        self._help_menu.add_command(label="About Notepad", command=self.__showAbout)
        self._menu_bar.add_cascade(label="Help", menu=self._help_menu)

        self._root.config(menu=self._menu_bar)

        self._scroll_bar.pack(side=tk.RIGHT, fill=tk.Y)

        # Scrollbar will adjust automatically according to the content
        self._scroll_bar.config(command=self._text_area.yview)
        self._text_area.config(yscrollcommand=self._scroll_bar.set)

    def __quitApplication(self):
        self._root.destroy()
        # exit()

    def __showAbout(self):
        tkm.showinfo("Notepad", "Mrinal Verma")

    def __openFile(self):

        self._file = tkfd.askopenfilename(
            defaultextension=".txt", filetypes=[("All Files", "*.*"), ("Text Documents", "*.txt")]
        )

        if self._file == "":

            # no file to open
            self._file = None
        else:

            # Try to open the file
            # set the window title
            self._root.title(os.path.basename(self._file) + " - Notepad")
            self._text_area.delete(1.0, tk.END)

            file = open(self._file, "r")

            self._text_area.insert(1.0, file.read())

            file.close()

    def __newFile(self):
        self._root.title("Untitled - Notepad")
        self._file = None
        self._text_area.delete(1.0, tk.END)

    def __saveFile(self):

        if self._file == None:
            # Save as new file
            self._file = tkfd.asksaveasfilename(
                initialfile="Untitled.txt",
                defaultextension=".txt",
                filetypes=[("All Files", "*.*"), ("Text Documents", "*.txt")],
            )

            if self._file == "":
                self._file = None
            else:

                # Try to save the file
                file = open(self._file, "w")
                file.write(self._text_area.get(1.0, tk.END))
                file.close()

                # Change the window title
                self._root.title(os.path.basename(self._file) + " - Notepad")

        else:
            file = open(self._file, "w")
            file.write(self._text_area.get(1.0, tk.END))
            file.close()

    def __cut(self):
        self._text_area.event_generate("<<Cut>>")

    def __copy(self):
        self._text_area.event_generate("<<Copy>>")

    def __paste(self):
        self._text_area.event_generate("<<Paste>>")

    def run(self):

        # Run main application
        self._root.mainloop()


# Run main application
notepad = Notepad(width=600, height=400)
notepad.run()

