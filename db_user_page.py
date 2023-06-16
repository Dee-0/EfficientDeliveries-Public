import sqlite3
from werkzeug.security import generate_password_hash, check_password_hash


# Check login credentials
def login_check(username, password):
    with sqlite3.connect("database.db") as users:
        cursor = users.cursor()
        cursor.execute('SELECT * FROM users')
        users = cursor.fetchall()
        for user in users:
            if username == user[2]:
                print("Found user! checking password...")
                if check_password_hash(user[3], password):
                    print("Logged in!")
                    user_id = user[0]
                    user_type = user[1]
                    username = user[2]
                    first_name = user[4]
                    last_name = user[5]
                    company_id = user[7]
                    email = user[6]
                    return True, user_id, user_type, username, first_name, last_name, company_id, email
        return False, -1, -1, -1, -1, -1, -1, -1


# Check password hash to new password input to confirm its the same password
def confirm_pasword(username, old_password, new_password):
    with sqlite3.connect("database.db") as users:
        cursor = users.cursor()
        cursor.execute("SELECT * FROM users")
        users = cursor.fetchall()
        for user in users:
            if username == user[2]:
                if check_password_hash(user[3], old_password):
                    new_password = generate_password_hash(new_password)
                    with sqlite3.connect("database.db") as users:
                        cursor = users.cursor()
                        cursor.execute(f"UPDATE users SET password = '{new_password}' WHERE username = '{username}'")
                        users.commit()
                        return True
    return False