import os
import sys
import json
import requests
from flask import Flask, session, render_template, request, redirect, jsonify, flash
from flask_session import Session
from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker
from werkzeug.security import check_password_hash, generate_password_hash
from helpers import login_required

app = Flask(__name__)

# Check for environment variable
if not os.getenv("DATABASE_URL"):
    raise RuntimeError("DATABASE_URL is not set")

# Configure session to use filesystem
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

# Set up database
engine = create_engine(os.getenv("DATABASE_URL"))
db = scoped_session(sessionmaker(bind=engine))


@app.route("/")
@login_required
def index():
    """ Show search box """
    return render_template("index.html")

@app.route("/login", methods=["GET", "POST"])
def login():
    """Log user in"""

    # Forget any user_id
    session.clear()
    if request.method == "POST":
            username = request.form.get("username")
            # Ensure username was submitted
            if not username:
                return render_template("apology.html", message="must provide username")
            # Ensure password was submitted
            elif not request.form.get("password"):
                return render_template("apology.html", message="must provide password")

            # Query database for username
            rows = db.execute("SELECT * FROM users WHERE username = :username",
                            {"username": username})
            qy = rows.fetchone()

            # Ensure username exists and password is correct
            if qy == None or not check_password_hash(qy[2], request.form.get("password")):
                return render_template("apology.html", message="invalid password/username")

            # Remember which user has logged in
            session["user_id"] = qy[0]

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

    # Redirect user to login form
    return redirect("/")

@app.route("/register", methods=["GET", "POST"])
def register():
    """Register user"""
    session.clear()
    if request.method == "POST":
        username = request.form.get("username")
        # Ensu username was submitted
        if not username:
            return render_template("apology.html", message="must provide username")
        # Ensure password was submitted
        elif not request.form.get("password"):
            return render_template("apology.html", message="must provide password")
        # Ensure confirm password is correct
        elif request.form.get("password") != request.form.get("confirm-pass"):
            return render_template("apology.html", message="confirmation password does not match!")
        check = db.execute("SELECT * FROM users WHERE username = :username",
                          {"username": username}).fetchone()
        if check:
            return render_template("apology.html", message="username already taken")

        hashedPassword = generate_password_hash(request.form.get("password"), method='pbkdf2:sha256', salt_length=8)
        db.execute("INSERT INTO users (username, password) VALUES (:username, :password)",
                    {"username": username, 
                    "password":hashedPassword})
        db.commit()
        rows = db.execute("SELECT * FROM users WHERE username = :username",
            {"username": username}).fetchone()

        # Remember which user has logged in
        session["user_id"] = rows[0]
        flash("Registered!")

        # Redirect user to home page
        return redirect("/")

    # User reached route via GET (as by clicking a link or via redirect)
    else:
        return render_template("register.html")

@app.route("/search", methods=["GET"])
@login_required
def search():
    """Search for a book"""
    if not request.args.get("book"):
        return render_template("apology.html", message="must provide a name")
    
    q = '%' + request.args.get("book") + '%'

    q = q.title()

    rows = db.execute("SELECT isbn, title, author, year FROM books WHERE isbn LIKE :q OR title LIKE :q OR author LIKE :q LIMIT 10",
            {"q": q})
    if rows.rowcount == 0:
        return render_template("apology.html", message="book not found")
    books = rows.fetchall()

    return render_template("search.html", books=books)

@app.route("/book/<isbn>", methods=["GET","POST"])
@login_required
def book(isbn):
    if request.method == "POST":
        stars = request.form.get("stars")
        stars = int(stars)
        review = request.form.get("review")

        rows = db.execute("SELECT id FROM books WHERE isbn = :isbn", {"isbn": isbn})

        bookid = rows.fetchone()
        bookid = bookid[0]
        currentuser = session["user_id"]
        userreview = db.execute("SELECT * FROM reviews WHERE user_id = :user_id AND book_id = :book_id",
        {"user_id": currentuser, "book_id": bookid})

        if userreview.rowcount == 1:
            flash("Users should not be able to submit multiple reviews for the same book")
            return redirect("/book/" + isbn)
        
        db.execute("INSERT INTO reviews (book_id, user_id, stars, review) VALUES (:book_id, :user_id, :stars, :review)",
        {"user_id": currentuser, "book_id": bookid, "stars": stars, "review": review})

        db.commit()
        flash("Submitted!")
        return redirect("/book/" + isbn)
    else:
        rows = db.execute("SELECT isbn, title, author, year FROM books WHERE isbn = :isbn",
        {"isbn": isbn})

        info = rows.fetchall()
        
        """ GOODREADS reviews """
        key = os.getenv("yTzonnaarqZZuKfUsd3keg")
        res = requests.get("https://www.goodreads.com/book/review_counts.json",
        params={"key": key, "isbns": isbn})
        response = res.json()
        response = response['books'][0]
        info.append(response)
        """ Users reviews """

         # Search book_id by ISBN
        query = db.execute("SELECT id FROM books WHERE isbn = :isbn",
                        {"isbn": isbn})

        # Save id into variable
        book = query.fetchone() # (id,)
        book = book[0]

        # Fetch book reviews
        # Date formatting (https://www.postgresql.org/docs/9.1/functions-formatting.html)
        results = db.execute("SELECT users.username, review, stars FROM users JOIN reviews ON users.id = reviews.user_id WHERE book_id = :book",
        {"book": book})

        reviews = results.fetchall()
        return render_template("book.html", info=info, reviews=reviews)
@app.route("/api/<isbn>", methods=["GET"])
@login_required
def api(isbn):
    rows = db.execute("SELECT title, author, year, isbn, COUNT(reviews.id) AS review_count, AVG(reviews.stars) AS average_score \
    FROM books JOIN reviews ON books.id = reviews.book_id WHERE isbn = :isbn GROUP BY title, author, year, isbn",
    {"isbn": isbn})

    if rows.rowcount != 1:
        return jsonify({"Error": "Invalid ISBN number"}), 404

    row = rows.fetchone()

    result = dict(row.items())
    result['average_score'] = float('%.2f'%(result['average_score']))
    return jsonify(result)