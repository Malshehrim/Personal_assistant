import json
import os
from datetime import datetime

# ==========================================
# 📂 DATA MANAGER (Handling Files)
# ==========================================
# This file handles saving and loading tasks from the 'tasks.json' file.
# It acts as a bridge between our App and the stored data.

# The name of the file where we save tasks
DATA_FILE = 'tasks.json'

def load_tasks():
    """
    Reads tasks from the JSON file.
    Returns an empty list [] if the file does not exist.
    """
    # 1. Check if the file exists on the computer
    if not os.path.exists(DATA_FILE):
        return []  # Return empty list if no file found

    try:
        # 2. Open the file in 'read' mode ('r')
        # We use utf-8 encoding to support all languages (like Arabic)
        with open(DATA_FILE, 'r', encoding='utf-8') as f:
            return json.load(f)  # Convert JSON text back into a Python list
    except (json.JSONDecodeError, IOError):
        return []  # If there is an error, return empty list

def save_tasks(tasks):
    """
    Saves the list of tasks into the JSON file.
    """
    # Open file in 'write' mode ('w')
    with open(DATA_FILE, 'w', encoding='utf-8') as f:
        # 'indent=4' makes the file easy for humans to read
        json.dump(tasks, f, indent=4, ensure_ascii=False)

def add_task(title, description, due_date):
    """
    Creates a new task and saves it.
    """
    tasks = load_tasks()  # Step 1: Get current tasks

    # Step 2: Create a new task dictionary
    new_task = {
        'id': len(tasks) + 1,  # Generate a simple ID
        'title': title,
        'description': description,
        'due_date': due_date,
        'status': 'pending',  # Default status is 'pending' (waiting)
        'created_at': datetime.now().isoformat()
    }

    # Step 3: Add to list and save
    tasks.append(new_task)
    save_tasks(tasks)
    return new_task

def toggle_task(task_id):
    """
    Switches a task's status between 'pending' and 'completed'.
    """
    tasks = load_tasks()
    
    # Find the task with the matching ID
    for task in tasks:
        if task['id'] == int(task_id):
            # Swap the status
            if task['status'] == 'pending':
                task['status'] = 'completed'
            else:
                task['status'] = 'pending'
            break  # Stop searching once found
            
    save_tasks(tasks)  # Save changes!

def get_tasks_by_type():
    """
    Organizes tasks into three groups:
    1. Upcoming (Future)
    2. Previous (Past/Overdue)
    3. Completed
    """
    tasks = load_tasks()
    
    upcoming = []
    previous = []
    completed = []
    
    # Get today's date for comparison
    today = datetime.now().date()
    
    for task in tasks:
        # 1. Check if completed first
        if task['status'] == 'completed':
            completed.append(task)
            continue
            
        # 2. If not completed, check the date
        try:
            # Convert string date 'YYYY-MM-DD' to Python Date
            task_date = datetime.strptime(task['due_date'], '%Y-%m-%d').date()
            
            if task_date < today:
                previous.append(task) # Date is in the past
            else:
                upcoming.append(task) # Date is today or future
        except ValueError:
            # If date format is wrong, default to upcoming
            upcoming.append(task)
            
    # Sort the lists to look nice
    # Upcoming: Nearest date first
    upcoming.sort(key=lambda x: x['due_date'])
    # Previous: Newest (closest to today) first
    previous.sort(key=lambda x: x['due_date'], reverse=True)
    
    return {
        'upcoming': upcoming,
        'previous': previous,
        'completed': completed
    }
