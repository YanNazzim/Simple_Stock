import sqlite3
from github3 import login
import requests

def commit_to_github():
    # Define your GitHub repository details and commit message
    repo_owner = "YanNazzim"
    repo_name = "Simple_Stock"
    file_path = "SimpleStock.db"
    commit_message = "Updated database"
    branch = "main"
    personal_access_token = "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"  # Replace with your own token

    # Connect to GitHub using your personal access token
    gh = login(token=personal_access_token)

    # Get the repository
    repo = gh.repository(repo_owner, repo_name)

    # Read the SQLite file
    with open(file_path, 'rb') as file:
        content = file.read()

    # Get the current SHA for the file
    current_sha = repo.contents(file_path).sha

    # Create a new commit with the updated database file
    repo.update_file(
        path=file_path,
        message=commit_message,
        content=content,
        sha=current_sha,
        branch=branch
    )

    return "Changes committed to GitHub successfully."


def connect_db():
    try:
        return sqlite3.connect('SimpleStock.db', timeout=10)
    except sqlite3.Error as e:
        print(f"An error occurred while connecting to the database: {e}")
        return None

def search_clients(query):
    conn = connect_db()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM Clients WHERE Name LIKE ? OR PhoneNumber LIKE ?", ('%' + query + '%', '%' + query + '%'))
    results = cursor.fetchall()
    conn.close()
    return results

def search_products(query):
    conn = connect_db()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM Products WHERE Name LIKE ? OR Description LIKE ?", ('%' + query + '%', '%' + query + '%'))
    results = cursor.fetchall()
    conn.close()
    return results

def get_product_by_id(product_id):
    try:
        conn = connect_db()
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM Products WHERE ProductID = ?', (product_id,))
        product = cursor.fetchone()
        conn.close()
        return product
    except sqlite3.Error as e:
        print(f"An error occurred: {e}")
        return None

def get_client_by_id(client_id):
    try:
        conn = connect_db()
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM Clients WHERE ClientID = ?', (client_id,))
        client = cursor.fetchone()
        conn.close()
        return client
    except sqlite3.Error as e:
        print(f"An error occurred: {e}")
        return None

def get_pin_for_username(username):
    conn = connect_db()
    cursor = conn.cursor()
    cursor.execute('SELECT Pin FROM Users WHERE UserName=?', (username,))
    pin = cursor.fetchone()
    conn.close()

    if pin:
        return pin[0]
    else:
        return None

def get_all_clients():
    conn = connect_db()
    if not conn:
        return []

    try:
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM Clients')
        clients = cursor.fetchall()
        return clients
    except sqlite3.Error as e:
        print(f"An error occurred while fetching clients: {e}")
        return []
    finally:
        conn.close()

def get_client_by_id(client_id):
    try:
        conn = connect_db()
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM Clients WHERE ClientID = ?', (client_id,))
        client = cursor.fetchone()
        return client
    except sqlite3.Error as e:
        print(f"An error occurred while fetching client by ID: {e}")
        return None
    finally:
        if conn:
            conn.close()


def get_all_inventory():
    try:
        conn = connect_db()
        cursor = conn.cursor()
        cursor.execute('''
            SELECT * FROM Products
        ''')
        inventory = cursor.fetchall()
        conn.close()
        return inventory
    except sqlite3.Error as e:
        print(f"An error occurred: {e}")
        if conn:
            conn.rollback()  # Roll back any changes if an error occurs
        return []
    finally:
        if conn:
            conn.close()
            
def get_all_users():
    try:
        conn = connect_db()
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM Users')
        users = cursor.fetchall()
        conn.close()
        return users
    except sqlite3.Error as e:
        print(f"An error occurred: {e}")
        return None

def add_user(username, pin):
    conn = connect_db()
    cursor = conn.cursor()
    try:
        cursor.execute('INSERT INTO Users (UserName, Pin) VALUES (?, ?)',
                       (username, pin))
        conn.commit()
    except sqlite3.IntegrityError as e:
        return f"Error: {e}. The provided PIN may already exist. Please try a different one."
    except Exception as e:
        return f"An error occurred: {e}"
    finally:
        conn.close()


def add_product_to_inventory(name, description, price, quantity):
    try:
        conn = connect_db()
        cursor = conn.cursor()
        cursor.execute('INSERT INTO Products (Name, Description, Price, AvailableQuantity) VALUES (?, ?, ?, ?)',
                       (name, description, price, quantity))
        conn.commit()
        conn.close()
    except Exception as e:
        print(f"An error occurred: {e}")
        if conn:
            conn.rollback()  # Roll back any changes if an error occurs
        raise e
    finally:
        if conn:
            conn.close()

def delete_product_by_id(product_id):
    conn = connect_db()
    cursor = conn.cursor()
    
    try:
        cursor.execute('DELETE FROM Products WHERE ProductID = ?', (product_id,))
        conn.commit()
        return True  # Indicate successful deletion
    except Exception as e:
        return str(e)  # Return the error message as a string
    finally:
        conn.close()

def update_product(product_id, name, description, price, quantity):
    conn = connect_db()
    cursor = conn.cursor()
    
    try:
        cursor.execute('''
            UPDATE Products 
            SET Name=?, Description=?, Price=?, AvailableQuantity=?
            WHERE ProductID = ?
        ''', (name, description, price, quantity, product_id))
        
        conn.commit()
    except Exception as e:
        print(f"An error occurred: {e}")
        if conn:
            conn.rollback()  # Roll back any changes if an error occurs
        raise e
    finally:
        if conn:
            conn.close()


def delete_user_by_id(user_id):
    try:
        conn = connect_db()
        cursor = conn.cursor()
        cursor.execute('DELETE FROM Users WHERE UserID = ?', (user_id,))
        conn.commit()
        return True  # Indicate successful deletion
    except sqlite3.Error as e:
        return str(e)  # Return the error message as a string
    finally:
        if conn:
            conn.close()


def add_client_to_db(name, phone_number, address, balance):
    try:
        conn = connect_db()
        cursor = conn.cursor()
        cursor.execute('INSERT INTO Clients (Name, PhoneNumber, Address, Balance) VALUES (?, ?, ?, ?)',
                       (name, phone_number, address, balance))
        conn.commit()
    except sqlite3.Error as e:
        print(f"An error occurred: {e}")
        if conn:
            conn.rollback()  # Roll back any changes if an error occurs
    finally:
        if conn:
            conn.close()

def delete_client_from_db(client_id):
    try:
        conn = connect_db()
        cursor = conn.cursor()
        cursor.execute('DELETE FROM Clients WHERE ClientID = ?', (client_id,))
        conn.commit()
    except sqlite3.Error as e:
        print(f"An error occurred: {e}")
        if conn:
            conn.rollback()
    finally:
        if conn:
            conn.close()

def update_client(client_id, name, phone_number, address, balance):
    conn = connect_db()
    cursor = conn.cursor()
    
    try:
        cursor.execute('''
            UPDATE Clients 
            SET Name=?, PhoneNumber=?, Address=?, Balance=?
            WHERE ClientID = ?
        ''', (name, phone_number, address, balance, client_id))
        
        conn.commit()
    except Exception as e:
        print(f"An error occurred: {e}")
        if conn:
            conn.rollback()
        raise e
    finally:
        if conn:
            conn.close()

def update_client_balance(client_id, new_balance):
    conn = connect_db()
    cursor = conn.cursor()
    try:
        cursor.execute('UPDATE Clients SET Balance = ? WHERE ClientID = ?', (new_balance, client_id))
        conn.commit()
    except sqlite3.Error as e:
        print(f"An error occurred: {e}")
        if conn:
            conn.rollback()
    finally:
        if conn:
            conn.close()
