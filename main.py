# ---------------------------------- IMPORTS ----------------------------------
import werkzeug.security
from flask import Flask, render_template, request, url_for, redirect, flash, send_from_directory
from werkzeug.security import generate_password_hash, check_password_hash
from sqlalchemy.exc import IntegrityError, InvalidRequestError
from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin, login_user, LoginManager, login_required, current_user, logout_user

# -------------------------------- FLASK CONFIG -------------------------------
app = Flask(__name__)  # Flask App creation
app.config['SECRET_KEY'] = 'bunny-pig'  # Secret Key creation
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///users.db'  # DB Link
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False  # Turning off outdated configs
db = SQLAlchemy(app)  # Creating Database App
login_manager = LoginManager()  # Login Manager
login_manager.init_app(app)  # Initializing Login Manager


# ---------------------------------- CLASSES ----------------------------------
class User(UserMixin, db.Model):
    # User class represents DB structure and is the base for the entire
    # login and registration in the website.
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(100), unique=True)
    password = db.Column(db.String(100))
    name = db.Column(db.String(1000))
    auth_flag = UserMixin.is_authenticated


@login_manager.user_loader
def load_user(user_id):
    return User.query.filter_by(id=user_id).first()


# ---------------------------------- ROUTING ----------------------------------
@app.route('/')
def home():
    # Home routing, for a first access to the website.
    # When called, the homepage will be rendered.
    return render_template("index.html")


@app.route('/register', methods=["GET", "POST"])
def register():
    # Register routing, this is for when a user wants to register in the website.
    # It get a name, an e-mail and the password, then stores it in the database.

    if request.method == "POST":
        # If POST method, that means user is submitting the registration form.

        form_name = request.form['name']  # Fetching name
        form_email = request.form['email']  # Fetching email

        # Fetching and encrypting password
        form_password = generate_password_hash(request.form['password'],
                                               method='pbkdf2:sha256',
                                               salt_length=8)

        # Creating a User class and building its attributes with the form answers.
        new_user = User()
        new_user.name = form_name
        new_user.password = form_password
        new_user.email = form_email

        # Adding and commiting the new user to the Database.
        try:
            db.session.add(new_user)
            db.session.commit()
            # Finally, returning the secret file from the website for download,
            # while already authenticating the user.
            login_user(new_user)
            return render_template("secrets.html", name=new_user.name)

        except IntegrityError or InvalidRequestError:
            # User already registered (unique email):
            flash_register = "Username already exists! Proceed to login!"
            return render_template("register.html", flash=flash_register)

    else:
        # If the page is first loading, the register form is loaded.
        return render_template("register.html")


@app.route('/login', methods=["GET", "POST"])
def login():
    # Here the user inputs his login and password,
    # then the password is checked through the check_password_hash function.

    if request.method == "POST":
        # If POST method, user is submitting login information.

        # Step 1 - Capturing Login Info
        login_mail = request.form['email']

        # Step 2 - Fetching the DB for this user
        active_user = db.session.query(User).filter_by(email=login_mail).first()

        # Step 3 - Check if password is correct
        try:
            # Checks for password
            check_hash = check_password_hash(active_user.password, request.form['password'])
        except AttributeError:
            # Username not Found
            check_hash = False
            # Return an error message!

        if check_hash:
            login_user(active_user)
            return render_template("secrets.html", name=active_user.name)
        else:
            login_flash = "Username and password combination not found!"
            return render_template("login.html", flash=login_flash)

    return render_template("login.html")


@app.route('/secrets')
@login_required
def secrets():
    # Secrets routing, where the user can download a secret file.
    return render_template("secrets.html")


@app.route('/logout')
@login_required
def logout():
    # Logout routing, for when the user logs out of its account.
    logout_user()
    return redirect(url_for('home'))


@app.route('/download')
@login_required
def download():
    # Download routing, for when user clicks the download link.
    return send_from_directory("static/files", "cheat_sheet.pdf")


# --------------------------------- EXECUTION ---------------------------------
if __name__ == "__main__":
    app.run(debug=True)
