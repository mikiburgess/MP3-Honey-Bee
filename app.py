"""
    MILESTONE PROJECT 3 by MIKHAILA BURGESS
    "HONEY BEE"
    - - - - - - - - - - - - - - - - - - - -
    Web Application
"""

# IMPORT EXTERNAL PACKAGES
import os
import datetime
from flask_pymongo import PyMongo
from flask import (
    Flask, flash, render_template,
    redirect, request, session, url_for)
from werkzeug.security import generate_password_hash, check_password_hash
from bson.objectid import ObjectId  # Enables us to work with MongoDB Object IDs

if os.path.exists("env.py"):
    import env


# INITIALISE WEB APPLICATION
app = Flask(__name__)

app.config["MONGO_URI"] = os.environ.get("MONGO_URI")
app.secret_key = os.environ.get("SECRET_KEY")

mongo = PyMongo(app)


# APPLICATION ENDPOINTS
@app.route("/")
@app.route("/home")
def home():
    return render_template("home.html")


@app.route("/signin", methods=["GET", "POST"])
def signin():
    if request.method == "POST":
        # check username exists in db
        existing_user = mongo.db.siteUsers.find_one(
            {"username": request.form.get("username").lower()})
    
        if existing_user:
            # ensure hashed password matches user input
            if check_password_hash(existing_user["password"], request.form.get("password")):
                session["user"] = request.form.get("username").lower()
                session["beekeeper"] = existing_user["beekeeper"]
                session["admin"] = existing_user["administrator"]

                if session["beekeeper"]:
                    flash(f"Welcome back, Beekeeper {session['user']}")
                else:
                    flash(f"Welcome back, {session['user']}")
                return redirect(url_for("home", username=session["user"]))
            else:
                # invalid password match
                flash("Incorrect Username and/or Password")
                return redirect(url_for("signin"))
        else:
            # username doesn't exist
            flash("Incorrect Username and/or Password")
            return redirect(url_for("signin"))
    
    return render_template("signin.html")


@app.route("/signout")
def signout():
    # remove user from session cookies
    flash("You have been logged out")
    session.pop("user")
    session["beekeeper"] = False
    session["admin"] = False
    return redirect(url_for("home"))


@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        print(request.form.get("firstname"))
        # check if username already exists in db
        existing_user = mongo.db.siteUsers.find_one(
            {"username": request.form.get("username").lower()})
        
        if existing_user:
            flash("Username already exists")
            return redirect(url_for("register"))

        # check if user is a beekeeper
        if request.form.get("beekeeper"):
            beekeeper = True
        else:
            beekeeper = False

        # add user registration to database
        register = {
            "username": request.form.get("username").lower(),
            "password": generate_password_hash(request.form.get("password")),
            "firstname": request.form.get("firstname").lower(),
            "surname": request.form.get("surname").lower(),
            "beekeeper": beekeeper,
            "administrator": False
        }
        mongo.db.siteUsers.insert_one(register)

        # put the new user into 'session' cookie
        session["user"] = request.form.get("username").lower()
        flash(f"Registration successful. Welcome {session['user']}")
        return redirect(url_for("home", username=session["user"]))

    return render_template("register.html")


@app.route("/hive_management", methods=["GET", "POST"])
def hive_management():
    
    # POST = New hive record entered
    if request.method == "POST":
        print("DATA: \n")
        print("\tReference: " + request.form.get("reference"))
        print("\tApiary: " + request.form.get("apiary"))
        print("\tHive Type: " + request.form.get("hiveType"))
        print("\tBees: " + request.form.get("bees"))
        print("\tBeekeeper: " + session["user"])

        try:
            # add user registration to database
            newHive = {
                "apiary": request.form.get("apiary").lower(),
                "reference": request.form.get("reference").lower(),
                "hiveType": request.form.get("hiveType").lower(),
                "bees": request.form.get("bees").lower(),
                "beekeeper": session["user"]
            }
            mongo.db.hives.insert_one(newHive)
        except Exception as e:
            print(e)

    # GET = show record of hives for current beekeeper
    hives = mongo.db.hives.find(
        {"beekeeper": session["user"]}
    )

    return render_template("hive_management.html", hives=list(hives))




# MAIN - RUNNING IN DEBUG MODE
if __name__ == "__main__":
    app.run(host=os.environ.get("IP"),
            port=int(os.environ.get("PORT")),
            debug=True)
