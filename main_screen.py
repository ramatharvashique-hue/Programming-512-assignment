"""main_screen.py - The main window: header, active campus, policy and role tabs."""
from tkinter import ttk

import rules
from lecturer_screens import BookTab
from bookings_screen import BookingsTab
from admin_screens import ManageTab
from report_screens import build_report_tab, build_comparison_tab


def show_main(app):
    app.clear()
    top = ttk.Frame(app, padding=8)
    top.pack(fill="x")
    ttk.Label(top, text=f"User: {app.user.get_username()} ({app.user.get_role()})   |   "
                        f"Active campus: {app.campus['name']}",
              font=("Arial", 11, "bold")).pack(side="left")
    ttk.Button(top, text="Logout", command=app.show_login).pack(side="right")
    ttk.Button(top, text="Change campus",
               command=app.show_campus_select).pack(side="right", padx=5)
    ttk.Label(app, text=rules.get_policy_text(app.campus["name"]),
              foreground="blue", padding=(8, 0)).pack(anchor="w")

    notebook = ttk.Notebook(app)
    notebook.pack(fill="both", expand=True, padx=8, pady=8)

    # Role based access: each user type only gets its own tabs
    for name in app.user.tabs():
        tab = ttk.Frame(notebook, padding=10)
        notebook.add(tab, text=name)
        if name == "Book Resource":
            BookTab(app, tab)
        elif name == "My Bookings":
            BookingsTab(app, tab, "lecturer")
        elif name == "Manage Resources":
            ManageTab(app, tab)
        elif name == "Campus Bookings":
            BookingsTab(app, tab, "campus")
        elif name == "Campus Report":
            build_report_tab(app, tab)
        elif name == "All Bookings":
            BookingsTab(app, tab, "all")
        elif name == "Comparison Report":
            build_comparison_tab(app, tab)
