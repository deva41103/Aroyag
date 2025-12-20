from datetime import datetime
import random
from flask import Blueprint, render_template, request, session, redirect
from config import supabase

dashboard_bp = Blueprint("dashboard", __name__)

@dashboard_bp.route("/patient/dashboard")
def patient_dashboard():
    if session.get("role") != "patient":
        return redirect("/patient")

    profile = (
        supabase
        .table("patient_profiles")
        .select("health_id, email, blood_group, city, state")
        .eq("user_id", session["user_id"])
        .single()
        .execute()
    )
    
    return render_template(
        "patient/patient_dashboard.html",
        profile=profile.data
    )

@dashboard_bp.route("/patient/create-profile", methods=["GET", "POST"])
def create_profile():
    if session.get("role") != "patient":
        return redirect("/patient")

    user_id = session["user_id"]

    # Fetch existing profile (if any)
    existing = (
        supabase
        .table("patient_profiles")
        .select("health_id")
        .eq("user_id", user_id)
        .execute()
    )

    # Generate Health ID ONLY if not present
    if not existing.data or not existing.data[0]["health_id"]:
        health_id = f"HL-{datetime.now().year}-{random.randint(100000, 999999)}"
    else:
        health_id = existing.data[0]["health_id"]

    if request.method == "POST":
        supabase.table("patient_profiles").upsert({
            "user_id": user_id,
            "email": request.form["email"],
            "blood_group": request.form["blood_group"],
            "city": request.form["city"],
            "state": request.form["state"],
            "completed": True,
            "health_id": health_id
        }).execute()

        return redirect("/patient/dashboard")

    return render_template("patient/patient_create_profile.html")

@dashboard_bp.route("/doctor/create-profile", methods=["GET", "POST"])
def doctor_create_profile():
    if session.get("role") != "doctor":
        return redirect("/doctor")

    if request.method == "POST":
        supabase.table("doctor_profiles").upsert({
            "user_id": session["user_id"],
            "full_name": request.form["full_name"],
            "email": request.form["email"],
            "license_number": request.form["license"],
            "specialization": request.form["specialization"],
            "hospital": request.form["hospital"],
            "verified": False
        }).execute()

        return redirect("/doctor/pending-verification")

    return render_template("doctor/doctor_create_profile.html")

@dashboard_bp.route("/doctor/dashboard")
def doctor_dashboard():
    if session.get("role") != "doctor":
        return redirect("/doctor")

    return render_template("doctor/doctor_dashboard.html")


@dashboard_bp.route("/doctor/pending-verification")
def doctor_pending():
    return render_template("doctor/doctor_pending.html")


@dashboard_bp.route("/hospital/create-profile", methods=["GET", "POST"])
def hospital_create_profile():
    if session.get("role") != "hospital":
        return redirect("/hospital")

    if request.method == "POST":
        supabase.table("hospital_profiles").upsert({
            "user_id": session["user_id"],
            "hospital_name": request.form["hospital_name"],
            "registration_number": request.form["registration"],
            "city": request.form["city"],
            "state": request.form["state"],
            "verified": False
        }).execute()

        return redirect("/hospital/pending-verification")

    return render_template("hospital/hospital_create_profile.html")

@dashboard_bp.route("/hospital/dashboard")
def hospital_dashboard():
    if session.get("role") != "hospital":
        return redirect("/hospital")

    return render_template("hospital/hospital_dashboard.html")

@dashboard_bp.route("/hospital/pending-verification")
def hospital_pending():
    return render_template("hospital/hospital_pending.html")
