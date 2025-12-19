from flask import Blueprint, render_template, request, session, redirect
from config import supabase

dashboard_bp = Blueprint("dashboard", __name__)

@dashboard_bp.route("/patient/dashboard")
def patient_dashboard():
    if session.get("role") != "patient":
        return redirect("/patient")

    return render_template(
        "patient_dashboard.html",
        phone=session.get("phone")
    )

@dashboard_bp.route("/patient/create-profile", methods=["GET", "POST"])
def create_profile():
    if session.get("role") != "patient":
        return redirect("/patient")

    if request.method == "POST":
        supabase.table("patient_profiles").upsert({
            "user_id": session["user_id"],
            "email": request.form["email"],
            "blood_group": request.form["blood_group"],
            "city": request.form["city"],
            "state": request.form["state"],
            "completed": True
        }).execute()

        return redirect("/patient/dashboard")

    return render_template("patient_create_profile.html")

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

    return render_template("doctor_create_profile.html")

@dashboard_bp.route("/doctor/dashboard")
def doctor_dashboard():
    if session.get("role") != "doctor":
        return redirect("/doctor")

    return render_template("doctor_dashboard.html")


@dashboard_bp.route("/doctor/pending-verification")
def doctor_pending():
    return render_template("doctor_pending.html")


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

    return render_template("hospital_create_profile.html")

@dashboard_bp.route("/hospital/dashboard")
def hospital_dashboard():
    if session.get("role") != "hospital":
        return redirect("/hospital")

    return render_template("hospital_dashboard.html")

@dashboard_bp.route("/hospital/pending-verification")
def hospital_pending():
    return render_template("hospital_pending.html")
