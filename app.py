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
from werkzeug.exceptions import HTTPException
from bson.objectid import ObjectId  # Enables us to work with MongoDB Object IDs

if os.path.exists("env.py"):
    import env


# INITIALISE WEB APPLICATION
app = Flask(__name__)

app.config["MONGO_URI"] = os.environ.get("MONGO_URI")
app.secret_key = os.environ.get("SECRET_KEY")

mongo = PyMongo(app)


"""
 APPLICATION FUNCTIONS
 ---------------------
"""

# LOAD BEEKEEPER APIARIES UPON LOGIN/CHANGE
def load_apiaries():
    if session["beekeeper"]:
        # Get list of apiary names from database and store in session variable
        session["apiaries"] = []
        apiaries = mongo.db.apiaries.find({"beekeeper": session['user']})
        for apiary in apiaries:
            session["apiaries"].append(apiary["apiary"])
    print(session['apiaries'])


"""
 APPLICATION ENDPOINTS
 ---------------------
"""

# NON-SPECIFIC ERROR HANDLER
# @app.errorhandler(Exception)
# def handle_exception(e):
#     return render_template("error.html", e=e)


# APPLICATION ENDPOINTS

@app.route("/placeholder")
def placeholder():
    return render_template("placeholder.html")
    # return render_template("dnd.html")


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


@app.route("/apiary_management")
def apiary_management():
    apiaries = list(mongo.db.apiaries.find(
            {"beekeeper": session["user"]}
        ).sort("reference", 1))
    return render_template("apiary_management.html", apiaries=apiaries)


@app.route("/add_apiary", methods=["GET", "POST"])
def add_apiary():
    if request.method == "POST":
        try:
            existing_apiary = mongo.db.apiaries.find_one(
                {"beekeeper": session["user"], 
                    "apiary": request.form.get("apiary").lower()})
            print(existing_apiary)
            if existing_apiary:
                flash("Error: Apiary already exists")
                return redirect(url_for("add_apiary"))
            
            # add new apiary to database
            newApiary = {
                "beekeeper": session["user"],
                "apiary": request.form.get("apiary").lower(),
                "description": request.form.get("apiary-description"),
                "date_added": datetime.datetime.now().strftime("%d %B %Y")
            }
        
            mongo.db.apiaries.insert_one(newApiary)
            flash("Success. New apiary added.")
            load_apiaries()

        except Exception as e:
            flash("Error ocurred. New apiary not added. Please try again")
            print(e)

        return redirect(url_for('apiary_management', apiary="all"))

    return render_template("add_apiary.html")


@app.route("/manage_apiary/<apiary_id>", methods=["GET", "POST"])
def manage_apiary(apiary_id):
    if request.method == "POST":
        submit = {
            "beekeeper": session["user"],
            "apiary": request.form.get("apiary"),
            "description": request.form.get("apiary-description"),
            "last_updated": datetime.datetime.now().strftime("%d %B %Y")
        }
        mongo.db.apiaries.update_one({"_id": ObjectId(apiary_id)}, {"$set": submit})
        flash("Apiary Details Successfully Updated")
    apiary = mongo.db.apiaries.find_one({"_id": ObjectId(apiary_id)})  
    return render_template("manage_apiary.html", apiary=apiary)


@app.route('/delete_apiary/<apiary_id>')
def delete_apiary(apiary_id):
    mongo.db.apiaries.delete_one({"_id": ObjectId(apiary_id)})
    flash("Apiary Successfully Deleted")
    return redirect(url_for("apiary_management"))


@app.route("/hive_management/<apiary>")
def hive_management(apiary):
    load_apiaries()
    # show record of hives for current beekeeper
    if apiary == "all":
        # no apiary selected, so return all
        hives = list(mongo.db.hives.find(
            {"beekeeper": session["user"]}
        ).sort("apiary", 1))
    else:
        # specific apiary selected, so return hives in that beekeepers apiary
        hives = list(mongo.db.hives.find(
            {"beekeeper": session["user"], "apiary": apiary}
        ).sort("reference", 1))
        
    return render_template("hive_management.html", hives=hives)


@app.route("/add_hive", methods=["GET", "POST"])
def add_hive():
    load_apiaries()
    # POST = New hive record entered
    if request.method == "POST":
        try:
            # add user registration to database
            newHive = {
                "beekeeper": session["user"],
                "apiary": request.form.get("apiary").lower(),
                "reference": request.form.get("reference").lower(),
                "hiveType": request.form.get("hiveType").lower(),
                "bees": request.form.get("bees").lower(),
                "date_added": datetime.datetime.now().strftime("%d %B %Y")
            }
            mongo.db.hives.insert_one(newHive)
            flash("Success. New hive added.")
        except Exception as e:
            flash("Error ocurred. New hive not added. Please try again")
            print(e)

        return redirect(url_for('hive_management', apiary="all"))
    
    return render_template("add_hive.html")


@app.route("/edit_hive/<hive_id>", methods=["GET", "POST"])
def edit_hive(hive_id):
    if request.method == "POST":
        submit = {
            "beekeeper": session["user"],
            "apiary": request.form.get("apiary"),
            "reference": request.form.get("reference"),
            "hiveType": request.form.get("hiveType"),
            "bees": request.form.get("bees"),
            "last_updated": datetime.datetime.now().strftime("%d %B %Y")
        }
        mongo.db.hives.update_one({"_id": ObjectId(hive_id)}, {"$set": submit})
        flash("Hive Details Successfully Updated")
    hive = mongo.db.hives.find_one({"_id": ObjectId(hive_id)})
    return render_template("edit_hive.html", hive=hive)


@app.route('/delete_hive/<hive_id>')
def delete_hive(hive_id):
    mongo.db.hives.delete_one({"_id": ObjectId(hive_id)})
    flash("Hive Successfully Deleted")
    return redirect(url_for("hive_management", apiary="all"))


@app.route('/hive_inspection/<hive_id>')
def hive_inspection(hive_id):
    hive = mongo.db.hives.find_one({"_id": ObjectId(hive_id)})
    return render_template("hive_inspection.html", hive=hive)


# MAIN - RUNNING IN DEBUG MODE
if __name__ == "__main__":
    app.run(host=os.environ.get("IP"),
            port=int(os.environ.get("PORT")),
            debug=True)
