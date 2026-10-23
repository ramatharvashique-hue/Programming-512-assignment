"""admin_screens.py - The campus administrator's 'Manage Resources' tab."""
import tkinter as tk
from tkinter import ttk, messagebox

import database as db
from helpers import make_tree, fill_tree, show_message


class ManageTab:
    def __init__(self, app, tab):
        self.app = app
        self.tree = make_tree(tab, ("ID", "Code", "Resource"), (50, 150, 250))

        form = ttk.Frame(tab, padding=5)
        form.pack(fill="x")
        self.code_var = tk.StringVar()
        self.name_var = tk.StringVar()
        ttk.Label(form, text="Code:").pack(side="left")
        ttk.Entry(form, textvariable=self.code_var, width=12).pack(side="left", padx=4)
        ttk.Label(form, text="Name:").pack(side="left")
        ttk.Entry(form, textvariable=self.name_var, width=22).pack(side="left", padx=4)

        buttons = ttk.Frame(tab)
        buttons.pack(pady=8)
        ttk.Button(buttons, text="Add", command=self.add).pack(side="left", padx=5)
        ttk.Button(buttons, text="Update name", command=self.update).pack(side="left", padx=5)
        ttk.Button(buttons, text="Remove", command=self.remove).pack(side="left", padx=5)
        self.refresh()

    def refresh(self):
        rows = []
        for r in db.get_resources(self.app.campus["id"]):
            rows.append((r["id"], r["code"], r["name"]))
        fill_tree(self.tree, rows)

    def selected_id(self):
        selected = self.tree.selection()
        if not selected:
            messagebox.showwarning("Resources", "Select a resource first.")
            return None
        return self.tree.item(selected[0])["values"][0]

    def add(self):
        ok, message = db.add_resource(self.code_var.get(), self.name_var.get(),
                                      self.app.campus["id"])
        show_message("Resources", ok, message)
        self.refresh()

    def update(self):
        resource_id = self.selected_id()
        if resource_id is None:
            return
        ok, message = db.update_resource(resource_id, self.name_var.get())
        show_message("Resources", ok, message)
        self.refresh()

    def remove(self):
        resource_id = self.selected_id()
        if resource_id is None:
            return
        if messagebox.askyesno("Remove", "Remove this resource?"):
            ok, message = db.remove_resource(resource_id)
            show_message("Resources", ok, message)
            self.refresh()
