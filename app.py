import flask
import sqlite3
from flask import Flask, render_template, request, session, redirect, url_for
from werkzeug.security import generate_password_hash
from datetime import datetime
from route_queue import calc_route_task

from db_interaction import get_all_managers_and_companies, get_all_drivers_and_companies
from db_users import add_user, get_all_managers, remove_manager_db, remove_driver_db, get_all_drivers, get_driver_by_id, get_drivers_by_company
from db_routes import save_route, remove_route_db,get_all_routes, get_all_routes_unassigned, assign_route_db, get_assigned_routes, get_route_info, get_all_driver_routes, get_routes_by_status, mark_route_complete, get_route_by_id, get_all_routes_driver
from db_companies import get_all_companies, addCompany, removeCompany, get_company_by_id
from db_messages import get_all_messages, send_message, get_possible_recipients, get_all_sent_messages, set_message_read
from db_logs import get_all_logs, add_to_log, get_logs_by_type
from db_user_page import login_check, confirm_pasword

app = Flask(__name__)

app.secret_key = 'my_key'


#Permissions check
def check_if_admin():
    if ('user_type' in session):
        if (session['user_type'] == 1):
            return True
    return False


def check_if_manager():
    if ('user_type' in session):
        if (session['user_type'] == 2):
            return True
    return False


def check_if_driver():
    if ('user_type' in session):
        if (session['user_type'] == 3):
            return True
    return False


# Get current time
def get_current_time_date():
    date = datetime.now().strftime("%d.%m.%Y")
    time = datetime.now().strftime("%H:%M:%S")
    return date, time


# Check unread messages count
def check_unread_count(messages):
    unread = 0
    for message in messages:
        if message[6] == 0:
            unread += 1
    session['unread_messages'] = unread


# Pages

@app.route("/")
def index():
    return render_template("index.html")


#Routes
@app.route("/newRoute", methods=["GET", "POST"])
def routes_page():
    if check_if_admin() or check_if_manager():
        return render_template("routes/newRoute.html")
    else:
        return render_template("routes/viewRoutes.html")


# Return map file
@app.route("/generatedRoute")
def generated_route():
    return flask.send_file("generatedRoute.html")


@app.route("/processData", methods=["GET", "POST"])
def process_data():
    status = ""
    data = request.json['data']
    origin = data[0]
    destinations = data[1:]
    message_date = datetime.now().strftime("%d.%m.%Y")
    message_time = datetime.now().strftime("%H:%M:%S")
    if save_route(session['company_id'], session['username'], origin, destinations):
        message_text = f"Route from {origin} to {destinations} created!"
        successful = "successfull"
    else:
        message_text = f"Could not create route from ' {origin} ' to {destinations}, perhaps the address does not exist or there is a typo, please try again."
        successful = "unsuccessfull"
    send_message("System", session['username'], message_text, message_date, message_time)
    date, time = get_current_time_date()
    add_to_log(session['user_type'], session['company_id'], session['username'],
               f"Route from {origin} to {destinations} creation was  {successful}", date, time, successful, 1)
    return render_template("routes/viewRoutes.html")


# Display requested route
@app.route("/newRouteDisplay", methods=["GET", "POST"])
def display_route():
    if request.method == "POST":
        route = request.form.get("route_filename")
        session['route_file_name'] = route
        route = f"templates\saved_routes\{route}"
        session['last_route_generated'] = route
        route_info = get_route_info(session['route_file_name'])
        origin = route_info[0][4]
        destinations = route_info[0][5]
        distance = str(route_info[0][6]) + "KM"

        return render_template("routes/newRouteDisplay.html", distance=distance, origin=origin, destinations=destinations)
    return render_template("routes/newRouteDisplay.html")


# Show route file
@app.route("/map_display")
def map_display():
    return flask.send_file(session['last_route_generated'])


# Remove a route
@app.route("/removeRoute", methods=["GET", "POST"])
def remove_route():
    status = ""
    if check_if_admin() or check_if_manager():
        routes = get_all_routes(session['company_id'], -1)
        if request.method == "POST":
            route_id = request.form.get("route_id")
            if remove_route_db(route_id):
                status = "Route Removed!"
                successful = "Successful"
            else:
                status = "Could not remove route."
                successful = "Unsuccessful"
            date, time = get_current_time_date()
            add_to_log(session['user_type'], session['company_id'], session['username'],
                       f"Route was removed {successful}", date, time, successful, 2)
            return render_template("routes/removeRoute.html", routes=routes, status=status)
    else:
        return render_template("index.html")
    return render_template("routes/removeRoute.html", routes=routes, status=status)


# Assign a route to a driver
@app.route("/assignRoute", methods=["GET", "POST"])
def assign_route():
    if check_if_admin() or check_if_manager():
        successful = "Unsuccessful"
        routes = get_all_routes_unassigned(session['company_id'])
        drivers = get_all_drivers(session['company_id'])
        if request.method == "POST":
            driver = request.form.get("driver")
            route = request.form.get("route")
            if assign_route_db(driver,route):
                successful = "successful"
            else:
                successful = "unsuccessful"
            date, time = get_current_time_date()
            add_to_log(session['user_type'], session['company_id'], session['username'], f"Route {route} assigned to {driver} was {successful}", date, time, successful, 1)
        return render_template("routes/assignRoute.html", routes=routes, drivers=drivers)
    else:
        return render_template("index.html")


# Reassign a route to a different driver
@app.route("/reassignRoute", methods=["GET", "POST"])
def reassign_route():
    if check_if_admin() or check_if_manager():
        routes = get_assigned_routes(session['company_id'])
        drivers = get_all_drivers(session['company_id'])
        if request.method == "POST":
            driver = request.form.get("driver")
            route = request.form.get("route")
            if assign_route_db(driver,route):
                successful = "successful"
            else:
                successful = "unsuccessful"
            date, time = get_current_time_date()
            add_to_log(session['user_type'], session['company_id'], session['username'], f"Route {route} reassigned to {driver} was {successful}", date, time, successful, 1)
        return render_template("routes/reassignRoute.html", routes=routes, drivers=drivers)
    else:
        return render_template("index.html")


# View all routes
@app.route("/viewRoutes")
def view_routes():
    if check_if_admin() or check_if_manager():
        routes = get_all_routes(session['company_id'], -1)
    else:
        return render_template("index.html")
    return render_template("routes/viewRoutes.html", routes=routes)


# View all routes for the driver
@app.route("/driverRoutesPage")
def view_routes_driver():
    if check_if_driver():
        routes = get_all_routes_driver(session['username'])
        return render_template("routes/driverRoutesPage.html", routes=routes)
    else:
        return render_template("index.html")


# Deliveries
# Show all deliveries
@app.route("/manageDeliveries")
def all_deliveries():
    if check_if_admin() or check_if_manager():
        routes = get_all_routes(session['company_id'], -1)
    else:
        routes = get_all_routes_driver(session['username'])
        return render_template("deliveries/manageDeliveries.html", routes=routes)
    return render_template("deliveries/manageDeliveries.html", routes=routes)


# Show all open deliveries
@app.route("/openDeliveries", methods=["GET", "POST"])
def view_open_deliveries():
    if check_if_admin() or check_if_manager():
        routes = get_routes_by_status(session['company_id'], 0, -1)
    else:
        routes = get_routes_by_status(session['company_id'], 0, session['username'])
    if request.method == "POST":
        route = request.form.get("route")
        if mark_route_complete(route):
            successful = "successfully"
        else:
            successful = "unsuccessfully"
        chosen_route = get_route_by_id(route)[0]
        date, time = get_current_time_date()
        add_to_log(session['user_type'], session['company_id'], session['username'],
                   f"Route {chosen_route[0]} from {chosen_route[6]} to {chosen_route[7]} was marked closed {successful}.", date, time, successful, 1)
        return render_template("deliveries/openDeliveries.html", routes=routes)
    return render_template("deliveries/openDeliveries.html", routes=routes)


# Show all closed deliveries
@app.route("/closedDeliveries", methods=["GET", "POST"])
def view_closed_deliveries():
    if check_if_admin() or check_if_manager():
        routes = get_routes_by_status(session['company_id'], 1, -1)
    else:
        routes = get_routes_by_status(session['company_id'], 1, session['username'])
    return render_template("deliveries/closedDeliveries.html", routes=routes)


# Companies
# Show all companies
@app.route("/manageCompanies")
def manage_companies():
    companies = get_all_companies()
    managers = get_all_managers()
    return render_template("companies/manageCompanies.html", companies=companies, managers=managers)


# Add a company
@app.route("/addCompany", methods=["GET", "POST"])
def add_company():
    status = ""
    if check_if_admin():
        if request.method == "POST":
            company_name = request.form.get("company_name")
            company_address = request.form.get("company_address")
            company_email = request.form.get("company_email")
            company_phone = request.form.get("company_phone")
            if addCompany(company_name, company_address, company_email, company_phone):
                managers = get_all_managers()
                status = "Company Added!"
                successful = "Successful"
                date, time = get_current_time_date()
                add_to_log(session['user_type'], session['company_id'], session['username'],
                           f"Company {company_name} Added.", date, time, successful, 2)
                return render_template("companies/addCompany.html", status=status)
            else:
                successful = "Unsuccessful"
                date, time = get_current_time_date()
                add_to_log(session['user_type'], session['company_id'], session['username'],
                           f"Company {company_name} WAS NOT added.", date, time, successful, 2)
                status = "Failed to add a company, try again later."
                return render_template("companies/addCompany.html", status=status)
    else:
        return render_template("index.html")
    return render_template("companies/addCompany.html")


# Remove a company
@app.route("/removeCompany", methods=["GET", "POST"])
def remove_company():
    status = ""
    if check_if_admin():
        companies = get_all_companies()
        if request.method == "POST":
            company_id = request.form.get("company")
            company = get_company_by_id(company_id)
            if removeCompany(company_id):
                status = "Company Removed!"
                successful = "Successful"
            else:
                status = "Could not remove company."
                successful = "Unsuccessful"
            date, time = get_current_time_date()
            add_to_log(session['user_type'], session['company_id'], session['username'],
                       f"Company {company[0][1]} was removed {successful}", date, time, successful, 2)
            return render_template("companies/removeCompany.html", companies=companies, status=status)
    else:
        return render_template("index.html")
    return render_template("companies/removeCompany.html", companies=companies, status=status)


# Managers
# Show all managers
@app.route("/manageManagers")
def manage_managers():
    if check_if_admin():
        managers,companies = get_all_managers_and_companies()
        return render_template("managers/manageManagers.html", managers=managers, companies=companies)


# Add a new manager
@app.route("/addManager", methods=["GET", "POST"])
def add_manager():
    if check_if_admin():
        companies = get_all_companies()
        company_id = -1
        if request.method == "POST":
            username = request.form.get("username")
            password = request.form.get("password")
            password = generate_password_hash(password)
            company_id = request.form.get("company_id")
            firstName = request.form.get("firstName")
            lastName = request.form.get("lastName")
            email = request.form.get("email")
            if add_user(2, username, password, firstName, lastName, email, company_id):
                successful = "successful"
            else:
                successful = "unsuccessful"
            date, time = get_current_time_date()
            add_to_log(session['user_type'], session['company_id'], session['username'],
                    f"Manager {username} addition was {successful}.", date, time, successful, 2)
            managers = get_all_managers()
            return render_template("managers/manageManagers.html", managers=managers, companies=companies)
    else:
        return render_template("index.html")
    return render_template("managers/addManager.html", companies=companies)


# Remove a manager
@app.route("/removeManager", methods=["GET", "POST"])
def remove_manager():
    if check_if_admin():
        managers = get_all_managers()
        if request.method == "POST":
            username = request.form.get("manager")
            if remove_manager_db(username):
                successful = "successful"
            else:
                successful = "unsuccessful"
            date, time = get_current_time_date()
            add_to_log(session['user_type'], session['company_id'], session['username'],
                    f"Manager {username} removal was {successful}", date, time, successful, 2)
    else:
        return render_template("index.html")
    return render_template("managers/removeManager.html", managers=managers)


# Drivers
# Show all drivers
@app.route("/manageDrivers")
def manage_drivers():
    if check_if_admin():
        drivers, companies = get_all_drivers_and_companies(session['company_id'])
        return render_template("drivers/manageDrivers.html", drivers=drivers, companies=companies)
    if check_if_manager():
        drivers, companies = get_all_drivers_and_companies(session['company_id'])
        return render_template("drivers/manageDrivers.html", drivers=drivers, companies=companies)
    else:
        return render_template("index.html")

# Show drivers by company id
@app.route("/companyDrivers", methods=["GET", "POST"])
def drivers_by_company():
    companies = get_all_companies()
    if check_if_admin():
        if request.method == "POST":
            company_id = request.form.get("company_id")
            if company_id != None:
                drivers = get_drivers_by_company(company_id)
                return render_template("drivers/companyDrivers.html", drivers=drivers, companies=companies)
            else:
                return render_template("drivers/companyDrivers.html", companies=companies)
        else:
            return render_template("drivers/companyDrivers.html", companies=companies)
    else:
        return render_template("index.html")


# Add a driver
@app.route("/addDriver", methods=["GET", "POST"])
def add_driver():
    status = ""
    company_id = session['company_id']
    if check_if_admin() or check_if_manager():
        companies = get_all_companies()
        if request.method == "POST":
            username = request.form.get("username")
            password = request.form.get("password")
            password = generate_password_hash(password)
            if check_if_admin():
                company_name = request.form.get("company_name")
                for company in companies:
                    if company_name == company[1]:
                        company_id = company[0]
            firstName = request.form.get("firstName")
            lastName = request.form.get("lastName")
            email = request.form.get("email")
            if add_user(3, username, password, firstName, lastName, email, company_id):
                status = "Driver Added!"
                successful = "successfully"
            else:
                successful = "unsuccessfully"
            date, time = get_current_time_date()
            add_to_log(session['user_type'], session['company_id'], session['username'],
                           f"Driver {username} addition was added {successful}", date, time, successful, 2)
            if check_if_admin():
                return render_template("drivers/addDriver.html", companies=companies, user=session['user_type'], status=status)
    else:
        return render_template("index.html")
    if check_if_admin():
        company_name = -1
        company_id = -1
        for company in companies:
            if company_name == company[1]:
                company_id = company[0]
        return render_template("drivers/addDriver.html", companies=companies, user=session['user_type'])
    else:
        return render_template("drivers/addDriver.html", user=session['user_type'])


# Remove a driver
@app.route("/removeDriver", methods=["GET", "POST"])
def remove_driver():
    status = ""
    if check_if_admin() or check_if_manager():
        drivers = get_all_drivers(session['company_id'])
        if request.method == "POST":
            username = request.form.get("driver")
            if remove_driver_db(username):
                status = "Driver removed!"
                successful = "successful"
            else:
                successful = "unsuccessful"
            date, time = get_current_time_date()
            add_to_log(session['user_type'], session['company_id'], session['username'],
                    f"Driver {username} removal was {successful}", date, time, successful, 2)
    return render_template("drivers/removeDriver.html", drivers=drivers, status=status)


#User

@app.route("/signup", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        username = request.form.get("username")
        password = request.form.get("password")
        password = generate_password_hash(password)

        with sqlite3.connect("database.db") as users:
            cursor = users.cursor()
            cursor.execute("INSERT INTO users(user_type, username, password, company_id) VALUES(?, ?, ?, ?)", (1, username, password, -1))
            users.commit()
        return render_template("main_page.html")
    else:
        return render_template("signup.html")


# Messages
# Show all messages
@app.route("/messages", methods=["GET", "POST"])
def messages_page():
    messages = get_all_messages(session['username'].lower())
    check_unread_count(messages)
    if request.method == "POST":
        message_id = request.form.get("message_id")
        set_message_read(message_id)
        check_unread_count(messages)
        return render_template("messages/messages.html", messages=messages)

    return render_template("messages/messages.html", messages=messages)


# Show all sent messages
@app.route("/sentMessages", methods=["GET", "POST"])
def sent_messages():
    messages = get_all_sent_messages(session['username'])
    return render_template("messages/sentMessages.html", messages=messages)


# Send a new message
@app.route("/newMessage", methods=["GET", "POST"])
def new_message():
    status = ""
    recipients = get_possible_recipients(session['company_id'])
    if request.method == "POST":
        username = request.form.get("username")
        username = username.lower()
        message_text = request.form.get("message")
        message_date = datetime.now().strftime("%d.%m.%Y")
        message_time = datetime.now().strftime("%H:%M:%S")
        if send_message(session['username'], username, message_text, message_date, message_time):
            status = "Message sent!"
            successful = "successful"
        else:
            successful = "unsuccessful"
        date, time = get_current_time_date()
        add_to_log(session['user_type'], session['company_id'], session['username'],
                   f"Message from {session['username']} to {username} sending was {successful}", date, time, successful, 3)
        return render_template("messages/newMessage.html", recipients=recipients, status=status)
    return render_template("messages/newMessage.html", recipients=recipients, status=status)


#Logs
#Show all logs
@app.route("/logs")
def logs():
    logs_db = get_all_logs(session['user_type'], session['company_id'])
    return render_template("logs/logs.html", logs=logs_db)


# Show all route related logs
@app.route("/routeLogs")
def route_logs():
    logs_db = get_logs_by_type(session['user_type'], session['company_id'], 1)
    return render_template("logs/logs.html", logs=logs_db)


#Show all user management logs
@app.route("/userManageLogs")
def user_manage_logs():
    logs_db = get_logs_by_type(session['user_type'], session['company_id'], 2)
    return render_template("logs/logs.html", logs=logs_db)


# Show all messages related logs
@app.route("/messagesLogs")
def message_logs():
    logs_db = get_logs_by_type(session['user_type'], session['company_id'], 3)
    return render_template("logs/logs.html", logs=logs_db)


# Show all user information logs
@app.route("/userInfoLogs")
def user_info_logs():
    logs_db = get_logs_by_type(session['user_type'], session['company_id'], 4)
    return render_template("logs/logs.html", logs=logs_db)


# Log in page
@app.route("/login", methods=["GET", "POST"])
def login():
    status = ""
    if ('username' in session):
        user_info = [session['username'], session['first_name'], session['last_name'], session['email'], session['company_name']]
        return render_template("user/user_page.html", user_info=user_info)
    if request.method == "POST":
        username = request.form.get("username")
        username_for_log = username
        password = request.form.get("password")
        correct, user_id, user_type ,username, first_name, last_name, company_id, email = login_check(username,password)
        if (correct):
            session['user_id'] = user_id
            session['user_type'] = user_type
            session['username'] = username
            session['first_name'] = first_name
            session['last_name'] = last_name
            session['company_id'] = company_id
            if session['company_id'] != -1:
                session['company_name'] = get_company_by_id(session['company_id'])[0][1]
            else:
                session['company_name'] = "Admin"
            session['email'] = email
            check_unread_count(get_all_messages(session['username']))
            successful = "successful"
            date, time = get_current_time_date()
            add_to_log(session['user_type'], session['company_id'], session['username'],
                       f"User {username} Logged in successfully.", date, time, successful, 4)
            return render_template("index.html")
        else:
            successful = "unsuccessful"
            date, time = get_current_time_date()
            add_to_log(0, 0, 0,
                       f"Attempt to log into account {username_for_log} was unsuccessful.", date, time, successful, 4)
            status = "Incorrect credentials"
            return render_template("user/login.html", status=status)
    return render_template("user/login.html")


# Change password page
@app.route("/changePassword", methods=["GET", "POST"])
def change_password():
    status = ""
    if request.method == "POST":
        username = session['username']
        old_password = request.form.get("currentPassword")
        new_password = request.form.get("newPassword")
        new_password2 = request.form.get("confirmPassword")
        print(f"{username} {old_password} {new_password} {new_password2}")
        if new_password == new_password2:
            if confirm_pasword(username,old_password,new_password):
                status = "Password changed successfully!"
                successful = "successful"
            else:
                status = "Password was not changed, try again."
                successful = "unsuccessful"
        else:
            status = "Password was not changed, try again."
            successful = "Unsuccessful"
        date, time = get_current_time_date()
        add_to_log(session['user_type'], session['company_id'], session['username'],
                   f"Password for {username} change was {successful}.", date, time, successful, 4)
    return render_template("user/changePassword.html", status=status)


# Logout
@app.route("/logout")
def logout():
    session.clear()
    return render_template("user/login.html")


# User page
@app.route("/user_page", methods=["GET", "POST"])
def user_page():
    user_info = [session['username'], session['first_name'], session['last_name']]
    return render_template("user/user_page.html", user_info=user_info)


if __name__ == "__main__":
    app.static_folder = 'static'
    app.run(debug=True)