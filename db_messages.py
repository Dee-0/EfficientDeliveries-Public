import sqlite3
from datetime import datetime


# Send a message
def send_message(from_user, to_user, text, message_date, message_time):
    with sqlite3.connect("database.db") as messages:
        cursor = messages.cursor()
        from_user = from_user.lower()
        cursor.execute(
            "INSERT INTO messages(from_user, to_user, text, message_date, message_time, mark_read) VALUES(?, ?, ?, ?, ?, ?)",
            (from_user, to_user, text, message_date, message_time, 0))
        messages.commit()
        return True
    return False


# Get all messages
def get_all_messages(username):
    with sqlite3.connect("database.db") as messages:
        cursor = messages.cursor()
        cursor.execute(f"SELECT * FROM messages WHERE to_user = '{username}'")
        messages = cursor.fetchall()
        messages = messages[::-1]
        return messages


# Get possible recipients to message
def get_possible_recipients(company_id):
    with sqlite3.connect("database.db") as recipients:
        cursor = recipients.cursor()
        if company_id == -1:
            cursor.execute(f"SELECT * FROM users")
            print("ye")
        else:
            cursor.execute(f"SELECT * FROM users WHERE company_id = {company_id} OR user_type = 1")
        recipients = cursor.fetchall()
        return recipients


# Set message as read
def set_message_read(message_id):
    with sqlite3.connect("database.db") as messages:
        cursor = messages.cursor()
        cursor.execute(f"UPDATE messages SET mark_read = 1 WHERE id = {message_id}")
        messages.commit()
        return True
    return False


# Get all sent messages
def get_all_sent_messages(username):
    with sqlite3.connect("database.db") as messages:
        cursor = messages.cursor()
        cursor.execute(f"SELECT * FROM messages WHERE from_user = '{username}'")
        messages = cursor.fetchall()
        messages = messages[::-1]
        return messages


