"""lecturer_screens.py - The lecturer's 'Book Resource' tab."""
import tkinter as tk
from tkinter import ttk, messagebox
from datetime import date, datetime

import database as db
from helpers import make_tree, fill_tree, show_message


class BookTab:
    def __init__(self, app, tab):
        self.app = app
        left = ttk.Frame(tab)
        left.pack(side="left", fill="both", expand=True)
        self.tree = make_tree(left, ("ID", "Code", "Resource", "Availability"),
                              (40, 100, 200, 150))
        right = ttk.Frame(tab, padding=15)
        right.pack(side="right", fill="y")

        self.date_var = tk.StringVar(value=date.today().strftime("%Y-%m-%d"))
        self.start_var = tk.IntVar(value=9)
        self.duration_var = tk.IntVar(value=1)
        ttk.Label(right, text="Date (YYYY-MM-DD):").pack(anchor="w")
        ttk.Entry(right, textvariable=self.date_var).pack(fill="x", pady=3)
        ttk.Label(right, text="Start hour:").pack(anchor="w")
        ttk.Combobox(right, textvariable=self.start_var, state="readonly",
                     values=list(range(6, 21))).pack(fill="x", pady=3)
        ttk.Label(right, text="Duration (hours):").pack(anchor="w")
        ttk.Spinbox(right, from_=1, to=8, textvariable=self.duration_var).pack(fill="x", pady=3)
        ttk.Button(right, text="Check availability",
                   command=self.refresh).pack(fill="x", pady=8)
        ttk.Button(right, text="Book selected resource",
                   command=self.book).pack(fill="x")
        self.refresh()

    def read_slot(self):
        """Read date, start and duration from the form. Returns None if invalid."""
        try:
            start = int(self.start_var.get())
            duration = int(self.duration_var.get())
            day = datetime.strptime(self.date_var.get().strip(), "%Y-%m-%d")
        except (ValueError, tk.TclError):
            messagebox.showerror("Invalid input",
                                 "Check the date (YYYY-MM-DD), start hour and duration.")
            return None
        return day.strftime("%Y-%m-%d"), start, duration

    def refresh(self):
        slot = self.read_slot()
        if slot is None:
            return
        rows = []
        for r in db.get_resources(self.app.campus["id"]):
            free = db.is_available(r["id"], slot[0], slot[1], slot[2])
            if free:
                status = "Available"
            else:
                status = "Booked"
            rows.append((r["id"], r["code"], r["name"], status))
        fill_tree(self.tree, rows)

    def book(self):
        selected = self.tree.selection()
        if not selected:
            messagebox.showwarning("No resource", "Select a resource first.")
            return
        slot = self.read_slot()
        if slot is None:
            return
        resource_id = self.tree.item(selected[0])["values"][0]
        ok, message = db.create_booking(resource_id, self.app.user.get_user_id(),
                                        self.app.campus["id"], self.app.campus["name"],
                                        slot[0], slot[1], slot[2])
        show_message("Booking", ok, message)
        self.refresh()
