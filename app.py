import json
import re
from flask import Flask, redirect, render_template, request, session, url_for
from db_functions import *

app = Flask(__name__)
app.secret_key = 'TrydentForces'


@app.route('/')
def index():
    return render_template('login.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        pin = request.form['pin']

        # Query the database to get the user's pin
        user_pin = get_pin_for_username(username)

        if user_pin == pin:
            # Store the username in the session
            session['username'] = username
            return redirect(url_for('dashboard'))
        else:
            error_message = "Invalid credentials. Please try again."
            return render_template('login.html', error_message=error_message)

    # Render the login page for GET requests
    return render_template('login.html')


@app.route('/logout', methods=['POST'])
def logout():
    return redirect(url_for('login'))

@app.route('/register')
def register():
    return render_template('register.html')

@app.route('/registerForm', methods=['POST'])
def register_user():
    username = request.form['username']
    pin = request.form['pin']
    
    # Check if the PIN meets the requirement
    if not re.search(r'(?=.*[A-Z])(?=.*\d{6,})', pin):
        error_message = 'PIN must contain at least 1 capital letter and 6 numbers.'
        return render_template('register.html', error_message=error_message)
    
    try:
        add_user(username, pin)  
        return redirect(url_for('login'))  
    except Exception as e:
        return render_template('register.html', error_message=f"An error occurred: {e}")

@app.route('/dashboard')
def dashboard():
    username = session.get('username')
    return render_template('dashboard.html', username=username)

@app.route('/search', methods=['GET'])
def search():
    query = request.args.get('query', '')
    client_results = search_clients(query)
    product_results = search_products(query)
    return render_template('search.html', query=query, client_results=client_results, product_results=product_results)

@app.route('/inventory')
def inventory():
    # Retrieve inventory from database
    inventory = get_all_inventory()  
    return render_template('inventory.html', inventory=inventory)

@app.route('/clients', methods=['GET', 'POST'])
def clients():
    if request.method == 'POST':
        query = request.form.get('search')
        clients = search_clients(query)
    else:
        clients = get_all_clients()
    return render_template('clients.html', clients=clients)

@app.route('/add_client', methods=['GET', 'POST'])
def add_client():
    if request.method == 'POST':
        name = request.form['name']
        phone_number = request.form['phoneNumber']
        address = request.form.get('address', None)  # Address is optional
        balance = request.form['balance']
        
        try:
            add_client_to_db(name, phone_number, address, balance)
            return redirect(url_for('clients', client_id=get_last_client_id()))
        except Exception as e:
            return f"An error occurred: {e}"

    return render_template('add_client.html')

@app.route('/delete_client/<int:client_id>', methods=['GET'])
def delete_client(client_id):
    try:
        delete_client_from_db(client_id)
        return redirect(url_for('clients'))
    except Exception as e:
        return f"An error occurred: {e}"

@app.route('/edit_client/<int:client_id>', methods=['GET', 'POST'])
def edit_client(client_id):
    try:
        if request.method == 'POST':
            # Process the form submission to save changes
            name = request.form.get('name')
            phone_number = request.form.get('phoneNumber')
            address = request.form.get('address')
            balance = float(request.form.get('balance'))  # Convert to float

            print(f"Received form data - Name: {name}, Phone Number: {phone_number}, Address: {address}, Balance: {balance}")

            success = update_client(client_id, name, phone_number, address, balance)

            if success:
                print(f"Client {client_id} updated successfully")
                return redirect(url_for('clients'))  # Redirect to clients.html
            else:
                return "Failed to save changes", 500
        else:
            # Render the edit_client.html template
            client = get_client_by_id(client_id)
            if client is not None:
                return render_template('edit_client.html', client=client)
            else:
                return "Client not found", 404
    except Exception as e:
        print(f"An error occurred: {e}")
        return f"Internal Server Error: {e}", 500

@app.route('/manage_users')
def manage_users():
    users = get_all_users() 
    return render_template('manage_users.html', users=users)

@app.route('/delete_user/<int:user_id>', methods=['POST'])
def delete_user(user_id):
    result = delete_user_by_id(user_id)
    if result is True:
        return redirect(url_for('manage_users'))  # Successful deletion, redirect to manage_users page
    else:
        return f"An error occurred: {result}"  # Display error message

@app.route('/add_product', methods=['GET', 'POST'])
def add_product():
    if request.method == 'POST':
        try:
            name = request.form['name']
            description = request.form['description']
            quantity = request.form['quantity']
            price = request.form['price']
            
            # Call your function to add the product here
            # Remember to handle exceptions
            add_product_to_inventory(name, description, price, quantity)
            
            return redirect(url_for('inventory'))
        except Exception as e:
            return f"An error occurred: {e}"
    else:
        return render_template('add_product.html')

@app.route('/delete_product/<int:product_id>', methods=['POST'])
def delete_product(product_id):
    result = delete_product_by_id(product_id)
    if result is True:
        return redirect(url_for('inventory'))  # Successful deletion, redirect to inventory page
    else:
        return f"An error occurred: {result}"  # Display error message

@app.route('/edit_product/<int:product_id>', methods=['GET', 'POST'])
def edit_product(product_id):
    if request.method == 'POST':
        name = request.form['name']
        description = request.form['description']
        price = request.form['price']
        quantity = request.form['quantity']

        try:
            update_product(product_id, name, description, price, quantity)

            return redirect(url_for('inventory'))
        except Exception as e:
            return f"An error occurred: {e}"

    # If it's a GET request, fetch the product details and display them in the form
    product = get_product_by_id(product_id)
    return render_template('edit_product.html', product=product)

@app.route('/make_payment/<int:client_id>/<float:payment_amount>', methods=['POST'])
def make_payment(client_id, payment_amount):
    try:
        client = get_client_by_id(client_id)
        if client is not None:
            new_balance = client[4] - payment_amount
            update_result = update_client_balance(client_id, new_balance)
            if update_result:
                return "Payment successful", 200
            else:
                return "Failed to update client balance", 500
        else:
            return "Client not found", 404
    except Exception as e:
        return f"An error occurred: {e}", 500

if __name__ == '__main__':
    app.run(debug=True)