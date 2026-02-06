from flask import render_template, request, redirect, url_for, flash, session
from app import app
from db import Database
from functools import wraps

db = Database()

def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated_function

@app.route('/')
def home():
    # Always render the home page, login state handled in template
    return render_template('index.html')

@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        username = request.form['username']
        email = request.form['email']
        password = request.form['password']
        
        success, message = db.create_user(username, email, password)
        if success:
            flash('Account created successfully! Please login.', 'success')
            return redirect(url_for('login'))
        else:
            flash(f'Error: {message}', 'danger')
            
    return render_template('login.html', mode='signup')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        
        user = db.verify_password(email, password)
        if user:
            session['user_id'] = user['id']
            session['email'] = user['email']
            session['username'] = user['username']
            session['role'] = user.get('role', 'user')
            
            if session['role'] == 'admin':
                return redirect(url_for('admin_dashboard'))
            return redirect(url_for('dashboard'))
        else:
            flash('Invalid email or password', 'danger')
            
    return render_template('login.html', mode='login')

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('login'))

@app.route('/dashboard')
@login_required
def dashboard():
    portfolio = db.get_portfolio(session['email'])
    transactions = db.get_transactions(session['email'])
    # Calculate total value (mock prices for now since we don't have a real API yet)
    total_value = 0
    # Calculate total value using current stock prices
    total_value = 0.0
    for item in portfolio:
        qty = int(item['quantity'])
        symbol = item['symbol']
        # Fetch current price from DB
        current_price = db.get_stock_price(symbol)
        if current_price == 0:
             # Fallback if stock deleted or not found, maybe keep it at 0 or use last known if we stored it
             pass
        total_value += qty * current_price
        
    return render_template('dashboard.html', portfolio=portfolio, transactions=transactions, total_value=total_value, user=session)

@app.route('/trade', methods=['GET', 'POST'])
@login_required
def trade():
    stocks = db.get_all_stocks()
    
    if request.method == 'POST':
        symbol = request.form['symbol']
        action = request.form['action']
        quantity = int(request.form['quantity'])
        
        # Validation: Verify stock is listed
        # In a real app, we'd check against the DB again or the list we just fetched.
        valid_symbols = [s['symbol'] for s in stocks]
        if symbol not in valid_symbols:
             flash('Error: This stock is not listed for trading.', 'danger')
             return redirect(url_for('trade'))

        # Find the stock to get its price
        current_price = db.get_stock_price(symbol)
        if current_price == 0:
             flash('Error: Stock price not found.', 'danger')
             return redirect(url_for('trade'))

        success, msg = db.create_transaction(
            session['email'],
            symbol,
            action,
            quantity,
            current_price # Use the listed price
        )
        
        if success:
            flash(f'Order executed: {action} {quantity} {symbol} at ${current_price}', 'success')
            return redirect(url_for('dashboard'))
        else:
            flash(f'Trade failed: {msg}', 'danger')
            
    return render_template('trade.html', user=session, stocks=stocks)

@app.route('/portfolio')
@login_required
def portfolio():
    portfolio_items = db.get_portfolio(session['email'])
    return render_template('portfolio.html', portfolio=portfolio_items)

def admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            return redirect(url_for('login'))
        
        # Verify role from DB to be safe
        user = db.get_user(session['email'])
        if not user or user.get('role') != 'admin':
            flash('Access denied: Admins only.', 'danger')
            return redirect(url_for('dashboard'))
            
        return f(*args, **kwargs)
    return decorated_function

@app.route('/admin', methods=['GET', 'POST'])
@admin_required
def admin_dashboard():
    if request.method == 'POST':
        symbol = request.form.get('symbol').upper()
        name = request.form.get('name')
        price = request.form.get('price')
        
        if symbol and name and price:
            success, msg = db.create_stock(symbol, name, float(price))
            if success:
                flash(f'Stock {symbol} listed successfully!', 'success')
            else:
                flash(f'Error listing stock: {msg}', 'danger')
        else:
            flash(f'All fields are required.', 'warning')
            
    users = db.get_all_users()
    stats = db.get_system_stats()
    stocks = db.get_all_stocks()
    return render_template('admin.html', users=users, stats=stats, stocks=stocks)

@app.route('/admin/delete_stock/<symbol>', methods=['POST'])
@admin_required
def admin_delete_stock(symbol):
    success, msg = db.delete_stock(symbol)
    if success:
        flash(f'Stock {symbol} deleted successfully.', 'success')
    else:
        flash(f'Error deleting stock: {msg}', 'danger')
    return redirect(url_for('admin_dashboard'))
