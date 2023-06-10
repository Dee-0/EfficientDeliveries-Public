import sqlite3


# Add a company to database
def addCompany(company_name, company_address, company_email, company_phone):
    with sqlite3.connect("database.db") as companies:
        cursor = companies.cursor()
        cursor.execute(
            f"INSERT INTO companies(company_name, company_address, company_email, company_phone) VALUES(?,?,?,?)",
            (company_name, company_address, company_email, company_phone))
        companies.commit()
        return True
    return False


# Get all companies from database
def get_all_companies():
    with sqlite3.connect("database.db") as companies:
        cursor = companies.cursor()
        cursor.execute("SELECT * FROM companies")
        companies = cursor.fetchall()
        return companies

# Remove company from database
def removeCompany(company_id):
    with sqlite3.connect("database.db") as companies:
        cursor = companies.cursor()
        cursor.execute(f"DELETE FROM companies WHERE id = {company_id}")
        companies.commit()
