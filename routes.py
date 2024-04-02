from flask import render_template, request, redirect, url_for, flash, session
from app import app
from models import db, User, Category, Product, Cart, Transaction, Order
from werkzeug.security import generate_password_hash, check_password_hash
from functools import wraps


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
    return redirect(url_for("profile"))


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


@app.route("/home")
@auth_required
def home():    
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

