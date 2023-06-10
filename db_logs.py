import sqlite3


# Add to log
def add_to_log(user_type, company_id, by_user, action, date, time, is_successful, log_type):
    # user_type, company_id, by_user, action, date, time, is_successful
    # date, time = get_current_time_date()
    # add_to_log(session['user_type'], session['company_id'], session['username'], f"Route {route} assigned to {driver}", date, time, successful)
    with sqlite3.connect("database.db") as logs:
        cursor = logs.cursor()
        cursor.execute(
            "INSERT INTO logs(user_type, company_id, by_user, action, date, time, is_successful, log_type) VALUES(?, ?, ?, ?, ?, ?, ?, ?)",
            (user_type, company_id, by_user, action, date, time, is_successful, log_type))
        logs.commit()
        return True
    return False


# Get all logs
def get_all_logs(user_type, company_id):
    with sqlite3.connect("database.db") as logs:
        cursor = logs.cursor()
        if user_type == 1:
            cursor.execute("SELECT * FROM logs")
        else:
            cursor.execute(f"SELECT * FROM logs WHERE company_id = {company_id}")
        logs = cursor.fetchall()
        logs = logs[::-1]
        return logs



# Get all logs by log type
def get_logs_by_type(user_type, company_id, log_type):
    with sqlite3.connect("database.db") as logs:
        cursor = logs.cursor()
        if user_type == 1:
            cursor.execute(f"SELECT * FROM logs WHERE log_type = {log_type}")
        elif company_id != -1:
            cursor.execute(f"SELECT * FROM logs WHERE company_id = {company_id} AND log_type = {log_type}")
        logs = cursor.fetchall()
        logs = logs[::-1]
        return logs