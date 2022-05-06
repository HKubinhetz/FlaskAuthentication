# ---------------------------------- IMPORTS ----------------------------------
from flask import Flask, render_template, request, url_for, redirect, flash, send_from_directory
from werkzeug.security import generate_password_hash, check_password_hash
from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin, login_user, LoginManager, login_required, current_user, logout_user


# -------------------------------- FLASK CONFIG -------------------------------
app = Flask(__name__)
app.config['SECRET_KEY'] = 'bunny-pig'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///users.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)


# --------------------------------- DB CONFIG ---------------------------------
class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(100), unique=True)
    password = db.Column(db.String(100))
    name = db.Column(db.String(1000))
# Line below only required once, when creating DB.
# db.create_all()


# ---------------------------------- ROUTING ----------------------------------
@app.route('/')
def home():
    return render_template("index.html")


@app.route('/register', methods=["GET", "POST"])
def register():

    if request.method == "POST":
        form_name = request.form['name']
        form_email = request.form['email']
        form_password = request.form['password']

        new_user = User()
        new_user.name = form_name
        new_user.password = form_password
        new_user.email = form_email

        db.session.add(new_user)
        db.session.commit()

        return render_template("secrets.html", name=new_user.name)

    else:
        return render_template("register.html")


@app.route('/login')
def login():
    return render_template("login.html")


@app.route('/secrets')
def secrets():
    return render_template("secrets.html")


@app.route('/logout')
def logout():
    pass


@app.route('/download')
def download():
    pass


# --------------------------------- EXECUTION ---------------------------------
if __name__ == "__main__":
    app.run(debug=True)
