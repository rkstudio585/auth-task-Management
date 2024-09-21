import re
import hashlib
import sqlite3

# Initialize SQLite Database
conn = sqlite3.connect('task_manager.db')
cursor = conn.cursor()

# Create users and tasks tables if they don't already exist
cursor.execute('''CREATE TABLE IF NOT EXISTS users (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    email TEXT NOT NULL UNIQUE,
                    password TEXT NOT NULL)''')

cursor.execute('''CREATE TABLE IF NOT EXISTS tasks (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id INTEGER,
                    task TEXT NOT NULL,
                    FOREIGN KEY(user_id) REFERENCES users(id))''')
conn.commit()

# Global variable to keep track of the logged-in user
logged_in_user = None

# Hashing Password using SHA-256
def hash_password(password: str) -> str:
    return hashlib.sha256(password.encode()).hexdigest()

# Email validation using Regular Expression
def validate_email(email: str) -> bool:
    regex = r'^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$'
    return re.match(regex, email) is not None

# Register user and store details in SQLite3
def register():
    global logged_in_user

    print("\n--- Register a New Account ---")
    email = input("Enter your email: ")
    password = input("Enter your password (min 8 characters): ")
    confirm_password = input("Confirm your password: ")

    if validate_email(email):
        if password and len(password) >= 8:
            if password == confirm_password:
                hashed_password = hash_password(password)
                try:
                    cursor.execute('INSERT INTO users (email, password) VALUES (?, ?)', 
                                   (email, hashed_password))
                    conn.commit()
                    print("Account created successfully!")
                    logged_in_user = email
                    home_page()
                except sqlite3.IntegrityError:
                    print("An account with this email already exists.")
            else:
                print("Passwords do not match.")
        else:
            print("Password must be at least 8 characters long.")
    else:
        print("Invalid email format.")

# Login user by checking credentials from SQLite3
def login():
    global logged_in_user

    print("\n--- Login to Your Account ---")
    email = input("Enter your email: ")
    password = input("Enter your password: ")

    if validate_email(email):
        if password and len(password) >= 8:
            hashed_password = hash_password(password)
            cursor.execute('SELECT * FROM users WHERE email = ? AND password = ?', (email, hashed_password))
            user = cursor.fetchone()
            if user:
                print("Login successful!")
                logged_in_user = email
                home_page()
            else:
                print("Invalid email or password.")
        else:
            print("Password must be at least 8 characters long.")
    else:
        print("Invalid email format.")

# Create a new task
def create_task(user_id):
    task = input("Enter your task: ")
    if task:
        cursor.execute('INSERT INTO tasks (user_id, task) VALUES (?, ?)', (user_id, task))
        conn.commit()
        print("Task added successfully!")
    else:
        print("Task cannot be empty.")

# View tasks for the logged-in user
def view_tasks(user_id):
    cursor.execute('SELECT * FROM tasks WHERE user_id = ?', (user_id,))
    tasks = cursor.fetchall()
    if tasks:
        print("\nYour Tasks:")
        for task in tasks:
            print(f"{task[0]}: {task[2]}")
    else:
        print("No tasks found.")

# Delete a task
def delete_task(user_id):
    view_tasks(user_id)
    try:
        task_id = int(input("Enter the task ID to delete: "))
        cursor.execute('DELETE FROM tasks WHERE id = ? AND user_id = ?', (task_id, user_id))
        conn.commit()
        print("Task deleted successfully!")
    except ValueError:
        print("Invalid task ID.")

# Home Page where users can manage tasks
def home_page():
    global logged_in_user

    cursor.execute('SELECT id FROM users WHERE email = ?', (logged_in_user,))
    user_id = cursor.fetchone()[0]

    print(f"\n--- Welcome to your Task Manager, {logged_in_user} ---")
    while True:
        action = input("\nType 'create' to add a task, 'view' to see tasks, 'delete' to remove a task, or 'logout' to log out: ").strip().lower()
        
        if action == "create":
            create_task(user_id)
        elif action == "view":
            view_tasks(user_id)
        elif action == "delete":
            delete_task(user_id)
        elif action == "logout":
            logout()
            break
        else:
            print("Invalid command. Please try again.")

# Logout function
def logout():
    global logged_in_user
    print(f"Goodbye, {logged_in_user}. You have logged out.")
    logged_in_user = None

# Help function to show how to use the program
def show_help():
    print("""
    --- Help Menu ---
    Welcome to the Task Management System!

    You can perform the following actions:
    
    1. Register - Create a new account.
    2. Login - Log into your existing account.
    3. Create Task - Add a new task to your list.
    4. View Tasks - See all your tasks.
    5. Delete Task - Remove a task from your list.
    6. Logout - Log out from your account.

    To use these actions, type one of the following commands:
    - 'register' to create a new account.
    - 'login' to log into your account.
    - 'create' to add a new task.
    - 'view' to see your tasks.
    - 'delete' to remove a task.
    - 'help' to show this help message.
    - 'exit' to quit the program.
    """)

# Main function to handle user input and execute corresponding actions
def main():
    show_help()
    while True:
        action = input("\nEnter a command (register/login/help/exit): ").strip().lower()
        
        if action == "register":
            register()
        elif action == "login":
            login()
        elif action == "help":
            show_help()
        elif action == "exit":
            print("Exiting the program. Goodbye!")
            break
        else:
            print("Invalid command. Type 'help' to see available options.")
    
if __name__ == "__main__":
    main()

# Close the database connection when done
conn.close()
