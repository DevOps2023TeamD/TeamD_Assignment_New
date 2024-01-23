from flask import Blueprint, render_template, request, session, redirect, url_for
from database import get_database_connection

capstone_bp = Blueprint('capstone', __name__)

# Create Capstone GET & POST
@capstone_bp.route('/createCapstone', methods=['GET', 'POST'])
def createCapstone():
    if request.method == "POST":
        cp_name = request.form['cp-name']
        cp_title = request.form['cp-title']
        cp_noOfStudents = request.form['cp-noOfStudents']
        cp_academicYear = request.form['cp-academicYear']
        cp_companyName = request.form['cp-companyName']
        cp_pointOfContract = request.form['cp-pointOfContact']
        cp_desc = request.form['cp-description']

        # Get radio input value
        cp_roleOfContact = request.form.get('cp-roleOfContact')

        # Connect to database
        connection = get_database_connection()
        cursor = connection.cursor()

        #SQL Query base
        query = """INSERT INTO capstone_projects (person_in_charge, role_of_contact, num_students, academic_year, capstone_title, company_name, company_contact, project_description)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s)"""
        
        cursor.execute(query, (cp_name, cp_roleOfContact, cp_noOfStudents, cp_academicYear, cp_title, cp_companyName, cp_pointOfContract, cp_desc))
        connection.commit()

        return render_template('createCapstone.html', message="Successful Capstone Creation")
    else:
        return render_template('createCapstone.html')

# Query Capstone GET & POST
@capstone_bp.route('/queryCapstone', methods=['GET', 'POST'])
def queryCapstone():
    if request.method == "POST":
        # Get academic year and keyword inputs
        academic_year = request.form['academic-year']
        keyword = request.form['keyword']

        # Validation: Check if academic_year is a valid year (4-digit number)
        if academic_year and (not academic_year.isdigit() or len(academic_year) != 4):
            return render_template('queryCapstone.html', error='Invalid Year Format')

        return redirect(url_for('capstone.queryResults', academic_year=academic_year, keyword=keyword))
    else:
        return render_template('queryCapstone.html')

# Query Results GET
@capstone_bp.route('/queryResults', methods=['GET'])
def queryResults():
    # Retrieve parameters from URL
    academic_year = request.args.get('academic_year')
    keyword = request.args.get('keyword')

    # Connect to database
    connection = get_database_connection()
    cursor = connection.cursor()

    #SQL Query base
    query = "SELECT * FROM capstone_projects WHERE 1=1"

    # Check if academic year and/or keyword are provided
    if academic_year:
        query += f" AND academic_year = '{academic_year}'"
    if keyword:
        query += f" AND capstone_title LIKE '%{keyword}%' OR project_description LIKE '%{keyword}%'"

    # Sort by descending year
    query += " ORDER BY academic_year DESC"

    # Execute the SQL Query
    cursor.execute(query)
    capstone_projects = cursor.fetchall()

    return render_template('queryResults.html', capstone_projects=capstone_projects, academic_year=academic_year, keyword=keyword)

# Capstone Details GET   
@capstone_bp.route('/capstoneDetails/<int:cp_id>', methods=['GET'])
def capstoneDetails(cp_id, message=''):
    # Retrieve account type from session 
    account_type = session.get('account_type')

    # Retrieve parameters from URL
    academic_year = request.args.get('academic_year')
    keyword = request.args.get('keyword')

    # Connect to the database
    connection = get_database_connection()
    cursor = connection.cursor()

    # Query the specific capstone project by ID
    query = "SELECT * FROM capstone_projects WHERE project_id = %s"
    cursor.execute(query, (cp_id,))
    capstone_project = cursor.fetchone()

    if account_type == "Normal User":
        return render_template(
            'capstoneDetails.html', 
            capstone_project=capstone_project, 
            account_type='Normal User', 
            message=message,
            academic_year=academic_year,
            keyword=keyword
        )
    elif account_type == "Administrator":
        return render_template(
            'capstoneDetails.html', 
            capstone_project=capstone_project, 
            account_type='Administrator', 
            message=message,
            academic_year=academic_year,
            keyword=keyword
        )

# Delete Capstone
@capstone_bp.route('/deleteCapstone/<int:cp_id>', methods=['GET'])
def deleteCapstone(cp_id):
    # Connect to database
    connection = get_database_connection()
    cursor = connection.cursor()

    #SQL Query base
    query = "DELETE FROM capstone_projects WHERE project_id = %s"

    cursor.execute(query, (cp_id,))
    connection.commit()

    return queryCapstone()