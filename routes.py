from flask import render_template
from app import app


@app.route("/")
def signin():
    return render_template("signin.html")

@app.route("/register")
def register():
    return render_template("register.html")