"""login_screens.py - Login, registration and campus selection screens."""
import tkinter as tk
from tkinter import ttk, messagebox

import database as db
from helpers import show_message
from models import create_user


class LoginScreen:
    def __init__(self, app):
        self.app = app
        app.clear()
        app.user = None
        app.campus = None

        frame = ttk.Frame(app, padding=30)
        frame.pack(expand=True)
        ttk.Label(frame, text="Smart Campus Resource Booking System",
                  font=("Arial", 16, "bold")).grid(row=0, column=0, columnspan=2, pady=15)
        ttk.Label(frame, text="Username:").grid(row=1, column=0, sticky="e", pady=5)
        ttk.Label(frame, text="Password:").grid(row=2, column=0, sticky="e", pady=5)
        self.username_var = tk.StringVar()
        self.password_var = tk.StringVar()
        ttk.Entry(frame, textvariable=self.username_var, width=25).grid(row=1, column=1)
        ttk.Entry(frame, textvariable=self.password_var, show="*",
                  width=25).grid(row=2, column=1)
        ttk.Button(frame, text="Login", command=self.do_login).grid(row=3, column=0, pady=15)
        ttk.Button(frame, text="Register as Lecturer",
                   command=self.do_register).grid(row=3, column=1)

    def do_login(self):
        username = self.username_var.get().strip()
        password = self.password_var.get()
        if username == "" or password == "":
            messagebox.showwarning("Missing details", "Enter username and password.")
            return
        row = db.login(username, password)
        if row is None:
            messagebox.showerror("Login failed", "Wrong username or password.")
            return
        self.app.user = create_user(row)
        self.app.show_campus_select()

    def do_register(self):
        ok, message = db.register_lecturer(self.username_var.get().strip(),
                                           self.password_var.get())
        show_message("Register", ok, message)


class CampusScreen:
    def __init__(self, app):
        self.app = app
        app.clear()

        # Campus administrators can only work on their own campus
        campuses = []
        for c in db.get_campuses():
            if app.user.get_role() != "Campus Administrator":
                campuses.append(c)
            elif c["id"] == app.user.get_campus_id():
                campuses.append(c)

        # Dictionary: campus name -> campus row
        self.campus_rows = {}
        names = []
        for c in campuses:
            self.campus_rows[c["name"]] = c
            names.append(c["name"])

        frame = ttk.Frame(app, padding=30)
        frame.pack(expand=True)
        ttk.Label(frame, text=f"Welcome, {app.user.get_username()} ({app.user.get_role()})",
                  font=("Arial", 14, "bold")).pack(pady=10)
        ttk.Label(frame, text="Select a campus:").pack()
        self.campus_var = tk.StringVar(value=names[0])
        ttk.Combobox(frame, textvariable=self.campus_var, state="readonly",
                     values=names).pack(pady=10)
        ttk.Button(frame, text="Continue", command=self.choose_campus).pack()
        ttk.Button(frame, text="Logout", command=app.show_login).pack(pady=10)

    def choose_campus(self):
        self.app.campus = self.campus_rows[self.campus_var.get()]
        self.app.show_main()


def show_login(app):
    LoginScreen(app)


def show_campus_select(app):
    CampusScreen(app)
