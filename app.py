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
        ''' Set session variables for current user '''
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
@app.errorhandler(400)  # Bad Request
@app.errorhandler(401)  # Unauthorized
@app.errorhandler(404)  # Not Found
@app.errorhandler(500)  # Internal Server Error
@app.errorhandler(502)  # Bad Gateway
def page_not_found(error):
    ''' Handle HTTP status codes/errors most relevant to application '''
    return render_template('error.html', error=error)


# APPLICATION ENDPOINTS

@app.route("/placeholder")
def placeholder():
    ''' Placeholder application endpoint to be used where 
        functionality not yet developed 
    '''
    return render_template("placeholder.html")


@app.route("/")
@app.route("/home")
def home():
    ''' Display Web Application Home Page '''
    return render_template("home.html")


@app.route("/learn_about_bees")
def learn_about_bees():
    ''' Display Learn About Bees Page '''
    return render_template("learn_about_bees.html")


@app.route("/about")
def about():
    ''' Display About Honey Bee Page '''
    return render_template("about.html")


@app.route("/signin", methods=["GET", "POST"])
def signin():
    ''' Sign in page for registered user '''
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
    ''' Sign out page for signed in user '''
    # remove user from session cookies
    flash("You have been logged out")
    session.pop("user")
    session["beekeeper"] = False
    session["admin"] = False
    return redirect(url_for("home"))


@app.route("/register", methods=["GET", "POST"])
def register():
    ''' Registration page for new site users '''
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
    ''' View table of all apiaries for current beekeeper '''
    apiaries = list(mongo.db.apiaries.find(
            {"beekeeper": session["user"]}
        ).sort("colony", 1))
    return render_template("apiary_management.html", apiaries=apiaries)


@app.route("/add_apiary", methods=["GET", "POST"])
def add_apiary():
    ''' Add new apiary for current beekeeper '''
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
    ''' View / edit selected apiary '''
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
    ''' Delete selected apiary from database 
        Current version - record immediately deleted from database.
    '''
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
    ''' View table of all hives for current beekeeper in specified apiary.
        Current version - always shows all hives, ordered by apiary name.
    '''
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
    ''' Add new hive for current beekeeper '''
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
    ''' View or Update individual hive record. '''
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
    ''' Delete record for specified hive.
        Current version - record immediately deleted from database.
    '''
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
    ''' Create new inspection record for selected hive '''
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
                "healthCB": request.form.get("healthCB") == 'on',
                "healthEFB": request.form.get("healthEFB") == 'on',
                "healthAFB": request.form.get("healthAFB") == 'on',
                "healthCBPV": request.form.get("healthCBPV") == 'on',
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
    ''' View table of inspections for specified hive '''
    hive = mongo.db.hives.find_one({"_id": ObjectId(hive_id)})
    inspections = list(mongo.db.hiveInspections.find(
            {"hiveID": ObjectId(hive_id)}).sort("inspectionDate", 1))
    return render_template("inspection_record.html",
                           hive=hive, inspections=inspections)


@app.route("/manage_inspection/<inspection_id>", methods=["GET", "POST"])
def manage_inspection(inspection_id):
    ''' View (GET) or edit (POST) single hive inspection record '''
    if request.method == "POST":
        # Update record according to form data
        try:
            edit_date = datetime.datetime.now()
            # update database record
            mongo.db.hiveInspections.update_one(
                {"_id": ObjectId(inspection_id)},
                {"$set": {
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
                    "healthCB": request.form.get("healthCB") == 'on',
                    "healthEFB": request.form.get("healthEFB") == 'on',
                    "healthAFB": request.form.get("healthAFB") == 'on',
                    "healthCBPV": request.form.get("healthCBPV") == 'on',
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
                    "last_updated": edit_date.strftime("%d %B %Y")
                }})
            # add current datetime to update history
            mongo.db.hiveInspections.update_one(
                {"_id": ObjectId(inspection_id)},
                {"$addToSet": {
                    "update_history":
                        {"date": edit_date,
                            "action": "Content edited"}
                }})
            flash("Inspection Record Successfully Updated")
        except Exception as e:
            flash("Error ocurred. Record not updated. Please try again")
            mongo.db.exceptionLog.insert_one(
                {"datetime": datetime.datetime.now(),
                 "action": "Update Inspection Record",
                 "exception": e})

    # View inspection record for hive
    inspection = mongo.db.hiveInspections.find_one(
        {"_id": ObjectId(inspection_id)})
    # get hive_id associated with this inspection
    hive = mongo.db.hives.find_one({"_id": ObjectId(inspection["hiveID"])})
    if request == "POST":
        # review updated record
        return redirect(url_for('inspection_record', hive_id=hive._id))
    else:
        # view inspection
        return render_template("manage_inspection.html",
                               inspection=inspection, hive=hive)


@app.route('/delete_inspection/<inspection_id>')
def delete_inspection(inspection_id):
    ''' Delete specified hive inspection record
        Current version - inspection immediately deleted from database.
    '''
    try:
        mongo.db.hiveInspections.delete_one({"_id": ObjectId(inspection_id)})
        flash("Inspection Successfully Deleted")
    except Exception as e:
        flash("Error ocurred. Inspection not deleted. Please try again")
        mongo.db.exceptionLog.insert_one(
                {"datetime": datetime.datetime.now(),
                 "action": "Delete inspection record",
                 "exception": e})
    # return to list of hive inspections for current hive
    return redirect(url_for("hive_management", apiary='all'))


# MAIN - RUNNING IN DEBUG MODE
if __name__ == "__main__":
    app.run(host=os.environ.get("IP"),
            port=int(os.environ.get("PORT")),
            debug=True)
