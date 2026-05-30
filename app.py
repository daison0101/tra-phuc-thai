from flask import (
    Flask,
    render_template,
    request,
    redirect,
    session
)
from gemini_ai import recommend_with_gemini
from sqlalchemy import or_
from flask_sqlalchemy import SQLAlchemy

from flask_login import (
    LoginManager,
    UserMixin,
    login_user,
    logout_user,
    login_required
)

from datetime import datetime

from config import DATABASE_URL

from ai import recommend_tea

# =========================
# APP CONFIG
# =========================

app = Flask(__name__)

app.secret_key = "tra-phuc-thai-secret-key"

app.config['SQLALCHEMY_DATABASE_URI'] = DATABASE_URL
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

# =========================
# LOGIN CONFIG
# =========================

login_manager = LoginManager()

login_manager.init_app(app)

login_manager.login_view = "login"

# =========================
# PRODUCT MODEL
# =========================

class Product(db.Model):

    __tablename__ = "products"

    id = db.Column(
        db.Integer,
        primary_key=True
    )

    name = db.Column(
        db.String(255),
        nullable=False
    )

    price = db.Column(
        db.Integer,
        nullable=False
    )

    short_description = db.Column(
        db.String(255)
    )

    description = db.Column(
        db.Text
    )

    image = db.Column(
        db.Text,
        nullable=False
    )

# =========================
# ORDER MODEL
# =========================

class Order(db.Model):

    __tablename__ = "orders"

    id = db.Column(
        db.Integer,
        primary_key=True
    )

    customer_name = db.Column(
        db.String(255),
        nullable=False
    )

    customer_phone = db.Column(
        db.String(50),
        nullable=False
    )

    customer_address = db.Column(
        db.Text,
        nullable=False
    )

    total_price = db.Column(
        db.Integer,
        nullable=False
    )

    created_at = db.Column(
        db.DateTime,
        default=datetime.utcnow
    )

# =========================
# DEMO USER
# =========================

class User(UserMixin):

    def __init__(self, id):
        self.id = id

admin_user = {
    "username": "admin",
    "password": "123456"
}

@login_manager.user_loader
def load_user(user_id):

    return User(user_id)

# =========================
# HOME
# =========================

@app.route('/')
def home():

    products = Product.query.all()

    return render_template(
        'index.html',
        products=products
    )

# =========================
# SEARCH
# =========================

@app.route('/search')
def search():

    query = request.args.get('q')

    if query:

        products = Product.query.filter(

            or_(

                Product.name.ilike(f'%{query}%'),

                Product.description.ilike(f'%{query}%')

            )

        ).all()

    else:

        products = Product.query.all()

    return render_template(
        'search.html',
        products=products,
        query=query
    )

# =========================
# PRODUCT DETAIL
# =========================

@app.route('/product/<int:id>')
def product_detail(id):

    product = Product.query.get_or_404(id)

    related_products = Product.query.filter(
        Product.id != id
    ).limit(3).all()

    return render_template(
        'product_detail.html',
        product=product,
        related_products=related_products
    )

# =========================
# LOGIN
# =========================

@app.route('/login', methods=['GET', 'POST'])
def login():

    error = None

    if request.method == 'POST':

        username = request.form['username']
        password = request.form['password']

        if (
            username == admin_user['username']
            and
            password == admin_user['password']
        ):

            user = User(1)

            login_user(user)

            return redirect('/admin')

        else:

            error = "Sai tài khoản hoặc mật khẩu"

    return render_template(
        'login.html',
        error=error
    )

# =========================
# LOGOUT
# =========================

@app.route('/logout')
@login_required
def logout():

    logout_user()

    return redirect('/')

# =========================
# ADMIN
# =========================

@app.route('/admin')
@login_required
def admin():

    products = Product.query.all()

    return render_template(
        'admin.html',
        products=products
    )

# =========================
# ADD PRODUCT
# =========================

@app.route('/add-product', methods=['POST'])
@login_required
def add_product():

    new_product = Product(

        name=request.form['name'],

        price=request.form['price'],

        short_description=request.form['short_description'],

        description=request.form['description'],

        image=request.form['image']

    )

    db.session.add(new_product)

    db.session.commit()

    return redirect('/admin')

# =========================
# EDIT PRODUCT
# =========================

@app.route('/edit-product/<int:id>', methods=['GET', 'POST'])
@login_required
def edit_product(id):

    product = Product.query.get_or_404(id)

    if request.method == 'POST':

        product.name = request.form['name']

        product.price = request.form['price']

        product.short_description = request.form['short_description']

        product.description = request.form['description']

        product.image = request.form['image']

        db.session.commit()

        return redirect('/admin')

    return render_template(
        'edit_product.html',
        product=product
    )
# =========================
# DELETE PRODUCT
# =========================

@app.route('/delete-product/<int:id>')
@login_required
def delete_product(id):

    product = Product.query.get_or_404(id)

    db.session.delete(product)

    db.session.commit()

    return redirect('/admin')

# =========================
# AI RECOMMEND
# =========================
@app.route('/ai-recommend', methods=['POST'])
def ai_recommend():

    user_input = request.form['problem']

    products = Product.query.all()

    result = recommend_with_gemini(user_input, products)

    return render_template(
        'recommend_result.html',
        result=result
    )

# =========================
# CART
# =========================

@app.route('/add-to-cart/<int:id>')
def add_to_cart(id):

    product = Product.query.get_or_404(id)

    cart = session.get('cart', [])

    cart.append({

        'id': product.id,

        'name': product.name,

        'price': product.price,

        'image': product.image

    })

    session['cart'] = cart

    return redirect('/cart')

@app.route('/cart')
def cart():

    cart_items = session.get('cart', [])

    total = sum(
        item['price']
        for item in cart_items
    )

    return render_template(
        'cart.html',
        cart_items=cart_items,
        total=total
    )

@app.route('/remove-from-cart/<int:index>')
def remove_from_cart(index):

    cart = session.get('cart', [])

    if 0 <= index < len(cart):

        cart.pop(index)

        session['cart'] = cart

    return redirect('/cart')

# =========================
# CHECKOUT
# =========================

@app.route('/checkout', methods=['GET', 'POST'])
def checkout():

    cart_items = session.get('cart', [])

    if not cart_items:

        return redirect('/')

    total = sum(
        item['price']
        for item in cart_items
    )

    if request.method == 'POST':

        new_order = Order(

            customer_name=request.form['name'],

            customer_phone=request.form['phone'],

            customer_address=request.form['address'],

            total_price=total

        )

        db.session.add(new_order)

        db.session.commit()

        session['cart'] = []

        return redirect('/')

    return render_template(
        'checkout.html',
        total=total
    )

# =========================
# ADMIN ORDERS
# =========================

@app.route('/admin-orders')
@login_required
def admin_orders():

    orders = Order.query.order_by(
        Order.created_at.desc()
    ).all()

    return render_template(
        'admin_orders.html',
        orders=orders
    )

# =========================
# RUN
# =========================
import os
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)
