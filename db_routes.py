import sqlite3
from werkzeug.security import generate_password_hash, check_password_hash
from route_calc import calculate_full_route
from datetime import datetime


# Save route
def save_route(company_id, requested_by, origin, destinations):
    route_map, distance = calculate_full_route(origin, destinations)
    route_date = datetime.now().strftime("%Y, %B %d - ")
    route_time = datetime.now().strftime("%H;%M;%S")
    route_map.save(f"templates/saved_routes/{route_date} {route_time}.html")
    db_destinations = ""
    for index in range(len(destinations)):
        db_destinations += f"{destinations[index]}"
        if index is not len(destinations) - 1:
            db_destinations += ","

    with sqlite3.connect("database.db") as routes:
        cursor = routes.cursor()
        cursor.execute(
            "INSERT INTO routes(company_id, requested_by, assigned_to, origin, destinations, distance, date, time, file_name, completed) VALUES(?, ?, ?, ?, ?, ?, ?, ?, ?, ?)",
            (company_id, requested_by, -1, origin, db_destinations, distance, route_date, route_time,
             f"{route_date} {route_time}.html", 0))
        routes.commit()
        print("Added route to database")
        return True
    return False


# Get all routes from database
def get_all_routes(company_id, completed):
    with sqlite3.connect("database.db") as routes:
        cursor = routes.cursor()
        if company_id == -1:
            cursor.execute(f"SELECT * FROM routes")
        elif completed == -1:
            cursor.execute(f"SELECT * FROM routes WHERE company_id = {company_id}")
        else:
            cursor.execute(f"SELECT * FROM routes WHERE company_id = {company_id} AND completed = {completed}")
        routes = cursor.fetchall()
        return routes


# Get a specific route from database by id
def get_route_by_id(route_id):
    with sqlite3.connect("database.db") as routes:
        cursor = routes.cursor()
        cursor.execute(f"SELECT * FROM routes WHERE id = {route_id}")
        routes = cursor.fetchall()
        return routes


# Get a specific route from database by file name
def get_route_info(route_file_name):
    with sqlite3.connect("database.db") as routes:
        cursor = routes.cursor()
        cursor.execute(f"SELECT * FROM routes WHERE file_name = '{route_file_name}'")
        route_info = cursor.fetchall()
        return route_info


# Get all routes from database by specific status (1 -> Completed, 0 -> Incomplete)
def get_routes_by_status(company_id, completed, driver_username):
    with sqlite3.connect("database.db") as routes:
        cursor = routes.cursor()
        if company_id == -1:
            if completed == 1:
                cursor.execute(f"SELECT * FROM routes WHERE completed = 1")
            else:
                cursor.execute(f"SELECT * FROM routes WHERE completed = 0")
        else:

            if completed == 1 and driver_username == -1:
                cursor.execute(f"SELECT * FROM routes WHERE company_id = {company_id} AND completed = 1")
            elif completed == 0 and driver_username == -1:
                cursor.execute(f"SELECT * FROM routes WHERE company_id = {company_id} AND completed = 0")
            elif completed == 1 and driver_username != -1:
                cursor.execute(f"SELECT * FROM routes WHERE company_id = {company_id} AND completed = 1 AND assigned_to = '{driver_username}'")
            elif completed == 0 and driver_username != -1:
                cursor.execute(f"SELECT * FROM routes WHERE company_id = {company_id} AND completed = 0 AND assigned_to = '{driver_username}'")
        routes = cursor.fetchall()
        return routes


# Get all unassigned routes
def get_all_routes_unassigned(company_id):
    with sqlite3.connect("database.db") as routes:
        cursor = routes.cursor()
        if company_id == -1:
            cursor.execute(f"SELECT * FROM routes")
        else:
            cursor.execute(f"SELECT * FROM routes WHERE company_id = {company_id} AND assigned_to = -1")
        routes = cursor.fetchall()
        return routes


# Mark route as complete
def mark_route_complete(route_id):
    with sqlite3.connect("database.db") as routes:
        cursor = routes.cursor()
        cursor.execute(f"UPDATE routes SET completed = 1 WHERE id = {route_id}")
        routes.commit()
        return True
    return False


# Assign route to a driver
def assign_route_db(driver_username, file_name):
    with sqlite3.connect("database.db") as routes:
        cursor = routes.cursor()
        cursor.execute(f"UPDATE routes SET assigned_to = '{driver_username}' WHERE file_name = '{file_name}'")
        routes.commit()
        return True
    return False


# Get all assigned routes by company id
def get_assigned_routes(company_id):
    with sqlite3.connect("database.db") as routes:
        cursor = routes.cursor()
        cursor.execute(f"SELECT * FROM routes WHERE company_id = {company_id} AND assigned_to != -1")
        routes = cursor.fetchall()
        return routes
    return -1


# Get all routes of a specific driver
def get_all_driver_routes(company_id, username, completed):
    with sqlite3.connect("database.db") as routes:
        cursor = routes.cursor()
        cursor.execute(f"SELECT * FROM routes WHERE company_id = {company_id} AND assigned_to = {username}")
        routes = cursor.fetchall()
        return routes


# Get all routes of a specific driver
def get_all_routes_driver(driver_username):
    with sqlite3.connect("database.db") as routes:
        cursor = routes.cursor()
        cursor.execute(f"SELECT * FROM routes WHERE assigned_to = '{driver_username}'")
        routes = cursor.fetchall()
        return routes


