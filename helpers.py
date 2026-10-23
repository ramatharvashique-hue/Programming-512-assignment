"""helpers.py - Small helpers used by several screens."""
from tkinter import ttk, messagebox


def make_tree(parent, columns, widths):
    """Create a table (Treeview) with a scrollbar."""
    frame = ttk.Frame(parent)
    tree = ttk.Treeview(frame, columns=columns, show="headings", height=10)
    for i in range(len(columns)):
        tree.heading(columns[i], text=columns[i])
        tree.column(columns[i], width=widths[i])
    bar = ttk.Scrollbar(frame, orient="vertical", command=tree.yview)
    tree.configure(yscrollcommand=bar.set)
    tree.pack(side="left", fill="both", expand=True)
    bar.pack(side="right", fill="y")
    frame.pack(fill="both", expand=True)
    return tree


def fill_tree(tree, rows):
    """Replace the rows of a table."""
    for item in tree.get_children():
        tree.delete(item)
    for row in rows:
        tree.insert("", "end", values=row)


def show_message(title, ok, message):
    """Show a success message if ok is True, otherwise an error message."""
    if ok:
        messagebox.showinfo(title, message)
    else:
        messagebox.showerror(title, message)
