"""bookings_screen.py - Bookings table used by lecturers, admins and operators."""
from tkinter import ttk, messagebox

import database as db
from helpers import make_tree, fill_tree, show_message


class BookingsTab:
    """mode is 'lecturer' (own bookings), 'campus' (active campus) or 'all'."""

    def __init__(self, app, tab, mode):
        self.app = app
        self.mode = mode
        columns = ("ID", "Campus", "Resource", "Lecturer", "Date", "Start", "Duration", "Status")
        self.tree = make_tree(tab, columns, (40, 110, 140, 110, 90, 60, 70, 80))

        buttons = ttk.Frame(tab)
        buttons.pack(pady=8)
        ttk.Button(buttons, text="Refresh", command=self.refresh).pack(side="left", padx=5)
        if mode == "lecturer":
            ttk.Button(buttons, text="Cancel selected booking",
                       command=self.cancel).pack(side="left", padx=5)
        self.refresh()

    def refresh(self):
        if self.mode == "lecturer":
            rows = db.get_bookings(lecturer_id=self.app.user.get_user_id())
        elif self.mode == "campus":
            rows = db.get_bookings(campus_id=self.app.campus["id"])
        else:
            rows = db.get_bookings()
        fill_tree(self.tree, rows)

    def cancel(self):
        selected = self.tree.selection()
        if not selected:
            messagebox.showwarning("Cancel", "Select a booking first.")
            return
        booking_id = self.tree.item(selected[0])["values"][0]
        ok, message = db.cancel_booking(booking_id, self.app.user.get_user_id())
        show_message("Cancel booking", ok, message)
        self.refresh()
