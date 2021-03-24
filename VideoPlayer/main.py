from flask import Flask, redirect, url_for, render_template, request, session, flash, send_file, escape
from datetime import timedelta
from flask_sqlalchemy import SQLAlchemy
import os

app = Flask(__name__)
app.secret_key = "feiwusaif238rusiotfuweluify349ruyfge477rfjeuiseur"
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///users.sqlite3'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.permanent_session_lifetime = timedelta(days=1)

db = SQLAlchemy(app)


class Users(db.Model):
    _id = db.Column("id", db.Integer, primary_key=True)
    username = db.Column(db.String(100))
    password = db.Column(db.String(100))

    def __init__(self, username, password):
        self.username = username
        self.password = password


@app.route("/")
def home():
    session.pop('_flashes', None)
    return render_template("index.html")


@app.route("/create", methods=["POST", "GET"])
def create_account():
    if request.method == "POST":
        session.permanent = True
        username = request.form["username"].lower()
        password = request.form["password"]

        found_user = Users.query.filter_by(username=username).first()
        if not found_user and username not in ["home", "create_account", "login", "user", "logout", "delete", "playvideo", "get_file_contents", "get_file", "search", "/", "", "\\", "create"]:
            usr = Users(username, password)
            db.session.add(usr)
            db.session.commit()
            flash("Account successfully created!")
        else:
            flash("Username has already been taken!")
        return redirect(url_for("create_account"))
    else:
        return render_template("usercreate.html")


@app.route("/login", methods=["POST", "GET"])
def login():
    if request.method == "POST":
        session.permanent = True
        username = request.form["username"]
        password = request.form["password"]

        found_user = Users.query.filter_by(username=username).first()
        if found_user:
            if found_user.password == password:
                session["user"] = username
                return redirect(url_for("user"))
            flash("Incorrect password or username")
            return redirect(url_for("login"))
        else:
            flash("Incorrect password or username")
            return redirect(url_for("login"))
    else:
        if "user" in session:
            return redirect(url_for("user"))
        return render_template("login.html")


@app.route("/user", methods=["POST", "GET"])
def user():
    if request.method == "GET":
        if "user" in session:
            username = session["user"]
            return render_template("user.html", name=username)
        else:
            flash("You are not logged in!")
            return redirect(url_for("login"))
    else:
        uploaded_file = request.files['file']
        if uploaded_file.filename != '':
            uploaded_file.save(session["user"] + '.mp4')
        flash("File Updated")
        return render_template("user.html", name=session["user"])


@app.route("/logout")
def logout():
    session.pop('_flashes', None)
    flash("You have been logged out!", "info")
    session.pop("user", None)
    session.pop("email", None)
    return redirect(url_for("login"))


@app.route("/delete", methods=["POST", "GET"])
def delete():
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]

        found_user = Users.query.filter_by(username=username).first()
        if found_user:
            if password == found_user.password:
                Users.query.filter_by(username=username).delete()
                session.pop("user", None)
                db.session.commit()
                flash(f"Successfully deleted the account {username}")
                if os.path.exists(username + ".mp4"):
                    os.remove(username + ".mp4")
                return redirect(url_for("delete"))
            else:
                flash("Invalid Password or Username")
                return redirect(url_for("delete"))
        else:
            flash("Invalid Password or Username")
            return redirect(url_for("delete"))
    else:
        return render_template("delete.html")


@app.route("/view/<username>")
def playvideo(username):
    found_user = Users.query.filter_by(username=username).first()

    if found_user and os.path.exists(username + '.mp4'):
        return redirect(url_for('get_file', filename=username + '.mp4'))
    else:
        flash("User didn't exist or user hasn't uploaded a video yet!")
        return redirect(url_for("search"))


@app.route("/get_file_contents/<filename>")
def get_file_contents(filename):
    ft = send_file(filename)
    return ft


@app.route("/get_file/<filename>")
def get_file(filename):
    if os.path.exists(filename):
        return f'<head><link rel="stylesheet" href="https://stackpath.bootstrapcdn.com/bootstrap/4.3.1/css/bootstrap.min.css" integrity="sha384-ggOyR0iXCbMQv3Xipma34MD+dH/1fQ784/j6cY/iJTQUOhcWr7x9JvoRxT2MZw1T" crossorigin="anonymous"></head><body><nav class="navbar navbar-expand-lg navbar-light bg-light"><a class="navbar-brand" href="#">Navbar</a><button class="navbar-toggler" type="button" data-toggle="collapse" data-target="#navbarNav" aria-controls="navbarNav" aria-expanded="false" aria-label="Toggle navigation"><span class="navbar-toggler-icon"></span></button><div class="collapse navbar-collapse" id="navbarNav"><ul class="navbar-nav"><li class="nav-item active"><a class="nav-link" href="/">Home <span class="sr-only">(current)</span></a></li><li><a class="nav-link" href="create">Create Account </a></li><li><a class="nav-link" href="login">Login </a></li><li><a class="nav-link" href="logout">Logout </a></li><li><a class="nav-link" href="delete">Delete Account </a></li><li><a class="nav-link" href="search">Search </a></li></ul></div></nav><script src="https://code.jquery.com/jquery-3.3.1.slim.min.js" integrity="sha384-q8i/X+965DzO0rT7abK41JStQIAqVgRVzpbzo5smXKp4YfRvH+8abtTE1Pi6jizo" crossorigin="anonymous"></script><script src="https://cdnjs.cloudflare.com/ajax/libs/popper.js/1.14.7/umd/popper.min.js" integrity="sha384-UO2eT0CpHqdSJQ6hJty5KVphtPhzWj9WO1clHTMGa3JDZwrnQq4sF86dIHNDz0W1" crossorigin="anonymous"></script><script src="https://stackpath.bootstrapcdn.com/bootstrap/4.3.1/js/bootstrap.min.js" integrity="sha384-JjSmVgyd0p3pXB1rRibZUAYoIIy6OrQ6VrjIEaFf/nJGzIxFDsf4x0xIM+B07jRM" crossorigin="anonymous"></script></body><video src="{escape(url_for("get_file_contents", filename=filename))}" controls autoplay>'
    else:
        try:
            return redirect(url_for(filename))
        except:
            flash("Video does not exist!")
            return redirect(url_for("search"))


@app.route("/search", methods=["POST", "GET"])
def search():
    if request.method == "POST":
        username = request.form["username"]
        return redirect(url_for("playvideo", username=username))
    else:
        return render_template("search.html")


if __name__ == "__main__":
    db.create_all()
    app.run(debug=True)
