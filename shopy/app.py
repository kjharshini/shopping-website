from flask import Flask, render_template, request, redirect, url_for, session
from pymongo import MongoClient
from datetime import datetime

app = Flask(__name__)
app.secret_key = 'minimal_secret_key'

client = MongoClient("mongodb://localhost:27017/")
db =client["shopy"]
users = db["users"]
orders = db["orders"]


# Mock Product Database
MOCK_PRODUCTS = [
    {"id": "1", "name": "Laptop", "price": "75,000", "image": "laptop.jpg", "category": "electronics"},
    {"id": "2", "name": "iPhone", "price": "45,000", "image": "phone.jpg", "category": "electronics"},
    {"id": "3", "name": "Sneakers", "price": "2,500", "image": "sneakers.jpg", "category": "sports"},
    {"id": "4", "name": "Running Shoes", "price": "3,200", "image": "running-shoes.jpg", "category": "sports"},
    {"id": "5", "name": "Spiral noteook", "price": "800", "image": "book.jpg", "category": "stationary"},
    {"id": "6", "name": "Smart Watch", "price": "2,000", "image": "smart-watch.jpg", "category": "electronics"},
    {"id": "7", "name": "Camera", "price": "15,000", "image": "camera.jpg", "category": "electronics"},
    {"id": "8", "name": "Jersey", "price": "1,500", "image": "jersey.jpg", "category": "sports"},
    {"id": "9", "name": "Football", "price": "1,000", "image": "football.jpg", "category": "sports"},
    {"id": "10", "name": "Pen", "price": "70", "image": "pen.jpg", "category": "stationary"},
    {"id": "11", "name": "Stapler", "price": "100", "image": "stapler.jpg", "category": "stationary"},
    {"id": "12", "name": "Paint Brush", "price": "560", "image": "brush.jpg", "category": "stationary"},
    {"id": "13", "name": "Lipstick", "price": "900", "image": "lipstick.jpg", "category": "beauty&care"},
    {"id": "14", "name": "Perfume", "price": "1500", "image": "perfume.jpg", "category": "beauty&care"},
    {"id": "15", "name": "Sunscreen", "price": "845", "image": "sunscreen.jpg", "category": "beauty&care"},
    {"id": "16", "name": "Shampoo", "price": "389", "image": "shampoo.jpg", "category": "beauty&care"},
    {"id": "17", "name": "Pan", "price": "1900", "image": "pan.jpg", "category": "kitchen"},
    {"id": "18", "name": "Knife", "price": "120", "image": "knife.jpg", "category": "kitchen"},
    {"id": "19", "name": "Gas Stove", "price": "6000", "image": "stove.jpg", "category": "kitchen"},
    {"id": "20", "name": "Bowl", "price": "320", "image": "bowl.jpg", "category": "kitchen"},
    {"id": "21", "name": "Lamp", "price": "2000", "image": "lamp.jpg", "category": "home-decor"},
    {"id": "22", "name": "Clock", "price": "1700", "image": "clock.jpg", "category": "home-decor"},
    {"id": "23", "name": "Curtains", "price": "676", "image": "curtains.jpg", "category": "home-decor"},
    {"id": "24", "name": "Wall Decor", "price": "450", "image": "walldecor.jpg", "category": "home-decor"},
    {"id": "25", "name": "Hoodie", "price": "800", "image": "hoodie.jpg", "category": "fashion"},
    {"id": "26", "name": "Jeans", "price": "899", "image": "jeans.jpg", "category": "fashion"},
    {"id": "27", "name": "Oversized T-shirt", "price": "399", "image": "tshirt.jpg", "category": "fashion"},
    {"id": "28", "name": "Saree", "price": "2800", "image": "saree.jpg", "category": "fashion"}
]
# Mock Cart (Normally would use session or database)
# mock_cart_items = [
#     {"name": "Classic Sneakers", "price": "2,500", "quantity": 1, "total": "2,500"},
# ]

# Mock Users Database
MOCK_USERS = []

@app.route('/')
def welcome():
    """Render the welcome page."""
    return render_template('welcome.html')

@app.route('/home')
def home():
    """Render the homepage with all products."""
    return render_template('index.html', items=MOCK_PRODUCTS)

@app.route('/login', methods=['GET', 'POST'])
def login():

    if request.method == 'POST':

        username = request.form.get('username')
        password = request.form.get('password')

        user = users.find_one({
            "username": username,
            "password": password
        })

        if user:
            session['user'] = username
            return redirect(url_for('home'))

        return render_template('login.html', error='Incorrect details')

    return render_template('login.html')

@app.route('/register', methods=['GET', 'POST'])
def register():

    if request.method == 'POST':

        username = request.form.get('username')
        full_name = request.form.get('full_name')
        phone = request.form.get('phone')
        email = request.form.get('email')
        address = request.form.get('address')
        password = request.form.get('password')
        confirm_password = request.form.get('confirm_password')

        if password != confirm_password:
            return render_template('register.html', error='Passwords do not match')

        existing_user = users.find_one({
            "$or": [
                {"username": username},
                {"email": email}
            ]
        })

        if existing_user:
            return render_template('register.html', error='User already exists')

        users.insert_one({
            "username": username,
            "full_name": full_name,
            "phone": phone,
            "email": email,
            "address": address,
            "password": password
        })

        session['user'] = username
        return redirect(url_for('home'))

    return render_template('register.html')

@app.route('/logout')
def logout():
    """Log out the user by clearing the session."""
    session.pop('user', None)
    return redirect(url_for('welcome'))

@app.route('/category/<category_name>')
def category(category_name):
    """Render products for a specific category."""
    filtered_items = [p for p in MOCK_PRODUCTS if p['category'].lower() == category_name.lower()]
    return render_template('category.html', category=category_name.capitalize(), items=filtered_items)

@app.route('/cart')
def cart():
    cart_data = session.get('cart', {})
    display_items = []
    grand_total = 0
    for item_id, quantity in cart_data.items():
        product = next((p for p in MOCK_PRODUCTS if p['id'] == item_id), None)
        if product:
            price_val = int(product['price'].replace(',', ''))
            total_val = price_val * quantity
            grand_total += total_val
            display_items.append({
                "id": product['id'],
                "name": product['name'],
                "price": product['price'],
                "quantity": quantity,
                "total": f"{total_val:,}"
            })
            
    return render_template('cart.html', items=display_items, grand_total=f"{grand_total:,}")

@app.route('/increment_cart/<item_id>')
def increment_cart(item_id):
    """Increment product quantity in the cart and redirect back to cart page."""
    if 'cart' not in session:
        session['cart'] = {}
    
    cart = session['cart']
    cart[item_id] = cart.get(item_id, 0) + 1
    session['cart'] = cart
    
    return redirect(url_for('cart'))

@app.route('/add_to_cart/<item_id>')
def add_to_cart(item_id):
    """Add a product to the cart (session-based)."""
    if 'cart' not in session:
        session['cart'] = {}
    
    cart = session['cart']
    cart[item_id] = cart.get(item_id, 0) + 1
    session['cart'] = cart
    
    return {"status": "success", "message": "Item added to cart"}

@app.route('/remove_from_cart/<item_id>')
def remove_from_cart(item_id):
    """Decrease quantity or remove product from the cart (session-based)."""
    if 'cart' in session:
        cart = session['cart']
        if item_id in cart:
            if cart[item_id] > 1:
                cart[item_id] -= 1
            else:
                del cart[item_id]
            session['cart'] = cart
    
    return redirect(url_for('cart'))

@app.route('/checkout')
def checkout():
    """Display the detailed bill and order summary before final purchase."""
    username = session.get('user')
    if not username:
        return redirect(url_for('login'))
        
    user_data = users.find_one({"username": username})
    cart_data = session.get('cart', {})
    
    if not cart_data:
        return redirect(url_for('cart'))
        
    display_items = []
    grand_total = 0
    for item_id, quantity in cart_data.items():
        product = next((p for p in MOCK_PRODUCTS if p['id'] == item_id), None)
        if product:
            price_val = int(product['price'].replace(',', ''))
            total_val = price_val * quantity
            grand_total += total_val
            display_items.append({
                "name": product['name'],
                "price": product['price'],
                "quantity": quantity,
                "total": f"{total_val:,}"
            })
            
    return render_template('checkout.html', 
                           items=display_items, 
                           grand_total=f"{grand_total:,}", 
                           user_data=user_data)

@app.route('/confirm_purchase')
def confirm_purchase():
    """Save the order to database, clear the cart, and redirect to home."""
    username = session.get('user')
    cart_data = session.get('cart', {})
    
    if username and cart_data:
        # Fetch full user details to store with the order for history
        user_data = users.find_one({"username": username})
        
        items_ordered = []
        grand_total = 0
        
        for item_id, quantity in cart_data.items():
            product = next((p for p in MOCK_PRODUCTS if p['id'] == item_id), None)
            if product:
                price_val = int(product['price'].replace(',', ''))
                total_val = price_val * quantity
                grand_total += total_val
                items_ordered.append({
                    "product_id": item_id,
                    "name": product['name'],
                    "price": product['price'],
                    "quantity": quantity,
                    "total": total_val
                })
        
        if items_ordered:
            orders.insert_one({
                "username": username,
                "customer_name": user_data.get('full_name') if user_data else username,
                "phone": user_data.get('phone') if user_data else '',
                "address": user_data.get('address') if user_data else '',
                "items": items_ordered,
                "grand_total": grand_total,
                "order_date": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                "status": "Processing"
            })

    session.pop('cart', None)
    return redirect(url_for('home'))

if __name__ == '__main__':
    app.run(debug=True, port=5000)
