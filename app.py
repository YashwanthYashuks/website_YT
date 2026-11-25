from flask import Flask, render_template, request, redirect, url_for, session, flash, jsonify
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime
import os


# ============================================================
# APPLICATION CONFIGURATION
# ============================================================

app = Flask(__name__)

app.config["SECRET_KEY"] = os.environ.get(
    "SECRET_KEY",
    "change-this-secret-key"
)

app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///yt_boquets.db"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

db = SQLAlchemy(app)


# ============================================================
# BUSINESS INFORMATION
# ============================================================

BUSINESS_NAME = "YT_Boquets_ReturnGifts"

# WhatsApp number WITHOUT +, spaces or hyphens
WHATSAPP = "918951104898"

LOCATION = (
    "SJR Layout Phase 2, Kodigehalli Main Rd, "
    "Ayyappa Nagar, Krishnarajapuram, "
    "Bengaluru, Karnataka - 560048"
)


# ============================================================
# PRODUCT MODEL
# ============================================================

class Product(db.Model):

    id = db.Column(
        db.Integer,
        primary_key=True
    )

    name = db.Column(
        db.String(150),
        nullable=False
    )

    description = db.Column(
        db.Text,
        default=""
    )

    price = db.Column(
        db.Float,
        nullable=False
    )

    # Example:
    # elegant_rose_bouquet.jpg
    image = db.Column(
        db.String(300),
        default=""
    )

    category = db.Column(
        db.String(80),
        default="Bouquets"
    )

    available = db.Column(
        db.Boolean,
        default=True
    )


# ============================================================
# CUSTOMER MODEL
# ============================================================

class Customer(db.Model):

    id = db.Column(
        db.Integer,
        primary_key=True
    )

    name = db.Column(
        db.String(120),
        nullable=False
    )

    phone = db.Column(
        db.String(30),
        nullable=False
    )

    email = db.Column(
        db.String(150),
        default=""
    )

    address = db.Column(
        db.Text,
        nullable=False
    )

    city = db.Column(
        db.String(100),
        default=""
    )

    pincode = db.Column(
        db.String(20),
        default=""
    )


# ============================================================
# ORDER MODEL
# ============================================================

class Order(db.Model):

    id = db.Column(
        db.Integer,
        primary_key=True
    )

    order_number = db.Column(
        db.String(40),
        unique=True,
        nullable=False
    )

    customer_id = db.Column(
        db.Integer,
        db.ForeignKey("customer.id"),
        nullable=False
    )

    total_amount = db.Column(
        db.Float,
        nullable=False
    )

    delivery_date = db.Column(
        db.String(30),
        default=""
    )

    special_instructions = db.Column(
        db.Text,
        default=""
    )

    status = db.Column(
        db.String(50),
        default="Order Received"
    )

    created_at = db.Column(
        db.DateTime,
        default=datetime.utcnow
    )

    updated_at = db.Column(
        db.DateTime,
        default=datetime.utcnow,
        onupdate=datetime.utcnow
    )

    customer = db.relationship(
        "Customer",
        backref="orders"
    )


# ============================================================
# ORDER ITEMS
# ============================================================

class OrderItem(db.Model):

    id = db.Column(
        db.Integer,
        primary_key=True
    )

    order_id = db.Column(
        db.Integer,
        db.ForeignKey("order.id"),
        nullable=False
    )

    product_id = db.Column(
        db.Integer,
        db.ForeignKey("product.id"),
        nullable=False
    )

    quantity = db.Column(
        db.Integer,
        nullable=False
    )

    price = db.Column(
        db.Float,
        nullable=False
    )

    subtotal = db.Column(
        db.Float,
        nullable=False
    )

    order = db.relationship(
        "Order",
        backref="items"
    )

    product = db.relationship(
        "Product"
    )


# ============================================================
# ORDER STATUS HISTORY
# ============================================================

class OrderStatusHistory(db.Model):

    id = db.Column(
        db.Integer,
        primary_key=True
    )

    order_id = db.Column(
        db.Integer,
        db.ForeignKey("order.id"),
        nullable=False
    )

    status = db.Column(
        db.String(50),
        nullable=False
    )

    updated_at = db.Column(
        db.DateTime,
        default=datetime.utcnow
    )


# ============================================================
# ADMIN LOGIN
# ============================================================

ADMIN_USER = os.environ.get(
    "ADMIN_USER",
    "admin"
)

ADMIN_PASSWORD = os.environ.get(
    "ADMIN_PASSWORD",
    "admin123"
)

ADMIN_PASSWORD_HASH = generate_password_hash(
    ADMIN_PASSWORD
)


# ============================================================
# GLOBAL VARIABLES FOR HTML
# ============================================================

@app.context_processor
def globals_for_templates():

    return {
        "business_name": BUSINESS_NAME,
        "whatsapp": WHATSAPP,
        "location": LOCATION,
        "currency": "₹"
    }


# ============================================================
# HOME PAGE
# ============================================================

@app.route("/")
def home():

    products = Product.query.filter_by(
        available=True
    ).all()

    return render_template(
        "index.html",
        products=products
    )


# ============================================================
# PRODUCT DETAILS
# ============================================================

@app.route("/product/<int:product_id>")
def product(product_id):

    item = Product.query.get_or_404(
        product_id
    )

    return render_template(
        "product.html",
        product=item
    )


# ============================================================
# CART
# ============================================================

@app.route("/cart")
def cart():

    cart = session.get(
        "cart",
        {}
    )

    if cart:

        product_ids = [
            int(product_id)
            for product_id in cart.keys()
        ]

        products = Product.query.filter(
            Product.id.in_(product_ids)
        ).all()

    else:

        products = []

    rows = []
    total = 0

    for product in products:

        quantity = int(
            cart.get(
                str(product.id),
                0
            )
        )

        subtotal = (
            product.price *
            quantity
        )

        total += subtotal

        rows.append({
            "product": product,
            "quantity": quantity,
            "subtotal": subtotal
        })

    return render_template(
        "cart.html",
        rows=rows,
        total=total
    )


# ============================================================
# ADD PRODUCT TO CART
# ============================================================

@app.post("/cart/add")
def add_to_cart():

    product_id = str(
        request.form["product_id"]
    )

    quantity = max(
        1,
        int(
            request.form.get(
                "quantity",
                1
            )
        )
    )

    cart = session.get(
        "cart",
        {}
    )

    cart[product_id] = (
        int(
            cart.get(
                product_id,
                0
            )
        )
        + quantity
    )

    session["cart"] = cart

    flash(
        "Product added to cart."
    )

    return redirect(
        request.referrer
        or url_for("home")
    )


# ============================================================
# UPDATE CART
# ============================================================

@app.post("/cart/update")
def update_cart():

    cart = {}

    for key, value in request.form.items():

        if key.startswith("qty_"):

            product_id = key.replace(
                "qty_",
                ""
            )

            quantity = int(value)

            if quantity > 0:

                cart[product_id] = quantity

    session["cart"] = cart

    return redirect(
        url_for("cart")
    )


# ============================================================
# CHECKOUT
# ============================================================

@app.route(
    "/checkout",
    methods=["GET", "POST"]
)
def checkout():

    cart = session.get(
        "cart",
        {}
    )

    if not cart:

        return redirect(
            url_for("cart")
        )

    product_ids = [
        int(product_id)
        for product_id in cart.keys()
    ]

    products = Product.query.filter(
        Product.id.in_(product_ids)
    ).all()

    total = 0

    for product in products:

        quantity = int(
            cart.get(
                str(product.id),
                0
            )
        )

        total += (
            product.price *
            quantity
        )

    # --------------------------------------------------------
    # PLACE ORDER
    # --------------------------------------------------------

    if request.method == "POST":

        customer = Customer(

            name=request.form[
                "name"
            ].strip(),

            phone=request.form[
                "phone"
            ].strip(),

            email=request.form.get(
                "email",
                ""
            ).strip(),

            address=request.form[
                "address"
            ].strip(),

            city=request.form.get(
                "city",
                ""
            ).strip(),

            pincode=request.form.get(
                "pincode",
                ""
            ).strip()
        )

        db.session.add(
            customer
        )

        db.session.flush()

        # Example:
        # ORD-20261125-101530
        order_number = (
            "ORD-"
            + datetime.now().strftime(
                "%Y%m%d-%H%M%S"
            )
        )

        order = Order(

            order_number=order_number,

            customer_id=customer.id,

            total_amount=total,

            delivery_date=request.form.get(
                "delivery_date",
                ""
            ),

            special_instructions=request.form.get(
                "special_instructions",
                ""
            ),

            status="Order Received"
        )

        db.session.add(
            order
        )

        db.session.flush()

        # ----------------------------------------------------
        # ORDER ITEMS
        # ----------------------------------------------------

        for product in products:

            quantity = int(
                cart[
                    str(product.id)
                ]
            )

            subtotal = (
                product.price *
                quantity
            )

            order_item = OrderItem(

                order_id=order.id,

                product_id=product.id,

                quantity=quantity,

                price=product.price,

                subtotal=subtotal
            )

            db.session.add(
                order_item
            )

        # ----------------------------------------------------
        # INITIAL STATUS HISTORY
        # ----------------------------------------------------

        status_history = OrderStatusHistory(

            order_id=order.id,

            status="Order Received"
        )

        db.session.add(
            status_history
        )

        db.session.commit()

        # Empty cart
        session["cart"] = {}

        return render_template(
            "confirmation.html",
            order=order
        )

    return render_template(
        "checkout.html",
        products=products,
        cart=cart,
        total=total
    )


# ============================================================
# CUSTOMER ORDER TRACKING
# ============================================================

@app.route(
    "/track",
    methods=["GET", "POST"]
)
def track():

    order = None

    if request.method == "POST":

        order_number = request.form[
            "order_number"
        ].strip()

        order = Order.query.filter_by(
            order_number=order_number
        ).first()

    return render_template(
        "track.html",
        order=order
    )


# ============================================================
# ORDER API
# ============================================================

@app.route(
    "/api/order/<order_number>"
)
def order_api(order_number):

    order = Order.query.filter_by(
        order_number=order_number
    ).first_or_404()

    return jsonify({

        "order_number":
            order.order_number,

        "status":
            order.status,

        "total":
            order.total_amount,

        "updated_at":
            order.updated_at.strftime(
                "%Y-%m-%d %H:%M"
            )
    })


# ============================================================
# ADMIN LOGIN
# ============================================================

@app.route(
    "/admin/login",
    methods=["GET", "POST"]
)
def admin_login():

    if request.method == "POST":

        username = request.form[
            "username"
        ]

        password = request.form[
            "password"
        ]

        if (
            username == ADMIN_USER
            and
            check_password_hash(
                ADMIN_PASSWORD_HASH,
                password
            )
        ):

            session["admin"] = True

            return redirect(
                url_for(
                    "admin_dashboard"
                )
            )

        flash(
            "Invalid admin credentials."
        )

    return render_template(
        "admin_login.html"
    )


# ============================================================
# ADMIN LOGOUT
# ============================================================

@app.route("/admin/logout")
def admin_logout():

    session.pop(
        "admin",
        None
    )

    return redirect(
        url_for("admin_login")
    )


# ============================================================
# ADMIN AUTHENTICATION
# ============================================================

def admin_required():

    return session.get(
        "admin"
    ) is True


# ============================================================
# ADMIN DASHBOARD
# ============================================================

@app.route("/admin")
def admin_dashboard():

    if not admin_required():

        return redirect(
            url_for("admin_login")
        )

    orders = Order.query.order_by(
        Order.created_at.desc()
    ).all()

    products = Product.query.order_by(
        Product.id.desc()
    ).all()

    return render_template(
        "admin.html",
        orders=orders,
        products=products
    )


# ============================================================
# UPDATE ORDER STATUS
# ============================================================

@app.post(
    "/admin/order/<int:order_id>/status"
)
def admin_status(order_id):

    if not admin_required():

        return redirect(
            url_for("admin_login")
        )

    order = Order.query.get_or_404(
        order_id
    )

    status = request.form[
        "status"
    ]

    allowed_statuses = [

        "Order Received",

        "Confirmed",

        "Preparing",

        "Ready",

        "Out for Delivery",

        "Delivered",

        "Cancelled"
    ]

    if status in allowed_statuses:

        order.status = status

        status_history = OrderStatusHistory(

            order_id=order.id,

            status=status
        )

        db.session.add(
            status_history
        )

        db.session.commit()

    return redirect(
        url_for(
            "admin_dashboard"
        )
    )


# ============================================================
# ADD PRODUCT FROM ADMIN
# ============================================================

@app.post("/admin/product/add")
def admin_product_add():

    if not admin_required():

        return redirect(
            url_for("admin_login")
        )

    product = Product(

        name=request.form[
            "name"
        ].strip(),

        description=request.form.get(
            "description",
            ""
        ).strip(),

        price=float(
            request.form[
                "price"
            ]
        ),

        category=request.form.get(
            "category",
            "Bouquets"
        ).strip(),

        image=request.form.get(
            "image",
            ""
        ).strip()
    )

    db.session.add(
        product
    )

    db.session.commit()

    return redirect(
        url_for(
            "admin_dashboard"
        )
    )


# ============================================================
# INITIAL PRODUCT DATA
# ============================================================


def seed():

    db.create_all()

    if Product.query.count() == 0:

        db.session.add_all([

            Product(
                name="Elegant Rose Bouquet",
                description="Fresh rose bouquet for special occasions.",
                price=499,
                category="Bouquets",
                image="elegant_rose_bouquet.jpg"
            ),

            Product(
                name="Premium Flower Bouquet",
                description="Premium mixed flowers arranged beautifully.",
                price=799,
                category="Bouquets",
                image="premium_flower_bouquet.jpg"
            ),

            Product(
                name="Mini Return Gift Pack",
                description="Cute return gift pack for small events.",
                price=149,
                category="Return Gifts",
                image="mini_return_gift_pack.jpg"
            ),

            Product(
                name="Premium Return Gift Box",
                description="Elegant return gift box for weddings and functions.",
                price=299,
                category="Return Gifts",
                image="premium_return_gift_box.jpg"
            ),

            Product(
                name="Custom Wedding Gift",
                description="Customizable return gift for bulk wedding orders.",
                price=399,
                category="Custom Orders",
                image="custom_wedding_gift.jpg"
            )

        ])

        db.session.commit()

    # Update image filenames for existing products
    image_updates = {
        "Elegant Rose Bouquet": "elegant_rose_bouquet.jpg",
        "Premium Flower Bouquet": "premium_flower_bouquet.jpg",
        "Mini Return Gift Pack": "mini_return_gift_pack.jpg",
        "Premium Return Gift Box": "premium_return_gift_box.jpg",
        "Custom Wedding Gift": "custom_wedding_gift.jpg"
    }

    for product_name, image_name in image_updates.items():

        product = Product.query.filter_by(
            name=product_name
        ).first()

        if product:
            product.image = image_name

    db.session.commit()

    print("Product image filenames updated successfully.")



# ============================================================
# CREATE DATABASE
# AND INSERT SAMPLE PRODUCTS
# ============================================================

with app.app_context():

    seed()


# ============================================================
# START APPLICATION
# ============================================================

if __name__ == "__main__":

    app.run(
        debug=True
    )