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
from bson.objectid import ObjectId

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


"""
 APPLICATION ENDPOINTS
 ---------------------
"""


# ERROR HANDLER ENDPOINTS
@app.errorhandler(400)
@app.errorhandler(401)
@app.errorhandler(404)
@app.errorhandler(500)
@app.errorhandler(502)
def page_not_found(error):
    return render_template('error.html', error=error)


# APPLICATION ENDPOINTS

@app.route("/placeholder")
def placeholder():
    return render_template("placeholder.html")
    # return render_template("dnd.html")


@app.route("/")
@app.route("/home")
def home():
    return render_template("home.html")


@app.route("/learn_about_bees")
def learn_about_bees():
    return render_template("learn_about_bees.html")


@app.route("/about")
def about():
    return render_template("about.html")


@app.route("/signin", methods=["GET", "POST"])
def signin():
    if request.method == "POST":
        # check username exists in db
        existing_user = mongo.db.siteUsers.find_one(
            {"username": request.form.get("username").lower()})
        # if user is registered, check password
        if existing_user:
            # ensure hashed password matches user input
            if check_password_hash(existing_user["password"],
                                   request.form.get("password")):
                session["user"] = request.form.get("username").lower()
                session["beekeeper"] = existing_user["beekeeper"]
                session["admin"] = existing_user["administrator"]

                if session["beekeeper"]:
                    flash(f"Welcome, Beekeeper {session['user']}")
                else:
                    flash(f"Welcome, {session['user']}")
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
    register = {}
    if request.method == "POST":
        try:
            # check if user is a beekeeper
            if request.form.get("beekeeper"):
                beekeeper = True
            else:
                beekeeper = False

            # store user entered data
            register = {
                "username": request.form.get("username").lower(),
                "password": generate_password_hash(
                    request.form.get("password")),
                "firstname": request.form.get("firstname").lower(),
                "surname": request.form.get("surname").lower(),
                "beekeeper": beekeeper,
                "administrator": False
            }

            # check if username already exists in db
            existing_user = mongo.db.siteUsers.find_one(
                {"username": request.form.get("username").lower()})
            if existing_user:
                flash("Username already exists")
                return render_template("register.html", register=register)

            # check passwords match
            if request.form.get("password") != request.form.get(
                    "password-repeat"):
                flash("Passwords do not match. Please try again.")
                return render_template("register.html", register=register)

            # data validation complete so record details in database
            mongo.db.siteUsers.insert_one(register)
            flash("Registration successful.  You can now sign in.")
            return redirect(url_for("signin"))

        except Exception as e:
            flash("Error ocurred. Registration unsuccessful. Please try again")
            mongo.db.exceptionLog.insert_one(
                {"datetime": datetime.datetime.now(),
                 "action": "Register new user",
                 "exception": e})

    return render_template("register.html", register=register)


@app.route("/apiary_management")
def apiary_management():
    apiaries = list(mongo.db.apiaries.find(
            {"beekeeper": session["user"]}
        ).sort("colony", 1))
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
            today = datetime.datetime.now()
            newApiary = {
                "beekeeper": session["user"],
                "apiary": request.form.get("apiary").lower(),
                "description": request.form.get("apiary-description"),
                "date_added": today.strftime("%d %B %Y"),
                "update_history": [{"date": today,
                                    "action": "New apiary created"}]
            }
            mongo.db.apiaries.insert_one(newApiary)
            flash("Success. New apiary added.")
            load_apiaries()
        except Exception as e:
            flash("Error ocurred. New apiary not added. Please try again")
            mongo.db.exceptionLog.insert_one(
                {"datetime": datetime.datetime.now(),
                 "action": "Add new apiary",
                 "exception": e})
        return redirect(url_for('apiary_management', apiary="all"))

    return render_template("add_apiary.html")


@app.route("/manage_apiary/<apiary_id>", methods=["GET", "POST"])
def manage_apiary(apiary_id):
    if request.method == "POST":
        try:
            edit_date = datetime.datetime.now()
            # set data for apiary
            mongo.db.apiaries.update_one(
                {"_id": ObjectId(apiary_id)},
                {"$set": {
                    "beekeeper": session["user"],
                    "apiary": request.form.get("apiary"),
                    "description": request.form.get("apiary-description"),
                    "last_updated": edit_date.strftime("%d %B %Y")
                }})
            # add current datetime to update history
            mongo.db.apiaries.update_one(
                {"_id": ObjectId(apiary_id)},
                {"$addToSet": {
                    "update_history":
                        {"date": edit_date,
                            "action": "Content edited"}
                }})
            flash("Apiary Details Successfully Updated")
        except Exception as e:
            flash("Error ocurred. Apiary not updated. Please try again")
            mongo.db.exceptionLog.insert_one(
                {"datetime": datetime.datetime.now(),
                 "action": "Update apiary", "exception": e})

    apiary = mongo.db.apiaries.find_one({"_id": ObjectId(apiary_id)})
    return render_template("manage_apiary.html", apiary=apiary)


@app.route('/delete_apiary/<apiary_id>')
def delete_apiary(apiary_id):
    try:
        mongo.db.apiaries.delete_one({"_id": ObjectId(apiary_id)})
        flash("Apiary Successfully Deleted")
    except Exception as e:
        flash("Error ocurred. Apiary not deleted.")
        mongo.db.exceptionLog.insert_one(
                {"datetime": datetime.datetime.now(),
                 "action": "Delete apiary",
                 "exception": e})
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
        ).sort("colony", 1))
    return render_template("hive_management.html", hives=hives)


@app.route("/add_hive", methods=["GET", "POST"])
def add_hive():
    load_apiaries()
    # POST = New hive record entered
    if request.method == "POST":
        try:
            # add user registration to database
            today = datetime.datetime.now()
            newHive = {
                "beekeeper": session["user"],
                "apiary": request.form.get("apiary").lower(),
                "colony": request.form.get("colony").lower(),
                "hiveType": request.form.get("hiveType").lower(),
                "bees": request.form.get("bees").lower(),
                "queenColor": request.form.get("queenColor").lower(),
                "description": request.form.get("hiveDescription"),
                "date_added": today.strftime("%d %B %Y"),
                "update_history": [{"date": today,
                                    "action": "New hive created"}]
            }
            mongo.db.hives.insert_one(newHive)
            flash("Success. New hive added.")
        except Exception as e:
            flash("Error ocurred. New hive not added. Please try again")
            mongo.db.exceptionLog.insert_one(
                {"datetime": datetime.datetime.now(),
                 "action": "Add new hive",
                 "exception": e})

        return redirect(url_for('hive_management', apiary="all"))
    return render_template("add_hive.html")


@app.route("/manage_hive/<hive_id>", methods=["GET", "POST"])
def manage_hive(hive_id):
    if request.method == "POST":
        try:
            edit_date = datetime.datetime.now()
            mongo.db.hives.update_one(
                {"_id": ObjectId(hive_id)},
                {"$set": {
                    "beekeeper": session["user"],
                    "apiary": request.form.get("apiary"),
                    "colony": request.form.get("colony"),
                    "hiveType": request.form.get("hiveType"),
                    "bees": request.form.get("bees"),
                    "queenColor": request.form.get("queenColor"),
                    "description": request.form.get("hiveDescription"),
                    "last_updated": edit_date.strftime("%d %B %Y")
                }})
            # add current datetime to update history
            mongo.db.hives.update_one(
                {"_id": ObjectId(hive_id)},
                {"$addToSet": {
                    "update_history":
                        {"date": edit_date,
                            "action": "Content edited"}
                }})
            flash("Hive Details Successfully Updated")
        except Exception as e:
            flash("Error ocurred. Hive not updated. Please try again")
            mongo.db.exceptionLog.insert_one(
                {"datetime": datetime.datetime.now(),
                 "action": "Update hive",
                 "exception": e})

    hive = mongo.db.hives.find_one({"_id": ObjectId(hive_id)})
    return render_template("manage_hive.html", hive=hive)


@app.route('/delete_hive/<hive_id>')
def delete_hive(hive_id):
    try:
        mongo.db.hives.delete_one({"_id": ObjectId(hive_id)})
        flash("Hive Successfully Deleted")
    except Exception as e:
        flash("Error ocurred. Hive not deleted.")
        mongo.db.exceptionLog.insert_one(
                {"datetime": datetime.datetime.now(),
                 "action": "Delete hive",
                 "exception": e})
    return redirect(url_for("hive_management", apiary="all"))


@app.route('/hive_inspection/<hive_id>', methods=["GET", "POST"])
def hive_inspection(hive_id):
    hive = mongo.db.hives.find_one({"_id": ObjectId(hive_id)})
    # POST = New hive inspection entered
    if request.method == "POST":
        try:
            # check if apiary and/or colony have been identified
            if 'apiary' not in hive:
                hive["apiary"] = "unspecified"
            if 'colony' not in hive:
                hive["colony"] = "unspecified"
            # get inspection data and insert into database
            today = datetime.datetime.now()
            newInspection = {
                "beekeeper": session["user"],
                "apiary": hive["apiary"],
                "colony": hive["colony"],
                "hiveID": hive["_id"],
                "inspectionDate": request.form.get("inspectionDate"),
                # Queen
                "queenPresent": request.form.get("queenPresent") == 'on',
                "queenClipped": request.form.get("queenClipped") == 'on',
                "queenCellsSeen": request.form.get("queenCellsSeen"),
                "queenCellsRemoved": request.form.get("queenCellsRemoved"),
                # Brood
                "eggsSeen": request.form.get("eggsSeen") == 'on',
                "broodSeen": request.form.get("broodSeen") == 'on',
                "broodPattern": request.form.get("broodPattern") == 'on',
                "broodDrones": request.form.get("broodDrones") == 'on',
                "broodFrames": request.form.get("broodFrames"),
                "noBrood": request.form.get("noBrood") == 'on',
                "eggRoom": request.form.get("eggRoom"),
                # Stores and Feed
                "storesAvailable": request.form.get("storesAvailable"),
                "syrupAmount": request.form.get("syrupAmount"),
                "syrupType": request.form.get("syrupType"),
                "fondantAmount": request.form.get("fondantAmount"),
                # Colony Health
                "healthStatus": request.form.get("healthStatus"),
                "healthCB": request.form.get("healthCB"),
                "healthEFB": request.form.get("healthEFB"),
                "healthAFB": request.form.get("healthAFB"),
                "healthCBPV": request.form.get("healthCBPV"),
                "varroaLevel": request.form.get("varroaLevel"),
                "varroaPop": request.form.get("varroaPop"),
                # Temper
                "colonyTemper": request.form.get("colonyTemper"),
                # Weather
                "temperature": request.form.get("temperature"),
                "weather": request.form.get("weather"),
                # Supers
                "supers": request.form.get("supers"),
                "supersChange": request.form.get("supersChange"),
                # Inspection notes
                "inspectionNotes": request.form.get("inspectionNotes"),
                "date_added": today.strftime("%Y-%m-%d"),
                "update_history": [{"date": today,
                                    "action": "New inspection record created"}]
            }

            mongo.db.hiveInspections.insert_one(newInspection)
            flash("Success. Hive inspection recorded.")

        except Exception as e:
            flash("Error ocurred. Inspection not recorded. Please try again")
            mongo.db.exceptionLog.insert_one(
                {"datetime": datetime.datetime.now(),
                 "action": "Add hive inspection record",
                 "exception": e})

        return redirect(url_for('hive_inspection', hive_id=hive_id))
    return render_template("hive_inspection.html", hive=hive)


@app.route("/inspection_record/<hive_id>")
def inspection_record(hive_id):
    hive = mongo.db.hives.find_one({"_id": ObjectId(hive_id)})
    inspections = list(mongo.db.hiveInspections.find(
            {"hiveID": ObjectId(hive_id)}).sort("inspectionDate", 1))
    return render_template("inspection_record.html",
                           hive=hive, inspections=inspections)


@app.route("/manage_inspection/<inspection_id>", methods=["GET", "POST"])
def manage_inspection(inspection_id):
    inspection = mongo.db.hiveInspections.find_one(
        {"_id": ObjectId(inspection_id)})
    hive = mongo.db.hives.find_one({"_id": ObjectId(inspection["hiveID"])})
    return render_template("manage_inspection.html",
                           inspection=inspection, hive=hive)


@app.route('/delete_inspection/<inspection_id>')
def delete_inspection(inspection_id):
    try:
        mongo.db.hiveInspections.delete_one({"_id": ObjectId(inspection_id)})
        flash("Inspection Successfully Deleted")
    except Exception as e:
        flash("Error ocurred. Inspection not deleted. Please try again")
        mongo.db.exceptionLog.insert_one(
                {"datetime": datetime.datetime.now(),
                 "action": "Delete inspection record",
                 "exception": e})
    return redirect(url_for("hive_management", apiary='all'))


# MAIN - RUNNING IN DEBUG MODE
if __name__ == "__main__":
    app.run(host=os.environ.get("IP"),
            port=int(os.environ.get("PORT")),
            debug=True)
