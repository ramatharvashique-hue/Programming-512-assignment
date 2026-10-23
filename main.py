"""main.py - Starts the Smart Campus Resource Booking System.
Run with:  python main.py
"""
import tkinter as tk

import database as db
from login_screens import show_login, show_campus_select
from main_screen import show_main


class App(tk.Tk):
    def __init__(self):
        tk.Tk.__init__(self)
        self.title("Smart Campus Resource Booking System")
        self.geometry("920x580")
        self.user = None      # the logged in user object
        self.campus = None    # the active campus (a database row)
        db.setup_database()
        self.show_login()

    def clear(self):
        for widget in self.winfo_children():
            widget.destroy()

    def show_login(self):
        show_login(self)

    def show_campus_select(self):
        show_campus_select(self)

    def show_main(self):
        show_main(self)


if __name__ == "__main__":
    App().mainloop()
