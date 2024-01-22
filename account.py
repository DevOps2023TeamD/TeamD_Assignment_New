from flask import Blueprint, render_template, request, session, redirect, url_for
from database import get_database_connection
from datetime import datetime

account_bp = Blueprint('account', __name__)

# Index 
@account_bp.route('/')
def index():
    return render_template('index.html')

# Login GET & POST 
@account_bp.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == "POST":
        # Get username and password inputs
        username = request.form['username']
        password = request.form['password']

        # Connect to database
        connection = get_database_connection()
        cursor = connection.cursor()

        #SQL Query to check login credentials 
        query = "SELECT * FROM accounts WHERE username = %s AND password = %s"
        cursor.execute(query, (username, password))
        account = cursor.fetchone()

        # If account is found with username and password
        if account:
            # Check if account is approved
            if account[5] == 'Approved':
                # Save account_id in session storage
                session['account_username'] = account[1]
                session['account_type'] = account[4]
                
                if account[4] == 'Normal User':
                    return render_template('dashboard.html', accountName=account[1], account_type='Normal User')
                elif account[4] == 'Administrator':
                    return render_template('dashboard.html', accountName=account[1], account_type='Administrator')
            else:
                # If account is not approved, display error
                return render_template('login.html', error='Account not approved')
        else:
            # Else return back to login 
            return render_template('login.html', error='Invalid credentials')
    else:
        return render_template('login.html')

# Register GET & POST
@account_bp.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == "POST":
        # Get username and password inputs
        username = request.form['username']
        password = request.form['password']

        # Connect to database
        connection = get_database_connection()
        cursor = connection.cursor()

        # SQL Query to check login credentials and status
        query = "INSERT INTO accounts (username, password, creation_date, account_type, approval_status) VALUES (%s, %s, %s, 'Normal User', 'Pending')"
        # Get current datetime
        current_date = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        cursor.execute(query, (username, password, current_date))
        connection.commit()
        return render_template('register.html', message='Successful registration')
    else:
        return render_template('register.html')

# Dashboard GET
@account_bp.route('/dashboard', methods=['GET']) 
def dashboard():
    # Get account type from session
    account_type = session.get('account_type')
    account_name = session.get('account_username')

    if account_type == 'Normal User':
        return render_template('dashboard.html', accountName=account_name, account_type='Normal User')
    elif account_type == 'Administrator':
        return render_template('dashboard.html', accountName=account_name, account_type='Administrator')
    else:
        return render_template('login.html')

# Account Management GET
@account_bp.route('/accountManagement', methods=['GET'])
def accountManagement():
    # Connect to database
    connection = get_database_connection()
    cursor = connection.cursor()

    #SQL Query base
    query = "SELECT * FROM accounts"

    # Execute the SQL Query
    cursor.execute(query)
    accounts = cursor.fetchall()

    return render_template('accountManagement.html', accounts=accounts)

# Account Details GET
@account_bp.route('/accountDetails/<int:acc_id>', methods=['GET'])
def accountDetails(acc_id, message=''):
    # Connect to the database
    connection = get_database_connection()
    cursor = connection.cursor()

    # Query the specific account by ID
    query = "SELECT * FROM accounts WHERE account_id = %s"
    cursor.execute(query, (acc_id,))
    account = cursor.fetchone()

    return render_template('accountDetails.html', account=account, message=message)

# Approve Account POST
@account_bp.route('/approveAccount/<int:acc_id>', methods=['POST'])
def approveAccount(acc_id):
    # Connect to database
    connection = get_database_connection()
    cursor = connection.cursor()

    #SQL Query base
    query = """UPDATE accounts SET approval_status='Approved' WHERE account_id=%s"""

    cursor.execute(query, (acc_id,))
    connection.commit()

    return accountManagement()

# Modify Account
@account_bp.route('/modifyAccount/<int:acc_id>', methods=['POST'])
def modifyAccount(acc_id):
    account_name = request.form['acc-name']
    account_password = request.form['acc-pwd']

    # Get input from radio button for account type
    account_type = request.form.get('acc-type')
    account_date = request.form['acc-date']

    # Connect to database
    connection = get_database_connection()
    cursor = connection.cursor()

    #SQL Query base
    query = """UPDATE accounts SET username = %s, password = %s, account_type =%s, creation_date =%s, WHERE account_id=%s"""

    cursor.execute(query, (account_name, account_password, account_type, account_date, acc_id))
    connection.commit()

    return accountDetails(acc_id, message='Successful Account Modification')

