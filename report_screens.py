"""report_screens.py - Campus report and cross-campus comparison report."""
import tkinter as tk

import database as db
import rules


def build_report_tab(app, tab):
    text = tk.Text(tab, height=18, width=80)
    text.pack(fill="both", expand=True)
    data = db.campus_report(app.campus["id"])
    text.insert("end", f"REPORT FOR {app.campus['name'].upper()}\n\n")
    text.insert("end", f"Total bookings: {data['total']}\n")
    text.insert("end", f"Average booking duration: {data['average']:.1f} hours\n\n")
    text.insert("end", "Most frequently used resources:\n")
    if not data["top"]:
        text.insert("end", "  No bookings yet.\n")
    for name, uses in data["top"]:
        text.insert("end", f"  {name}: {uses} booking(s)\n")
    text.config(state="disabled")


def build_comparison_tab(app, tab):
    text = tk.Text(tab, height=18, width=100, font=("Courier", 10))
    text.pack(fill="both", expand=True)
    text.insert("end", f"{'Campus':<14}{'Bookings':<10}{'Avg hours':<11}"
                       f"{'Max hours rule':<16}{'Most used resource'}\n")
    text.insert("end", "-" * 75 + "\n")
    for c in db.get_campuses():
        data = db.campus_report(c["id"])
        if data["top"]:
            top = data["top"][0][0]
        else:
            top = "None"
        limit = rules.CAMPUS_RULES[c["name"]]["max_hours"]
        text.insert("end", f"{c['name']:<14}{data['total']:<10}"
                           f"{data['average']:<11.1f}{limit:<16}{top}\n")
    text.insert("end", "\nNote: campuses with a lower maximum duration and shorter "
                       "opening hours tend to\nhave shorter bookings, so rules "
                       "directly affect usage trends.\n")
    text.config(state="disabled")
