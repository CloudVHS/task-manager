import tkinter as tk
from tkinter import ttk
from storage import load_tasks, save_tasks

# ================= ЛОГИКА =================

def add_task():
    text = entry.get().strip()
    deadline = deadline_entry.get().strip()

    if not text:
        return
    if deadline == "" or "Дедлайн" in deadline:
        deadline = "-"

    task = f"[ ] {text}"
    if deadline and "Дедлайн" not in deadline:
        task += f" (до {deadline})"

    tree.insert("", tk.END, values=("⬜", text, deadline))
    entry.delete(0, tk.END)
    deadline_entry.delete(0, tk.END)
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
        tree.insert("", tk.END, values=(done, text, deadline))

# ================= GUI =================

root = tk.Tk()
root.title("Task Manager")
root.geometry("450x500")

entry = tk.Entry(root, width=40)
entry.pack(pady=10)
deadline_entry = tk.Entry(root, width=40)
deadline_entry.insert(0, "Дедлайн (например 10.02.2026)")
deadline_entry.pack(pady=5)


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

tree.heading("done", text="")
tree.heading("task", text="Задача")
tree.heading("deadline", text="Дедлайн")

tree.column("done", width=40, anchor="center")
tree.column("task", width=250)
tree.column("deadline", width=120, anchor="center")

tree.pack(pady=10)
tree.bind("<ButtonRelease-1>", toggle_done)

load_all_tasks()
root.mainloop()
