import tkinter as tk
from tkinter import ttk
from storage import load_tasks, save_tasks
from datetime import datetime, date
from tkcalendar import Calendar

# ================= LOGIC =================
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


calendar_button = tk.Button(
    root,
    text="📅 Выбрать дедлайн",
    command=open_calendar
)
calendar_button.pack(pady=2)

add_button = tk.Button(root, text="Add", command=add_task)
delete_button = tk.Button(root, text="Delete", command=delete_task)

add_button.pack(pady=2)
delete_button.pack(pady=2)

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
root.mainloop()
