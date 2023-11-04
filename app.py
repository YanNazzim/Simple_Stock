from urllib import request
from fastapi import FastAPI, Query, Request, HTTPException, Form
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from db_functions import *

app = FastAPI()

# Define templates directory for rendering HTML templates
templates = Jinja2Templates(directory="templates")

@app.get('/', response_class=HTMLResponse)
async def index(request: Request):
    return templates.TemplateResponse("login.html", {"request": request})

@app.post('/login', response_class=HTMLResponse)
async def login(request: Request, username: str = Form(...), pin: str = Form(...)):
    user_pin = get_pin_for_username(username)
    if user_pin == pin:
        return templates.TemplateResponse("dashboard.html", {"request": request})
    else:
        raise HTTPException(status_code=400, detail="Invalid credentials. Please try again.")

@app.post('/logout', response_class=HTMLResponse)
async def logout():
    return templates.TemplateResponse("login.html", {"request": request})

@app.get('/register', response_class=HTMLResponse)
async def register(request: Request):
    return templates.TemplateResponse("register.html", {"request": request})

@app.post('/registerForm', response_class=HTMLResponse)
async def register_user(username: str = Form(...), pin: str = Form(...)):
    try:
        add_user(username, pin)  
        return templates.TemplateResponse("login.html", {"request": request})  
    except Exception as e:
        return templates.TemplateResponse("error.html", {"request": request, "error_message": f"An error occurred: {e}"})

@app.get('/dashboard', response_class=HTMLResponse)
async def dashboard(request: Request):
    return templates.TemplateResponse("dashboard.html", {"request": request})

@app.get('/search', response_class=HTMLResponse)
async def search(request: Request, query: str = Query(...)):
    client_results = search_clients(query)
    product_results = search_products(query)
    return templates.TemplateResponse("search.html", {"request": request, "query": query, "client_results": client_results, "product_results": product_results})

@app.get('/inventory', response_class=HTMLResponse)
async def inventory(request: Request):
    inventory = get_all_inventory()  
    return templates.TemplateResponse("inventory.html", {"request": request, "inventory": inventory})

@app.post('/clients', response_class=HTMLResponse)
async def clients(request: Request, search: str = Form(...)):
    if search:
        clients = search_clients(search)
    else:
        clients = get_all_clients()
    return templates.TemplateResponse("clients.html", {"request": request, "clients": clients})

@app.get('/manage_users', response_class=HTMLResponse)
async def manage_users(request: Request):
    users = get_all_users() 
    return templates.TemplateResponse("manage_users.html", {"request": request, "users": users})

@app.post('/delete_user/{user_id}', response_class=HTMLResponse)
async def delete_user(user_id: int):
    result = delete_user_by_id(user_id)
    if result is True:
        return RedirectResponse(url='/manage_users', status_code=303)  # Successful deletion, redirect to manage_users page
    else:
        return templates.TemplateResponse("error.html", {"request": request, "error_message": f"An error occurred: {result}"})

@app.post('/add_product', response_class=HTMLResponse)
async def add_product(request: Request, name: str = Form(...), description: str = Form(...), price: float = Form(...), quantity: int = Form(...)):
    try:
        add_product_to_inventory(name, description, price, quantity)  
        return RedirectResponse(url='/inventory', status_code=303)  # Successful addition, redirect to inventory page
    except Exception as e:
        return templates.TemplateResponse("error.html", {"request": request, "error_message": f"An error occurred: {e}"})

@app.post('/delete_product/{product_id}', response_class=HTMLResponse)
async def delete_product(product_id: int):
    result = delete_product_by_id(product_id)
    if result is True:
        return RedirectResponse(url='/inventory', status_code=303)  # Successful deletion, redirect to inventory page
    else:
        return templates.TemplateResponse("error.html", {"request": request, "error_message": f"An error occurred: {result}"})

@app.post('/edit_product/{product_id}', response_class=HTMLResponse)
async def edit_product(product_id: int, name: str = Form(...), description: str = Form(...), price: float = Form(...), quantity: int = Form(...)):
    try:
        update_product(product_id, name, description, price, quantity)  
        return RedirectResponse(url='/inventory', status_code=303)  # Successful edit, redirect to inventory page
    except Exception as e:
        return templates.TemplateResponse("error.html", {"request": request, "error_message": f"An error occurred: {e}"})

@app.post('/add_client', response_class=HTMLResponse)
async def add_client(request: Request, name: str = Form(...), phone_number: str = Form(...), address: str = Form(...), balance: float = Form(...)):
    try:
        add_client_to_db(name, phone_number, address, balance)  
        return RedirectResponse(url=f'/clients?client_id={get_last_client_id()}', status_code=303)  # Successful addition, redirect to clients page
    except Exception as e:
        return templates.TemplateResponse("error.html", {"request": request, "error_message": f"An error occurred: {e}"})

@app.post('/delete_client/{client_id}', response_class=HTMLResponse)
async def delete_client(client_id: int):
    try:
        delete_client_from_db(client_id)
        return RedirectResponse(url='/clients', status_code=303)  # Successful deletion, redirect to clients page
    except Exception as e:
        return templates.TemplateResponse("error.html", {"request": request, "error_message": f"An error occurred: {e}"})

@app.post('/update_client/{client_id}', response_class=HTMLResponse)
async def update_client(client_id: int, name: str = Form(...), phone_number: str = Form(...), address: str = Form(...), balance: float = Form(...)):
    try:
        update_client(client_id, name, phone_number, address, balance)  
        return RedirectResponse(url=f'/clients?client_id={client_id}', status_code=303)  # Successful update, redirect to client details page
    except Exception as e:
        return templates.TemplateResponse("error.html", {"request": request, "error_message": f"An error occurred: {e}"})
