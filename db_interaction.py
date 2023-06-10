import sqlite3

connect = sqlite3.connect("database.db", check_same_thread=False)
connect.execute(
    "CREATE TABLE IF NOT EXISTS users (id INTEGER PRIMARY KEY AUTOINCREMENT, user_type INTEGER, username, password, firstName, lastName, "
    "email, company_id INTEGER)")
connect.execute(
    "CREATE TABLE IF NOT EXISTS companies (id INTEGER PRIMARY KEY AUTOINCREMENT, company_name, company_address, company_email, "
    "company_phone)")
connect.execute(
    "CREATE TABLE IF NOT EXISTS routes (id INTEGER PRIMARY KEY AUTOINCREMENT, company_id INTEGER, requested_by, assigned_to, origin, destinations, "
    "distance, date, time, file_name, completed DEFAULT 0)")
connect.execute(
    "CREATE TABLE IF NOT EXISTS messages (id INTEGER PRIMARY KEY AUTOINCREMENT, from_user, to_user, text, message_date, message_time, mark_read)")
# 1 - Route, 2 - Users, 3 - Messages, 4 - User_page
connect.execute(
    "CREATE TABLE IF NOT EXISTS logs (id INTEGER PRIMARY KEY AUTOINCREMENT, user_type INTEGER, company_id INTEGER, by_user, action, date, time, is_successful, log_type INTEGER)")


def get_all_drivers_and_companies(company_id):
    with sqlite3.connect("database.db") as users:
        cursor = users.cursor()
        if company_id == -1:
            cursor.execute(f"SELECT * FROM users WHERE user_type = 3")
            drivers = cursor.fetchall()
        else:
            cursor.execute(f"SELECT * FROM users WHERE user_type = 3 AND company_id = {company_id}")
            drivers = cursor.fetchall()
    with sqlite3.connect("database.db") as companies:
        cursor = companies.cursor()
        cursor.execute(f"SELECT * FROM companies")
        companies = cursor.fetchall()
    return drivers, companies



def get_all_managers_and_companies():
    with sqlite3.connect("database.db") as users:
        cursor = users.cursor()
        cursor.execute(f"SELECT * FROM users WHERE user_type = 2")
        managers = cursor.fetchall()
    with sqlite3.connect("database.db") as companies:
        cursor = companies.cursor()
        cursor.execute(f"SELECT * FROM companies")
        companies = cursor.fetchall()
    return managers, companies
