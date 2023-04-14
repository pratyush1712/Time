from flask import Blueprint, render_template, request, flash, redirect, url_for
from .models import User
from werkzeug.security import generate_password_hash, check_password_hash
from . import db
from flask_login import login_user, login_required, logout_user, current_user

auth = Blueprint("auth", __name__)

@auth.route("/")
@auth.route("/login", methods=["GET", "POST"])
def login():
    """
    If the user is already logged in, redirect to the init page. If the user is not logged in, check if
    the email and password match a user in the database. If they do, log the user in and redirect to the
    init page. If they don't, flash an error message and redirect to the login page
    :return: The rendered template of the login.html page.
    """
    if request.method == "POST":
        email = request.form.get("email")
        password = request.form.get("password")

        user = User.query.filter_by(email=email).first()
        if user:
            if check_password_hash(user.password_digest, password):
                flash("Logged in successfully!", category="success")
                login_user(user, remember=True)
                return redirect(url_for("views.init"))
            else:
                flash("Incorrect password, try again.", category="error")
        else:
            redirect(url_for("auth.sign_up"))
            flash("Email does not exist.", category="error")

    return render_template("login.html", user=current_user)

@auth.route("/logout")
@login_required
def logout():
    """
    Logs out the current user and redirects to the login page
    :return: a redirect to the login page.
    """
    logout_user()
    return redirect(url_for("auth.login"))

@auth.route("/sign-up", methods=["GET", "POST"])
def sign_up():
    """
    It creates a new user in the database and logs them in.
    :return: The sign_up.html template is being returned.
    """
    if request.method == "POST":
        email = request.form.get("email")
        first_name = request.form.get("firstName")
        password1 = request.form.get("password1")
        password2 = request.form.get("password2")
        maxFocusTime = request.form.get("maxFocusTime")
        preferedWorkTime = request.form.get("preferedWorkTime")

        user = User.query.filter_by(email=email).first()
        if user:
            flash("Email already exists.", category="error")
        else:
            new_user = User(
                email=email,
                name=first_name,
                password=generate_password_hash(password1, method="sha256"),
                maxFocusTime=maxFocusTime,
                preferedWorkTime=(1 if preferedWorkTime == "night" else 0),
            )
            db.session.add(new_user)
            db.session.commit()
            login_user(new_user, remember=True)
            flash("Account created!", category="success")
            return redirect(url_for("views.init"))

    return render_template("sign_up.html")
