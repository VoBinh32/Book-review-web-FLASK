# Books Review Website

## Web Programming with Python and JavaScript

[Project Instructions](https://docs.cs50.net/ocw/web/projects/1/project1.html)

This is my solution to CS50W Project 1.

## App Screenshots

![Login Page](https://github.com/VoBinh32/Book-review-web-FLASK/blob/main/static/project1.PNG)
![Login Page]()
![Login Page]()
![Login Page]()
![Login Page]()

## Usage

1. Register for an account
2. Login
3. Search for the book by its ISBN, author name, or title
4. Get the information about the book and write your review
5. Logout

## Setup

```
# Clone repo
$ git clone

$ cd cs50-project1

# Install all dependencies
$ pip install -r requirements.txt

# ENV Variables
$ set FLASK_APP=application.py
$ set DATABASE_URL=Your Heroku Postgres DB URI
$ set FLASK_DEBUG = 1
$ set GOODREADS_KEY = Your Goodreads Developer API Key # See: https://www.goodreads.com/api

To run the application execute the command:
$ flask run
The flask application should now be running on http://127.0.0.1:5000/

## Architecture and Design

This application uses [Flask](https://flask.palletsprojects.com/en/1.1.x/), a Python micro-framework that helps with RESTful handling of data, application routing and template binding for rendering the data from:

1. Goodreads API
2. PostgreSQL database hosted on [Heroku](https://www.heroku.com/)
```
