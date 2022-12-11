import os

from cs50 import SQL
from flask import Flask, flash, redirect, render_template, request, session
from flask_session import Session
from werkzeug.security import check_password_hash, generate_password_hash

from helpers import login_required

# Configure application
app = Flask(__name__)


# Configure session to use filesystem (instead of signed cookies)
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

# Configure CS50 Library to use SQLite database
db = SQL("sqlite:///birthdays.db")

# Make sure API key is set
if not os.environ.get("API_KEY"):
    raise RuntimeError("API_KEY not set")

@app.after_request
def after_request(response):
    """Ensure responses aren't cached"""
    response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    response.headers["Expires"] = 0
    response.headers["Pragma"] = "no-cache"
    return response


@app.route("/login", methods=["GET", "POST"])
def login():
    """Log user in"""

    # Forget any user_id
    session.clear()

    # User reached route via POST (as by submitting a form via POST)
    if request.method == "POST":

        # Query database for username
        rows = db.execute("SELECT * FROM users WHERE username = ?", request.form.get("username"))

        # Ensure username exists and password is correct
        if len(rows) != 1 or not check_password_hash(rows[0]["hash"], request.form.get("password")):
            flash("Invalid username and/or password")
            return redirect("/login")

        # Remember which user has logged in
        session["user_id"] = rows[0]["id"]

        # Redirect user to home page
        return redirect("/")

    # User reached route via GET (as by clicking a link or via redirect)
    else:
        return render_template("login.html")


@app.route("/logout")
def logout():
    """Log user out"""

    # Forget any user_id
    session.clear()

    # Redirect user to main page
    return redirect("/")


@app.route("/register", methods=["GET", "POST"])
def register():
    """Register user"""
    if (request.method == "GET"):
        return render_template("signup.html")
    else:
        # assigns the different request.form.get() to three different uniqur variables #
        username = request.form.get("username")
        password = request.form.get("password")

        # hashed out the user's password #
        hash = generate_password_hash(password)

        # try helps test and see if there are errors in the database execution and except handles error by returning apology
        try:
            user_id = db.execute("INSERT INTO users (username, hash) VALUES(?, ?)", username, hash)
        except:
            flash("Username already exists")
            return redirect("/register")

    session["user_id"] = user_id
    return redirect("/")


@app.route("/contacts", methods=["GET", "POST"])
@login_required
def contacts():
    user_id = session["user_id"]
    contacts_db = db.execute("SELECT * FROM contacts JOIN favorites ON contacts.id = favorites.contacts_id WHERE contacts.user_id = :id", id=user_id)
    return render_template("contacts.html", contacts=contacts_db)


@app.route("/form", methods=["GET", "POST"])
def form():
    if request.method == "GET":
        return render_template("form.html")
    else:
        # makes variables equal to corresponding request.form.get() #
        user_id = request.form.get("email")
        name = request.form.get("name")
        number = request.form.get("number")
        email = request.form.get("email")
        address = request.form.get("address")
        birthday = request.form.get("birthday")
        profession = request.form.get("profession")
        color = request.form.get("color")
        food = request.form.get("food")
        movie = request.form.get("movie")
        book = request.form.get("book")
        hobby = request.form.get("hobby")
        notes = request.form.get("notes")
        if not name:
            flash("Must fill out name")
            return redirect("/form")
        if not number.isdigit():
            flash("Phone number must only contain integers")
            return redirect("/form")

        number = int(number)

        db.execute("INSERT INTO contacts (user_id, name, number, email, address, profession, notes, birthday) VALUES(?, ?, ?, ?, ?, ?, ?, ?)",
                   user_id, name, number, email, address, profession, notes, birthday)

        db.execute("INSERT INTO favorites (user_id, color, food, movie, book, hobby) VALUES(?, ?, ?, ?, ?, ?)",
                   user_id, color, food, movie, book, hobby)
        flash("successfully submitted")
        return redirect("/form")


@app.route("/")
def homepage():
    return render_template("homepage.html")


@app.route("/contact-us")
def contact():
    return render_template("contact2.html")
