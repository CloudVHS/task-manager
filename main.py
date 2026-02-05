import tkinter as tk
from tkinter import ttk
from storage import load_tasks, save_tasks

# ================= ЛОГИКА =================

def add_task():
    text = entry.get().strip()
    if not text:
        return

    tree.insert("", tk.END, values=("⬜", text))
    entry.delete(0, tk.END)
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

    # реагируем ТОЛЬКО на первый столбец (чекбокс)
    if column != "#1" or not item_id:
        return

    done, text = tree.item(item_id, "values")

    done = "☑" if done == "⬜" else "⬜"
    tree.item(item_id, values=(done, text))
    save_all_tasks()

def save_all_tasks():
    tasks = []
    for item in tree.get_children():
        tasks.append(tree.item(item, "values"))
    save_tasks(tasks)

def load_all_tasks():
    for done, text in load_tasks():
        tree.insert("", tk.END, values=(done, text))

# ================= GUI =================

root = tk.Tk()
root.title("Task Manager")
root.geometry("450x500")

entry = tk.Entry(root, width=40)
entry.pack(pady=10)

add_button = tk.Button(root, text="Add", command=add_task)
delete_button = tk.Button(root, text="Delete", command=delete_task)

add_button.pack(pady=2)
delete_button.pack(pady=2)

tree = ttk.Treeview(root, columns=("done", "task"), show="headings", height=15)
tree.heading("done", text="")
tree.heading("task", text="Задача")
tree.column("done", width=40, anchor="center")
tree.column("task", width=350)

tree.pack(pady=10)
tree.bind("<Button-1>", toggle_done)

load_all_tasks()
root.mainloop()
