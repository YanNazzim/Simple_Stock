from flask import Flask, redirect, render_template, request, url_for
import subprocess
from db_functions import *

app = Flask(__name__)

@app.route('/')
def index():
    return render_template('login.html')

from flask import render_template, redirect, url_for

@app.route('/commit_to_github', methods=['POST'])
def commit_to_github():
    subprocess.call(['.git/hooks/post-commit'])
    return redirect(url_for('dashboard'))

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        pin = request.form['pin']

        # Query the database to get the user's pin
        user_pin = get_pin_for_username(username)

        if user_pin == pin:
            return render_template('dashboard.html')
        else:
            return f"An error occurred: Invalid credentials. Please try again."

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
    
    try:
        add_user(username, pin)  
        return redirect(url_for('login'))  
    except Exception as e:
        return f"An error occurred: {e}"


@app.route('/dashboard')
def dashboard():
    return render_template('dashboard.html')

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


@app.route('/add_product', methods=['POST'])
def add_product():
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

def get_last_client_id():
    conn = connect_db()
    cursor = conn.cursor()
    cursor.execute('SELECT MAX(ClientID) FROM Clients')
    last_client_id = cursor.fetchone()[0]
    conn.close()
    return last_client_id

@app.route('/delete_client/<int:client_id>', methods=['GET'])
def delete_client(client_id):
    try:
        delete_client_from_db(client_id)
        return redirect(url_for('clients'))
    except Exception as e:
        return f"An error occurred: {e}"

if __name__ == '__main__':
    app.run(debug=True)

@app.route('/make_payment/<int:client_id>/<float:payment_amount>', methods=['POST'])
def make_payment(client_id, payment_amount):
    try:
        client = get_client_by_id(client_id)
        if client is not None:
            new_balance = client[4] - payment_amount
            update_client_balance(client_id, new_balance)
            return "Payment successful", 200
        else:
            return "Client not found", 404
    except Exception as e:
        return f"An error occurred: {e}", 500

