from flask import render_template, request, redirect, url_for, flash, session
from app import app
from models import db, User, Category, Product, Cart, Transaction, Order
from werkzeug.security import generate_password_hash, check_password_hash
from functools import wraps
from datetime import datetime

@app.route("/")
def signin():
    return render_template("signin.html")


@app.route("/", methods=["POST"])
def sigin_post():
    username = request.form.get("username")
    password = request.form.get("password")

    if not username or not password:
        flash("Username and Password cannot be empty.")
        return redirect(url_for("signin"))

    user = User.query.filter_by(username=username).first()

    if not user or not check_password_hash(user.passhash, password):
        flash("Username or password is incorrect.")
        return redirect(url_for("signin"))

    session["user_id"] = user.id
    flash("LogIn successful :)")
    return redirect(url_for("home"))


@app.route("/register")
def register():
    return render_template("register.html")


@app.route("/register", methods=['POST'])
def register_post():
    name = request.form.get("name")
    username = request.form.get("username")
    password = request.form.get("password")
    confirm_password = request.form.get("confirm_password")

    if not username or not password or not confirm_password:
        flash("Please fill out all the fields.")
        return redirect(url_for("register"))

    if password != confirm_password:
        flash("Passwords do not match.")
        return redirect(url_for("register"))

    user = User.query.filter_by(username=username).first()

    if user:
        flash("Username already exists. Please pick another username.")
        return redirect(url_for("register"))

    pass_hash = generate_password_hash(password)

    new_user = User(name=name, username=username, passhash=pass_hash)
    db.session.add(new_user)
    db.session.commit()
    return redirect(url_for("signin"))

@app.route("/logout")
def logout():
    session.pop("user_id")
    return redirect(url_for("signin"))


# =========================

# Decorator function for authentication

def auth_required(func):
    @wraps(func)
    def inner(*args, **kwargs):
        if "user_id" in session:
            return func(*args, **kwargs)
        else:
            flash("Please sign in first.")
            return redirect(url_for("signin"))
    return inner


def admin_required(func):
    @wraps(func)
    def inner(*args, **kwargs):
        if not "user_id" in session:
            flash("Please sign in first.")
            return redirect(url_for("signin"))
        
        user = User.query.get(session["user_id"])
        if not user.is_admin:
            flash("You are not authorised to access this page.")
            return redirect(url_for("index"))
        return func(*args, **kwargs)
    return inner


# ---------- user routes
@app.route("/home")
@auth_required
def home():
    user = User.query.get(session["user_id"])
    if user.is_admin == True:
        return redirect(url_for("admin"))
    return render_template("index.html")
    

@app.route("/profile", methods = ["POST"])
@auth_required
def profile_post():
    username = request.form.get("username")
    name = request.form.get("name")
    cpassword = request.form.get("cpassword")
    password = request.form.get("password")

    if not username or not password or not cpassword:
        flash("Please fill out all the required fields.")
        return redirect(url_for("profile"))
    
    user = User.query.get(session["user_id"])
    if not check_password_hash(user.passhash, cpassword):
        flash("Current password is incorrect ;)")
        return redirect(url_for("profile"))
    
    if username != user.username:
        new_username = User.query.filter_by(username=username).first()
        if new_username:
            flash("This username already exists, choose another.")
            return redirect(url_for("profile"))
        
    user.passhash = generate_password_hash(password)
    user.username = username
    user.name = name
    db.session.commit()
    flash("Profile updated successfully.")
    return redirect(url_for("profile"))

@app.route("/profile")
@auth_required
def profile():
    user = User.query.get(session["user_id"])
    return render_template("profile.html", user = user)



# ------------ Admin pages

@app.route("/admin")
@admin_required
def admin():
    categories = Category.query.all()
    return render_template("admin.html", categories=categories)

@app.route("/category/add")
@admin_required
def add_category():
    return render_template("category/add.html")

@app.route("/category/add", methods = ["POST"])
@admin_required
def add_category_post():
    name = request.form.get("name")

    if not name:
        flash("Please fill out all the fields.")
        return redirect(url_for("add_category"))
    
    new_category = Category.query.filter_by(name = name).first()
    if new_category:
        flash("Category already exists.")
        return redirect(url_for("home"))
    category = Category(name=name)
    db.session.add(category)
    db.session.commit()

    flash("Category Added Successfully.")
    return redirect(url_for("admin"))


@app.route("/category/<int:id>/")
@admin_required
def show_category(id):
    category = Category.query.get(id)
    if not category:
        flash("Category does not exists.")
        return redirect(url_for("admin"))
    return render_template("category/show.html", category = category)



@app.route("/category/<int:id>/edit")
@admin_required
def edit_category(id):
    category = Category.query.get(id)
    if not category:
        flash("Category does not exist.")
        return redirect(url_for("admin"))
    return render_template("category/edit.html", category = category)

@app.route("/category/<int:id>/edit", methods = ["POST"])
@admin_required
def edit_category_post(id):
    categories = Category.query.all()
    name = request.form.get("name")

    if not name:
        flash("Please fill out all the fields")
        return redirect(url_for("edit_category"))
    
    category = Category.query.get(id)
    if not category:
        flash("Category does not exist.")
        return redirect(url_for("admin"))
    
    # if category:
    #     flash("Category already exists.")
    #     return redirect(url_for("edit_category"))
    
    category.name = name
    db.session.commit()
    flash("Category edited successfully.")
    return redirect(url_for("admin"))

@app.route("/category/<int:id>/delete")
@admin_required
def delete_category(id):
    category = Category.query.get(id)
    if not category:
        flash("Category does not exist")
        return redirect(url_for("admin"))
    return render_template("category/delete.html", category = category)

@app.route("/category/<int:id>/delete", methods = ["POST"])
@admin_required
def delete_category_post(id):
    category = Category.query.get(id)
    if not category:
        flash("Category does not exist")
        return redirect(url_for("admin"))
    
    db.session.delete(category)
    db.session.commit()

    flash("Category deleted successfully.")
    return redirect(url_for("admin"))

@app.route("/product/add/<int:category_id>")
@admin_required
def add_product(category_id):
    category = Category.query.get(category_id)
    categories = Category.query.all()
    if not category:
        flash("Category does not exist.")
        return redirect(url_for("admin"))
    return render_template("product/add.html", category=category, categories=categories)

@app.route("/product/add/", methods = ["POST"])
@admin_required
def add_product_post():
    name = request.form.get("name")
    price = request.form.get("price")
    category_id = request.form.get("category_id")
    quantity = request.form.get("quantity")
    man_date = request.form.get("man_date")

    category = Category.query.get(category_id)
    if not category:
        flash("This category does not exist")
        return redirect(url_for(admin))
    
    if not name or not price or not quantity or not man_date:
        flash("Please fill out all the fields.")
        return redirect(url_for("add_product", category_id = category_id))
    
    try:
        price = float(price)
        quantity = int(quantity)
        man_date = datetime.strptime(man_date, "%Y-%m-%d")
    except ValueError:
        flash("Invalid value for quantity or price.")
        return redirect(url_for("add_product", category_id = category_id))
    

    if price <= float(0):
        flash("Price cannot less than or equal to zero!")
        return redirect(url_for("add_product", category_id = category_id))
    
    if quantity < 0:
        flash("Price cannot less than zero!")
        return redirect(url_for("add_product", category_id = category_id))
    
    if man_date > datetime.now():
        flash("Invalid manufacturing Date")
        return redirect(url_for("add_product", category_id = category_id))

    product = Product(name = name,
                      price = price,
                      category_id = category_id,
                      quantity = quantity,
                      man_date = man_date)
    
    db.session.add(product)
    db.session.commit()
    flash("Product added successfully :)")
    return redirect(url_for("admin"))