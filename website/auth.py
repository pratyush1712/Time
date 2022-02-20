from flask import Blueprint, render_template, request, flash, redirect, url_for
from .models import User
from werkzeug.security import generate_password_hash, check_password_hash
from . import db
from flask_login import login_user, login_required, logout_user, current_user


auth = Blueprint('auth', __name__)

@auth.route("/")
@auth.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')

        user = User.query.filter_by(email=email).first()
        if user:
            if check_password_hash(user.password_digest, password):
                flash('Logged in successfully!', category='success')
                login_user(user, remember=True)
                return redirect(url_for('views.init'))
            else:
                flash('Incorrect password, try again.', category='error')
        else:
            redirect(url_for('auth.sign_up'))
            flash('Email does not exist.', category='error')

    return render_template("login.html", user=current_user)


@auth.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('auth.login'))


@auth.route('/sign-up', methods=['GET', 'POST'])
def sign_up():
    if request.method == 'POST':
        email = request.form.get('email')
        first_name = request.form.get('firstName')
        password1 = request.form.get('password1')
        password2 = request.form.get('password2')
        maxFocusTime = request.form.get("maxFocusTime")
        preferedWorkTime = request.form.get("preferedWorkTime")

        user = User.query.filter_by(email=email).first()
        if user:
            flash('Email already exists.', category='error')
        else:
            new_user = User(email=email, name=first_name, password=generate_password_hash(
                password1, method='sha256'), maxFocusTime=maxFocusTime, preferedWorkTime = (1 if preferedWorkTime=='night' else 0))
            db.session.add(new_user)
            db.session.commit()
            login_user(new_user, remember=True)
            flash('Account created!', category='success')
            return redirect(url_for('views.init'))

    return render_template("sign_up.html")








# @auth.route("/login", methods=['POST'])
# def login():
#     email = request.form.get("email")
#     password = request.form.get("password")
#     if email is None or password is None:
#         return json.dumps("Invalid email or password")
    
#     valid_cred, user = verify_credentials(email, password)
#     if not valid_cred:
#         return json.dumps("Invalid!")
#     return json.dumps(user.serialize())

# @auth.route("/register/", methods=['POST'])
# def register_account():
#     email = request.form.get("email")
#     password = request.form.get("password")
#     name = request.form.get("name")
#     maxFocusTime = request.form.get("maxFocusTime")
#     preferedWorkTime = request.form.get("preferedWorkTime")

#     if email is None or password is None:
#         return json.dumps("Invalid email or password")
    
#     created, user = create_user(name, email, password, maxFocusTime, preferedWorkTime)

#     if not created:
#         return json.dumps("User already exists", 403)
    
#     return json.dumps({
#         "session_token": user.session_token,
#         "session_expiration": str(user.session_expiration),
#         "update_token": user.update_token
#     })

# @auth.route('/session/', methods=['POST'])
# def update_session():
#     success, update_token = extract_token(request)
    