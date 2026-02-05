import tkinter as tk
from storage import load_tasks, save_tasks

def add_task():
    task = entry.get()

    if task.strip() == "":
        return

    listbox.insert(tk.END, task)
    entry.delete(0, tk.END)
    save_all_tasks()

def delete_task():
    selected = listbox.curselection()

    if not selected:
        return

    index = selected[0]
    listbox.delete(index)
    save_all_tasks()

def save_all_tasks():
    tasks = list(listbox.get(0, tk.END))
    save_tasks(tasks)

def load_all_tasks():
    tasks = load_tasks()
    for task in tasks:
        listbox.insert(tk.END, task)

root = tk.Tk()
root.title("Task Manager")
root.geometry("400x500")

entry = tk.Entry(root, width=40)
entry.pack(pady=10)

add_button = tk.Button(root, text="Добавить задачу", command=add_task)
add_button.pack(pady=5)

delete_button = tk.Button(root, text="Удалить выбранную", command=delete_task)
delete_button.pack(pady=5)

listbox = tk.Listbox(root, width=50, height=15)
listbox.pack(pady=10)

load_all_tasks()
root.mainloop()
