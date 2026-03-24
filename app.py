from flask import Flask, render_template, request, redirect, url_for
from pymongo import MongoClient
from bson.objectid import ObjectId
import os
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)

MONGO_URI = os.getenv("MONGO_URI", "")
DB_NAME = os.getenv("DB_NAME", "health_organizer")

client = MongoClient(MONGO_URI) if MONGO_URI else None
db = client[DB_NAME] if client is not None else None
medications_collection = db["medications"] if db is not None else None
symptoms_collection = db["symptoms"] if db is not None else None

# Temporary in-memory backend data for now
symptoms_data = [
    {
        "id": 1,
        "name": "Headache",
        "severity": "Mild",
        "date": "2026-03-22",
        "notes": "Started in the afternoon"
    },
    {
        "id": 2,
        "name": "Fatigue",
        "severity": "Moderate",
        "date": "2026-03-23",
        "notes": "Low energy throughout day"
    }
]

appointments_data = [
    {
        "id": 1,
        "doctor": "Dr. Sarah Smith",
        "doctor_type": "Primary Care",
        "date": "2026-03-30",
        "reason": "Annual Physical",
        "notes": "",
        "status": "Scheduled"
    },
    {
        "id": 2,
        "doctor": "Dr. Kevin Lee",
        "doctor_type": "Optometry / Ophthalmology",
        "date": "2026-04-05",
        "reason": "Vision Exam",
        "notes": "",
        "status": "Scheduled"
    },
    {
        "id": 3,
        "doctor": "Dr. Maria Lopez",
        "doctor_type": "Dentistry",
        "date": "2026-04-18",
        "reason": "Cleaning",
        "notes": "",
        "status": "Completed"
    }
]


@app.route("/")
def index():
    medications = []
    if medications_collection is not None:
        medications = list(medications_collection.find())
    
    symptoms = []
    if symptoms_collection is not None:
        symptoms = list(symptoms_collection.find())

    return render_template(
        "index.html",
        medications=medications,
        symptoms=symptoms,
        appointments=appointments_data
    )


@app.route("/login")
def login():
    return render_template("login.html")


@app.route("/signup")
def signup():
    return render_template("signup.html")


@app.route("/profile")
def profile():
    user_profile = {
        "full_name": "Roshan Karimi",
        "email": "roshan@example.com",
        "phone": "(555) 123-4567",
        "birthday": "2004-06-15",
        "height": "5'10\"",
        "weight": "160 lbs",
        "blood_type": "O+",
        "allergies": "None listed",
        "primary_doctor": "Dr. Smith",
        "emergency_contact": "Mom - (555) 987-6543"
    }
    return render_template("profile.html", user=user_profile)


@app.route("/add_medication", methods=["POST"])
def add_medication():
    if medications_collection is None:
        return "Database not connected. Check your .env file.", 500

    name = request.form.get("name", "").strip()
    dosage = request.form.get("dosage", "").strip()
    frequency = request.form.get("frequency", "").strip()

    if name and dosage and frequency:
        medications_collection.insert_one({
            "name": name,
            "dosage": dosage,
            "frequency": frequency
        })

    return redirect(url_for("index"))


@app.route("/delete_medication/<med_id>", methods=["POST"])
def delete_medication(med_id):
    if medications_collection is None:
        return "Database not connected. Check your .env file.", 500

    medications_collection.delete_one({"_id": ObjectId(med_id)})
    return redirect(url_for("index"))


@app.route("/add_symptom", methods=["POST"])
def add_symptom():
    if symptoms_collection is None:
        return "Database not connected", 500

    name = request.form.get("name", "").strip()
    severity = request.form.get("severity", "").strip()
    date = request.form.get("date", "").strip()
    notes = request.form.get("notes", "").strip()

    if name and severity and date:
        symptoms_collection.insert_one({
            "name": name,
            "severity": severity,
            "date": date,
            "notes": notes
        })

    return redirect(url_for("index"))


@app.route("/edit_symptom", methods=["POST"])
def edit_symptom():
    if symptoms_collection is None:
        return "Database not connected", 500

    symptom_id = request.form.get("id", "").strip()
    name = request.form.get("name", "").strip()
    severity = request.form.get("severity", "").strip()
    date = request.form.get("date", "").strip()
    notes = request.form.get("notes", "").strip()

    if symptom_id:
        symptoms_collection.update_one(
            {"_id": ObjectId(symptom_id)},
            {"$set": {
                "name": name,
                "severity": severity,
                "date": date,
                "notes": notes
            }}
        )

    return redirect(url_for("index"))


@app.route("/add_appointment", methods=["POST"])
def add_appointment():
    doctor = request.form.get("doctor", "").strip()
    doctor_type = request.form.get("doctor_type", "").strip()
    custom_specialty = request.form.get("custom_specialty", "").strip()
    date = request.form.get("date", "").strip()
    reason = request.form.get("reason", "").strip()
    notes = request.form.get("notes", "").strip()
    status = request.form.get("status", "").strip() or "Scheduled"

    if doctor_type == "Other Specialty" and custom_specialty:
        doctor_type = custom_specialty

    if doctor and doctor_type and date and reason:
        next_id = max([a["id"] for a in appointments_data], default=0) + 1
        appointments_data.append({
            "id": next_id,
            "doctor": doctor,
            "doctor_type": doctor_type,
            "date": date,
            "reason": reason,
            "notes": notes,
            "status": status
        })

    return redirect(url_for("index"))

@app.route("/edit_appointment", methods=["POST"])
def edit_appointment():
    appointment_id = request.form.get("id", "").strip()
    doctor = request.form.get("doctor", "").strip()
    doctor_type = request.form.get("doctor_type", "").strip()
    custom_specialty = request.form.get("custom_specialty", "").strip()
    date = request.form.get("date", "").strip()
    reason = request.form.get("reason", "").strip()
    notes = request.form.get("notes", "").strip()
    status = request.form.get("status", "").strip()

    if doctor_type == "Other Specialty" and custom_specialty:
        doctor_type = custom_specialty

    for appointment in appointments_data:
        if str(appointment["id"]) == appointment_id:
            appointment["doctor"] = doctor
            appointment["doctor_type"] = doctor_type
            appointment["date"] = date
            appointment["reason"] = reason
            appointment["notes"] = notes
            appointment["status"] = status
            break

    return redirect(url_for("index"))


if __name__ == "__main__":
    app.run(debug=True, use_reloader=False)
