import sqlite3


# Add user to database
def add_user(user_type, username, password, firstName, lastName, email, company_id):
    with sqlite3.connect("database.db") as users:
        cursor = users.cursor()
        cursor.execute(
            "INSERT INTO users(user_type, username, password, firstName, lastName, email, company_id) VALUES(?, ?, ?, ?, ?, ?, ?)",
            (user_type, username, password, firstName, lastName, email, company_id))
        users.commit()
        return True
    return False


# Get all drivers by company id
def get_all_drivers(company_id):
    with sqlite3.connect("database.db") as users:
        cursor = users.cursor()
        if company_id == -1:
            cursor.execute(f"SELECT * FROM users WHERE user_type = 3")
        else:
            cursor.execute(f"SELECT * FROM users WHERE user_type = 3 AND company_id = {company_id}")
        drivers = cursor.fetchall()
        return drivers


# Get a driver by id
def get_driver_by_id(driver_id):
    with sqlite3.connect("database.db") as users:
        cursor = users.cursor()
        cursor.execute(f"SELECT username FROM users WHERE id = {driver_id}")
        driver = cursor.fetchall()
        driver = driver[0][0]
        return driver


# Remove a driver
def remove_driver(username):
    with sqlite3.connect("database.db") as users:
        cursor = users.cursor()
        cursor.execute(f"DELETE FROM users WHERE username = '{username}'")
        users.commit()
        with sqlite3.connect("database.db") as routes:
            cursor2 = routes.cursor()
            cursor2.execute(f"UPDATE routes SET assigned_to = -1 WHERE assigned_to = '{username}'")
        return True
    return False


# Get all managers from database
def get_all_managers():
    with sqlite3.connect("database.db") as users:
        cursor = users.cursor()
        cursor.execute(f"SELECT * FROM users WHERE user_type = 2")
        managers = cursor.fetchall()
        return managers

# Remove a manager
def remove_manager(username):
    with sqlite3.connect("database.db") as users:
        cursor = users.cursor()
        cursor.execute(f"DELETE FROM users WHERE username = '{username}'")
        users.commit()
        return True
    return False