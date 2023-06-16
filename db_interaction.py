import sqlite3


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
