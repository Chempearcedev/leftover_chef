import os
from flask import (
    Flask, flash, render_template,
    redirect, request, session, url_for)
from flask_pymongo import PyMongo
from bson.objectid import ObjectId
from werkzeug.security import generate_password_hash, check_password_hash
if os.path.exists("env.py"):
    import env


app = Flask(__name__)

app.config["MONGO_DBNAME"] = os.environ.get("MONGO_DBNAME")
app.config["MONGO_URI"] = os.environ.get("MONGO_URI")
app.secret_key = os.environ.get("SECRET_KEY")

mongo = PyMongo(app)


@app.route("/")
@app.route("/get_jobs")
def get_jobs():
    jobs = list(mongo.db.jobs.find())
    return render_template("jobs.html", jobs=jobs)


@app.route("/userprofile/<username>", methods=["GET", "POST"])
def userprofile(username):

    username = mongo.db.user.find_one(
        {"username": session["user"]})["username"]

    if session["user"]:
        return render_template("userprofile.html", username=username)

    return render_template("userprofile.html", username=username)


@app.route("/loggingout")
def loggingout():
    flash("You are logged out")
    session.pop("user")
    return redirect(url_for("login"))


@app.route("/registration", methods=["GET", "POST"])
def registration():
    if request.method == "POST":
        # does user exists
        existing_user = mongo.db.user.find_one(
            {"username": request.form.get("username").lower()})

        if existing_user:
            flash("Username already exists")
            return redirect(url_for("registration"))

        registration = {
            "username": request.form.get("username").lower(),
            "password": generate_password_hash(request.form.get("password"))
        }
        mongo.db.user.insert_one(registration)

       
        session["user"] = request.form.get("username").lower()
        flash("Your Registration Was Successful!")
        return redirect(url_for("userprofile", username=session["user"]))

    return render_template("registration.html")


# LOGIN FUNCTION


@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        # checking if the username already exists
        existing_user = mongo.db.user.find_one(
            {"username": request.form.get("username").lower()})

        if existing_user:
         
            if check_password_hash(
                existing_user["password"], request.form.get("password")):
                    session["user"] = request.form.get("username").lower()
                    flash("Hello there, {}".format
                        (request.form.get("username")))
                    return redirect(url_for
                        ("userprofile", username=session["user"]))
            else:

                flash("That's an incorrect Username and/or Password")
                return redirect(url_for("login"))

        else:

            flash("That's an incorrect Username and/or Password")
            return redirect(url_for("login"))

    return render_template("login.html")


if __name__ == "__main__":
    app.run(host=os.environ.get("IP"),
            port=int(os.environ.get("PORT")),
            debug=True)