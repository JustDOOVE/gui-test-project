import tkinter as tk
from tkinter import ttk
import sqlite3
import datetime
from tkcalendar import Calendar
from ttkthemes import ThemedStyle


def add_task() -> None:
    """adds a task to the database"""
    task_text = entry.get()
    selected_date = cal.get_date()
    if not selected_date:
        tk.messagebox.showwarning("Attention", "Please select a date before adding a task.")
        return
    if task_text:
        cursor.execute("INSERT INTO tasks (task, date) VALUES (?, ?)", (task_text, selected_date))
        conn.commit()
        entry.delete(0, tk.END)
        update_task_list(selected_date)


def select_date() -> None:
    """shows a list of tasks for a date"""
    selected_date = cal.get_date()
    update_task_list(selected_date)
    date_label.config(text=f"TASKS FOR {selected_date}")


def update_task_list(selected_date=None) -> None:
    """updates the task list"""
    task_tree.delete(*task_tree.get_children())
    if selected_date:
        cursor.execute("SELECT id, task, date FROM tasks WHERE date=?", (selected_date,))
    else:
        date_label.config(text="SHOWED ALL TASKS")
        cursor.execute("SELECT id, task, date FROM tasks ORDER BY date DESC")
    tasks = cursor.fetchall()
    row = 1
    if not tasks:
        task_tree.insert("", "end", values=("", "no tasks for this date", ""))
    else:
        for task in tasks:
            task_tree.insert("", "end", values=(row, task[1], task[2]), iid=task[0])
            row += 1


def check_records_count():
    """compares the number of tasks in the task list and the database"""
    cursor.execute("SELECT COUNT(*) FROM tasks")
    db_record_count = cursor.fetchone()[0]
    tree_record_count = len(task_tree.get_children())
    if tree_record_count - db_record_count == 1 or tree_record_count - db_record_count == 0:
        return True
    elif db_record_count - tree_record_count == 1:
        return False


def remove_task() -> None:
    """Deletes the selected task"""
    selected_item = task_tree.selection()
    task_values = task_tree.item(selected_item, "values")
    if selected_item:
        task = task_values[1]
        date = task_values[2]
        task_id = selected_item[0]
        removed_tasks.clear()
        removed_tasks.append((task, date))
        cursor.execute("DELETE FROM tasks WHERE id=?", (task_id,))
        conn.commit()
    if check_records_count():
        update_task_list()
        return
    selected_date = cal.get_date()
    update_task_list(selected_date)


def undo_remove_task():
    """cancels deletion of the last task"""
    if removed_tasks:
        task_text, task_date = removed_tasks.pop()
        cursor.execute("INSERT INTO tasks (task, date) VALUES (?, ?)", (task_text, task_date))
        conn.commit()
        if check_records_count() is False:
            update_task_list()
            return
        selected_date = cal.get_date()
        update_task_list(selected_date)


def remove_old_tasks(cursor):
    """when program was started automatically remove 2 days old tasks from database"""
    current_date = datetime.datetime.now()
    two_days_ago = current_date - datetime.timedelta(days=2)
    cursor.execute("DELETE FROM tasks WHERE date < ?", (two_days_ago.strftime("%d/%m/%Y"),))
    conn.commit()


def has_tasks_on_date(selected_date) -> bool:
    """check how any tasks on selected day"""
    cursor.execute("SELECT COUNT(*) FROM tasks WHERE date=?", (selected_date,))
    count = cursor.fetchone()[0]
    return count > 0


def edit_task():
    pass


# db creator
conn = sqlite3.connect('todo_list.db')
cursor = conn.cursor()

cursor.execute('''
   CREATE TABLE IF NOT EXISTS tasks (
       id INTEGER PRIMARY KEY AUTOINCREMENT,
       task TEXT,
       date TEXT
   )
''')
conn.commit()


# main
root = tk.Tk()
root.title("TASK MANAGER")
root.configure(bg="#365B5B")

# program name
title_label = tk.Label(root, text="Daily task manager", font=("Helvetica", 16), bg="#365B5B", fg="white")
title_label.pack(pady=(10, 0))


# entry and upper button
button_frame_upper = tk.Frame(root, bg=root.cget("bg"))
button_frame_upper.pack()
entry = tk.Entry(button_frame_upper, width=60, font=("Helvetica", 13), bd=2, relief=tk.RIDGE)
entry.pack(padx=10, pady=10)
add_button = tk.Button(button_frame_upper, text="Add task", command=add_task, width=15)
add_button.pack(pady=(0, 10))


# calendar
cal = Calendar(root, date_pattern='dd/mm/yyyy')
cal.pack(side=tk.LEFT, padx=(10, 10), pady=10)
cal.bind("<<CalendarSelected>>", lambda event=None: select_date())

date_label = tk.Label(root, text="", font=("Helvetica", 14), bg="#365B5B", fg="white")
date_label.pack(pady=(0, 10))


# table
task_tree = tk.ttk.Treeview(root, columns=("N", "Task", "Date"), show="headings", height=12)
task_tree.heading("N", text="N")
task_tree.heading("Task", text="Task")
task_tree.heading("Date", text="Date")
task_tree.pack(padx=(0, 10))
task_tree.column("N", width=50, anchor="center")
task_tree.column("Task", width=354, anchor="center")
task_tree.column("Date", width=70, anchor="center")


# lower buttons frame
button_frame_lower = tk.Frame(root, bg=root.cget("bg"))
button_frame_lower.pack(pady=10)
remove_button = tk.Button(button_frame_lower, text="Delete task", command=remove_task, width=15)
remove_button.pack(side=tk.LEFT, padx=20)
undo_remove_button = tk.Button(button_frame_lower, text="Cancel deletion", command=undo_remove_task, width=15)
undo_remove_button.pack(side=tk.LEFT, padx=20)
show_all_button = tk.Button(button_frame_lower, text="Show all tasks", command=update_task_list, width=15)
show_all_button.pack(side=tk.LEFT, padx=20)


# other
removed_tasks = []
remove_old_tasks(cursor)
update_task_list()
root.mainloop()
