from flask import render_template, request, redirect, url_for, flash
from app import app
from models import db, User, Category, Product, Cart, Transaction, Order
from werkzeug.security import generate_password_hash, check_password_hash

@app.route("/")
def home():
    return render_template("index.html")

@app.route("/signin")
def signin():
    return render_template("signin.html")

@app.route("/signin", methods = ["POST"])
def sigin_post():
    username = request.form.get("username")
    password = request.form.get("password")

    if not username or not password:
        flash("Username and Password cannot be empty.")
        return redirect(url_for(signin))
    
    user = User.query.filter_by(username=username).first()

    if not user or not check_password_hash(user.passhash, password):
        flash("Username or password is incorrect.")
        return redirect(url_for(signin))
    
    return redirect(url_for("index"))
    

@app.route("/register")
def register():
    return render_template("register.html")

@app.route("/register", methods = ["POST"])
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
    

    passhash = generate_password_hash(password)

    new_user = User(name=name, username=username, passhash=passhash)
    db.session.add(new_user)
    db.session.commit()
    return redirect(url_for("signin"))
