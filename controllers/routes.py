from controllers import app, db, login_manager
from flask import render_template, redirect, flash, url_for, request
from controllers.forms import RegisterForm, LoginForm
from models.models import User, Subject, Chapter, Quiz, Question, Score
from flask_login import login_user, login_required, logout_user, current_user
import os


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

@app.cli.command("db-create")
def create_db():
    with app.app_context():
        db.create_all()

        admin = User.query.filter_by(username="admin@quizmaster.com").first()
        if not admin :
            admin = User(
                username="admin@quizmaster.com",
                fullname = "Quiz Master Admin"
                )
            admin.set_password("admin123")
            db.session.add(admin)
            db.session.commit()
            print("admin created")
        else:
            print("admin already there")
        print("databse created")
    



@app.route("/")
def home():
    return render_template("home.html")

@app.route("/register", methods=['GET', 'POST'])
def register():
    form = RegisterForm()
    if form.validate_on_submit():
        user = User(
            username=form.username.data,
            fullname=form.fullname.data,
            qualification=form.qualification.data,
            dob=form.dob.data
        )
        user.set_password(form.password.data)
        db.session.add(user)
        db.session.commit()
        flash('You were successfully registered')
        return redirect(url_for('login'))
    return render_template("register.html", form=form)

@app.route("/login", methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('dashboard'))
    
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()
        if user and user.check_password(form.password.data):
            login_user(user)
            return redirect(url_for('dashboard'))
        flash("Invalid username or password")
        
    return render_template("login.html", form=form)


@app.route("/dashboard")
@login_required
def dashboard():
    return render_template("dashboard.html", user=current_user)

@app.route("/logout")
@login_required
def logout():
    logout_user()
    flash('You have been logged out')
    return redirect(url_for('login'))

@app.route("/admin/login",methods=['GET','POST'])
def admin_login():
    form=LoginForm()
    if form.validate_on_submit():
        user=User.query.filter_by(username="admin@quizmaster.com").first()
        if user and user.username == form.username.data and user.check_password(form.password.data):
            login_user(user)
            flash("admin login successful")
            return  redirect("/admin/dashboard")
        else : 
            print("invalid username or password")

    return render_template("admin/login.html",form=form)


@app.route("/admin/dashboard") 
@login_required
def admin_dashboard():
    if current_user.username != "admin@quizmaster.com" :
        flash("you do not access to this page")
        return redirect(url_for("home"))
    return render_template("admin/dashboard.html")
