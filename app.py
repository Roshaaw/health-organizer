from flask import Flask, render_template, request, redirect, url_for, session
from werkzeug.security import generate_password_hash, check_password_hash
from pymongo import MongoClient
from bson.objectid import ObjectId
import os
import re
from dotenv import load_dotenv

load_dotenv(override=True)

app = Flask(__name__)
app.secret_key = "dev-secret-key-change-later"

MONGO_URI = os.getenv("MONGO_URI")
DB_NAME = os.getenv("DB_NAME", "health_organizer")


client = MongoClient(MONGO_URI) if MONGO_URI else None
db = client[DB_NAME] if client is not None else None
medications_collection = db["medications"] if db is not None else None
symptoms_collection = db["symptoms"] if db is not None else None
appointments_collection = db["appointments"] if db is not None else None

def get_current_user():
    # If user is not logged in, there is no current user
    if "user_id" not in session:
        return None

    # Find logged-in user by their MongoDB _id
    return db["users"].find_one({"_id": ObjectId(session["user_id"])})


@app.route("/")
def index():
    user = get_current_user()

    if not user:
        return redirect(url_for("login"))

    user_id = str(user["_id"])

    medications = []
    if medications_collection is not None:
        medications = list(medications_collection.find({"user_id": user_id}))

    symptoms = []
    if symptoms_collection is not None:
        symptoms = list(symptoms_collection.find({"user_id": user_id}))

    appointments = []
    if appointments_collection is not None:
        appointments = list(appointments_collection.find({"user_id": user_id}))

    return render_template(
        "index.html",
        medications=medications,
        symptoms=symptoms,
        appointments=appointments,
        user=user
    )


@app.route("/signup", methods=["GET", "POST"])
def signup():
    if db is None:
        return "Database not connected", 500

    if request.method == "POST":
        first_name = request.form.get("first_name", "").strip()
        last_name = request.form.get("last_name", "").strip()
        email = request.form.get("email", "").strip().lower()
        password = request.form.get("password", "").strip()

        if not first_name or not last_name or not email or not password:
            return "All fields are required.", 400

        email_pattern = r"^[\w\.-]+@[\w\.-]+\.\w+$"
        if not re.match(email_pattern, email):
            return "Please enter a valid email address.", 400

        existing_user = db["users"].find_one({"email": email})
        if existing_user:
            return "An account with this email already exists.", 400

        new_user = db["users"].insert_one({
            "first_name": first_name,
            "last_name": last_name,
            "email": email,
            "password": generate_password_hash(password),
            "phone": "",
            "birthday": "",
            "height": "",
            "weight": "",
            "blood_type": "",
            "allergies": "",
            "primary_doctor": "",
            "emergency_contact": ""
        })

        session["user_id"] = str(new_user.inserted_id)
        session["user_name"] = first_name

        return redirect(url_for("profile"))
    

    return render_template("signup.html")


@app.route("/login", methods=["GET", "POST"])
def login():
    if db is None:
        return "Database not connected", 500

    if request.method == "POST":
        email = request.form.get("email", "").strip().lower()
        password = request.form.get("password", "").strip()

        user = db["users"].find_one({"email": email})

        if not user or not check_password_hash(user.get("password", ""), password):
            return "Invalid email or password.", 400

        session["user_id"] = str(user["_id"])
        session["user_name"] = user.get("first_name", "")

        return redirect(url_for("profile"))

    return render_template("login.html")


@app.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("login"))


@app.route("/profile")
def profile():
    if db is None:
        return "Database not connected", 500

    user = get_current_user()

    # If not logged in, send user to login page
    if not user:
        return redirect(url_for("login"))

    success = request.args.get("success") == "true"

    return render_template("profile.html", user=user, success=success)


@app.route("/profile/update", methods=["POST"])
def update_profile():
    if db is None:
        return "Database not connected", 500

    first_name = request.form.get("first_name", "").strip()
    last_name = request.form.get("last_name", "").strip()
    email = request.form.get("email", "").strip()
    phone = request.form.get("phone", "").strip()
    birthday = request.form.get("birthday", "").strip()

    # Required fields
    if not first_name or not last_name or not email:
        return "First name, last name, and email are required.", 400

    # Email format check
    email_pattern = r"^[\w\.-]+@[\w\.-]+\.\w+$"
    if not re.match(email_pattern, email):
        return "Please enter a valid email address.", 400

    # Phone format check: allows 1234567890, 123-456-7890, (123) 456-7890
    phone_pattern = r"^$|^\(?\d{3}\)?[-.\s]?\d{3}[-.\s]?\d{4}$"
    if not re.match(phone_pattern, phone):
        return "Please enter a valid phone number.", 400

    # Birthday format check: HTML date input sends YYYY-MM-DD
    date_pattern = r"^$|^\d{4}-\d{2}-\d{2}$"
    if not re.match(date_pattern, birthday):
        return "Please enter a valid birthday.", 400

    user = get_current_user()

    if not user:
        return "User not found", 404

    db["users"].update_one(
        {"_id": user["_id"]},
        {"$set": {
            "first_name": first_name,
            "last_name": last_name,
            "email": email,
            "phone": phone,
            "birthday": birthday,
            "height": request.form.get("height", "").strip(),
            "weight": request.form.get("weight", "").strip(),
            "blood_type": request.form.get("blood_type", "").strip(),
            "allergies": request.form.get("allergies", "").strip(),
            "primary_doctor": request.form.get("primary_doctor", "").strip(),
            "emergency_contact": request.form.get("emergency_contact", "").strip(),
        }}
    )

    return redirect(url_for("profile", success="true"))

@app.route("/add_medication", methods=["POST"])
def add_medication():
    user = get_current_user()

    if not user:
        return redirect(url_for("login"))

    if medications_collection is None:
        return "Database not connected. Check your .env file.", 500

    name = request.form.get("name", "").strip()
    dosage = request.form.get("dosage", "").strip()
    times_per_day = request.form.get("times_per_day", "1").strip()
    days_of_week = request.form.getlist("days_of_week")
    medication_times = [t for t in request.form.getlist("medication_times") if t]

    if name and dosage and times_per_day and medication_times:
        medications_collection.insert_one({
            "user_id": str(user["_id"]),
            "name": name,
            "dosage": dosage,
            "times_per_day": times_per_day,
            "days_of_week": days_of_week,
            "medication_times": medication_times
        })

    return redirect(url_for("index"))

@app.route("/edit_medication", methods=["POST"])
def edit_medication():
    user = get_current_user()

    if not user:
        return redirect(url_for("login"))

    if medications_collection is None:
        return "Database not connected.", 500

    med_id = request.form.get("id", "").strip()
    medication_times = [t for t in request.form.getlist("medication_times") if t]
    days_of_week = request.form.getlist("days_of_week")

    medications_collection.update_one(
        {
            "_id": ObjectId(med_id),
            "user_id": str(user["_id"])
        },
        {"$set": {
            "name": request.form.get("name", "").strip(),
            "dosage": request.form.get("dosage", "").strip(),
            "times_per_day": request.form.get("times_per_day", "1").strip(),
            "days_of_week": days_of_week,
            "medication_times": medication_times
        
        }}
    )

    return redirect(url_for("index"))


@app.route("/delete_medication/<med_id>", methods=["POST"])
def delete_medication(med_id):
    user = get_current_user()

    if not user:
        return redirect(url_for("login"))

    if medications_collection is None:
        return "Database not connected.", 500

    medications_collection.delete_one({
        "_id": ObjectId(med_id),
        "user_id": str(user["_id"])
    })

    return redirect(url_for("index"))


@app.route("/add_symptom", methods=["POST"])
def add_symptom():
    user = get_current_user()

    if not user:
        return redirect(url_for("login"))

    if symptoms_collection is None:
        return "Database not connected", 500

    name = request.form.get("name", "").strip()
    severity = request.form.get("severity", "").strip()
    date = request.form.get("date", "").strip()
    notes = request.form.get("notes", "").strip()

    if name and severity and date:
        symptoms_collection.insert_one({
            "user_id": str(user["_id"]),
            "name": name,
            "severity": severity,
            "date": date,
            "notes": notes
        })

    return redirect(url_for("index"))


@app.route("/edit_symptom", methods=["POST"])
def edit_symptom():
    user = get_current_user()

    if not user:
        return redirect(url_for("login"))

    if symptoms_collection is None:
        return "Database not connected", 500

    symptom_id = request.form.get("id", "").strip()

    symptoms_collection.update_one(
        {
            "_id": ObjectId(symptom_id),
            "user_id": str(user["_id"])
        },
        {"$set": {
            "name": request.form.get("name", "").strip(),
            "severity": request.form.get("severity", "").strip(),
            "date": request.form.get("date", "").strip(),
            "notes": request.form.get("notes", "").strip()
        }}
    )

    return redirect(url_for("index"))


@app.route("/add_appointment", methods=["POST"])
def add_appointment():
    user = get_current_user()

    if not user:
        return redirect(url_for("login"))

    if appointments_collection is None:
        return "Database not connected", 500

    doctor = request.form.get("doctor", "").strip()
    doctor_type = request.form.get("doctor_type", "").strip()
    custom_specialty = request.form.get("custom_specialty", "").strip()
    date = request.form.get("date", "").strip()
    time = request.form.get("time", "").strip()
    reason = request.form.get("reason", "").strip()
    notes = request.form.get("notes", "").strip()
    status = request.form.get("status", "").strip() or "Scheduled"

    if doctor_type == "Other Specialty" and custom_specialty:
        doctor_type = custom_specialty

    if doctor and doctor_type and date and time and reason:
        appointments_collection.insert_one({
            "user_id": str(user["_id"]),
            "doctor": doctor,
            "doctor_type": doctor_type,
            "date": date,
            "time": time,
            "reason": reason,
            "notes": notes,
            "status": status
        })

    return redirect(url_for("index"))

@app.route("/edit_appointment", methods=["POST"])
def edit_appointment():
    user = get_current_user()

    if not user:
        return redirect(url_for("login"))

    if appointments_collection is None:
        return "Database not connected", 500

    appointment_id = request.form.get("id", "").strip()
    doctor_type = request.form.get("doctor_type", "").strip()
    custom_specialty = request.form.get("custom_specialty", "").strip()

    if doctor_type == "Other Specialty" and custom_specialty:
        doctor_type = custom_specialty

    appointments_collection.update_one(
        {
            "_id": ObjectId(appointment_id),
            "user_id": str(user["_id"])
        },
        {"$set": {
            "doctor": request.form.get("doctor", "").strip(),
            "doctor_type": doctor_type,
            "date": request.form.get("date", "").strip(),
            "time": request.form.get("time", "").strip(),
            "reason": request.form.get("reason", "").strip(),
            "notes": request.form.get("notes", "").strip(),
            "status": request.form.get("status", "").strip()
        }}
    )

    return redirect(url_for("index"))


if __name__ == "__main__":
    app.run(debug=True, use_reloader=False)
