from controllers import create_app, db  # Ensure db is imported
from flask import render_template
from models.models import User, Subject, Chapter, Quiz, Question, Score

app = create_app()  # Initialize Flask app

@app.cli.command("db-create")  # Register CLI command
def create_db():
    """Creates the database tables"""
    with app.app_context():  # Ensure the app context is active
        db.create_all()
        print("Database Created")

@app.route("/")
def home():
    return render_template("home.html")

@app.route("/about")
def about():
    return render_template("about.html")
