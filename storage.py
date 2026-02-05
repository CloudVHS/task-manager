import json
import os

FILE_NAME = "tasks.json"

def load_tasks():
    if not os.path.exists(FILE_NAME):
        return []

    with open(FILE_NAME, "r", encoding="utf-8") as file:
        return json.load(file)

def save_tasks(tasks):
    with open(FILE_NAME, "w", encoding="utf-8") as file:
        json.dump(tasks, file, ensure_ascii=False, indent=2)
