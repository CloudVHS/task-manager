import tkinter as tk
from tkinter import ttk
from storage import load_tasks, save_tasks
from datetime import datetime, date
from tkcalendar import Calendar
import json
import os

# ================= SETTINGS =================
SETTINGS_FILE = "settings.json"

def load_settings():
    if not os.path.exists(SETTINGS_FILE):
        return {"theme": "light"}

    try:
        with open(SETTINGS_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return {"theme": "light"}


def save_settings():
    with open(SETTINGS_FILE, "w", encoding="utf-8") as f:
        json.dump(
            {"theme": current_theme},
            f,
            ensure_ascii=False,
            indent=2
        )

# ================= THEME =================
THEMES = {
    "light": {
        "bg": "#f5f5f5",
        "fg": "#000000",

        "entry_bg": "#ffffff",

        "button_bg": "#e0e0e0",
        "button_hover": "#d0d0d0",
        "button_fg": "#000000",

        "tree_bg": "#ffffff",
        "tree_fg": "#000000"
    },

    "dark": {
        "bg": "#2b2b2b",
        "fg": "#ffffff",

        "entry_bg": "#3a3a3a",

        "button_bg": "#3a3a3a",
        "button_hover": "#2f2f2f",
        "button_fg": "#ffffff",

        "tree_bg": "#3f3f3f",
        "tree_fg": "#ffffff"
    }
}

settings = load_settings()
current_theme = settings.get("theme", "light")

# ================= LOGIC =================
def apply_theme():
    theme = THEMES[current_theme]

    root.configure(bg=theme["bg"])

    entry.configure(bg=theme["entry_bg"], fg=theme["fg"])
    deadline_entry.configure(readonlybackground=theme["entry_bg"], fg=theme["fg"])

    no_deadline_check.configure(bg=theme["bg"], fg=theme["fg"])

    style = ttk.Style()
    style.theme_use("clam")

    # Treeview
    style.configure(
        "Treeview",
        background=theme["tree_bg"],
        foreground=theme["tree_fg"],
        fieldbackground=theme["tree_bg"]
    )

    style.map(
        "Treeview",
        background=[("selected", "#6a9fb5")],
        foreground=[("selected", "#ffffff")]
    )
    style.configure(
        "Treeview.Heading",
        background=theme["button_bg"],
        foreground=theme["tree_fg"],
        relief="flat"
    )

    style.map(
        "Treeview.Heading",
        background=[
            ("active", theme["button_hover"])
        ]
    )

    for widget in root.winfo_children():
        if isinstance(widget, tk.Button):
            widget.configure(
                bg=theme["button_bg"],
                fg=theme["button_fg"],
                activebackground=theme["button_hover"],
                activeforeground=theme["button_fg"],
                relief="flat",
                bd=0,
                highlightthickness=0,
                highlightbackground=theme["bg"]
            )

def on_button_enter(event):
    theme = THEMES[current_theme]
    event.widget.configure(bg=theme["button_hover"])


def on_button_leave(event):
    theme = THEMES[current_theme]
    event.widget.configure(bg=theme["button_bg"])

def open_settings():
    settings = tk.Toplevel(root)
    settings.title("Настройки")
    settings.geometry("250x150")
    settings.resizable(False, False)

    var = tk.StringVar(value=current_theme)

    def change_theme():
        global current_theme
        current_theme = var.get()
        apply_theme()
        save_settings()

    tk.Label(
        settings,
        text="Тема оформления"
    ).pack(pady=10)

    tk.Radiobutton(
        settings,
        text="Светлая",
        variable=var,
        value="light",
        command=change_theme
    ).pack(anchor="w", padx=20)

    tk.Radiobutton(
        settings,
        text="Тёмная",
        variable=var,
        value="dark",
        command=change_theme
    ).pack(anchor="w", padx=20)

def on_date_selected(event):
    root.focus_set()

def block_typing(event):
    return "break"

def open_calendar():
    cal_win = tk.Toplevel(root)
    cal_win.title("Выбор дедлайна")
    cal_win.resizable(False, False)
    cal_win.grab_set()  # grab ТОЛЬКО для этого окна

    cal = Calendar(
        cal_win,
        selectmode="day",
        date_pattern="dd.mm.yyyy"
    )
    cal.pack(padx=10, pady=10)

    def set_date():
        selected = cal.get_date()
        deadline_var.set(selected)
        cal_win.destroy()

    tk.Button(
        cal_win,
        text="OK",
        command=set_date
    ).pack(pady=5)

    cal_win.protocol("WM_DELETE_WINDOW", cal_win.destroy)

def normalize_deadline(deadline_str):
    if not deadline_str:
        return "-"

    deadline_str = deadline_str.strip()

    if deadline_str.lower() in ("дедлайн", "dd.mm.yyyy", "дд.мм.гггг"):
        return "-"

    try:
        deadline_date = datetime.strptime(deadline_str, "%d.%m.%Y").date()
    except ValueError:
        return "-"

    if deadline_date < date.today():
        return "-"

    return deadline_date.strftime("%d.%m.%Y")

def is_overdue(deadline):
    if deadline == "-" or not deadline:
        return False

    deadline_date = datetime.strptime(deadline, "%d.%m.%Y").date()
    return deadline_date < date.today()

def add_task():
    text = entry.get().strip()
    if not text:
        return

    deadline = deadline_var.get()

    tree.insert("", tk.END, values=("⬜", text, deadline))

    entry.delete(0, tk.END)
    deadline_var.set("-")
    no_deadline_var.set(False)

    save_all_tasks()

def delete_task():
    selected = tree.selection()
    if not selected:
        return
    tree.delete(selected[0])
    save_all_tasks()

def toggle_done(event):
    item_id = tree.identify_row(event.y)
    column = tree.identify_column(event.x)

    if not item_id or column != "#1":
        return

    done, text, deadline = tree.item(item_id, "values")

    done = "☑" if done == "⬜" else "⬜"

    tree.item(item_id, values=(done, text, deadline))
    save_all_tasks()

def save_all_tasks():
    tasks = []
    for item in tree.get_children():
        tasks.append(tree.item(item, "values"))
    save_tasks(tasks)

def load_all_tasks():
    for done, text, deadline in load_tasks():
        tags = ()
        if is_overdue(deadline):
            tags = ("overdue",)
        tree.insert("", tk.END, values=(done, text, deadline), tags=tags)

# ================= GUI =================

root = tk.Tk()
root.title("Task Manager")
root.geometry("450x500")

entry = tk.Entry(root, width=40)
entry.pack(pady=10)

deadline_var = tk.StringVar(value="-")

deadline_entry = tk.Entry(
    root,
    textvariable=deadline_var,
    state="readonly",
    width=15,
    justify="center"
)
deadline_entry.pack(pady=5)

def toggle_no_deadline():
    if no_deadline_var.get():
        deadline_var.set("-")

no_deadline_var = tk.BooleanVar()
no_deadline_check = tk.Checkbutton(
    root,
    text="Без дедлайна",
    variable=no_deadline_var,
    command=toggle_no_deadline
)
no_deadline_check.pack()

calendar_button = ttk.Button(root, text="📅 Выбрать дедлайн", command=open_calendar)
calendar_button.pack(pady=2)
add_button = ttk.Button(root, text="Add", command=add_task)
add_button.pack(pady=2)
delete_button = ttk.Button(root, text="Delete", command=delete_task)
delete_button.pack(pady=2)
settings_button = ttk.Button(root, text="⚙ Настройки", command=open_settings)
settings_button.pack(pady=5)

tree = ttk.Treeview(
    root,
    columns=("done", "task", "deadline"),
    show="headings",
    height=15
)

tree.tag_configure("overdue", foreground="red")
tree.heading("done", text="")
tree.heading("task", text="Задача")
tree.heading("deadline", text="Дедлайн")

tree.column("done", width=40, anchor="center")
tree.column("task", width=250)
tree.column("deadline", width=120, anchor="center")

tree.pack(pady=10)
tree.bind("<ButtonRelease-1>", toggle_done)
deadline_entry.bind("<<DateEntrySelected>>", on_date_selected)
deadline_entry.bind("<Key>", block_typing)

load_all_tasks()
apply_theme()
root.mainloop()
