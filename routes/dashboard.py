from datetime import datetime
import random
from flask import Blueprint, render_template, request, session, redirect
from config import supabase
from function.qr_generator import upload_patient_qr

# -------------------------------
# Dashboard Blueprint
# -------------------------------
dashboard_bp = Blueprint(
    "dashboard",
    __name__,
    template_folder="templates"
)

# =========================
# PATIENT DASHBOARD
# =========================

@dashboard_bp.route("/patient/dashboard", methods=["GET"])
def patient_dashboard():
    if session.get("role") != "patient" or not session.get("user_id"):
        return redirect("/patient")

    profile = (
        supabase
        .table("patient_profiles")
        .select("health_id, email, blood_group, city, state, qr_url")
        .eq("user_id", session["user_id"])
        .execute()
    )

    if not profile.data:
        return redirect("/patient/create-profile")

    return render_template(
        "patient/patient_dashboard.html",
        profile=profile.data[0]
    )


@dashboard_bp.route("/patient/create-profile", methods=["GET", "POST"])
def patient_create_profile():
    if session.get("role") != "patient" or not session.get("user_id"):
        return redirect("/patient")

    user_id = session["user_id"]

    existing = (
        supabase
        .table("patient_profiles")
        .select("health_id, qr_url")
        .eq("user_id", user_id)
        .execute()
    )

    if existing.data:
        health_id = existing.data[0]["health_id"]
        qr_url = existing.data[0]["qr_url"]
    else:
        health_id = f"HL-{datetime.now().year}-{random.randint(100000, 999999)}"
        qr_url = upload_patient_qr(user_id)

    if request.method == "POST":
        supabase.table("patient_profiles").upsert({
            "user_id": user_id,
            "email": request.form.get("email"),
            "blood_group": request.form.get("blood_group"),
            "city": request.form.get("city"),
            "state": request.form.get("state"),
            "completed": True,
            "health_id": health_id,
            "qr_url": qr_url
        }).execute()

        return redirect("/patient/dashboard")

    return render_template("patient/patient_create_profile.html")


# =====================================================
# DOCTOR PROFILE & DASHBOARD
# =====================================================

@dashboard_bp.route("/doctor/create-profile", methods=["GET", "POST"])
def doctor_create_profile():
    if session.get("role") != "doctor" or not session.get("user_id"):
        return redirect("/doctor")

    hospitals = (
        supabase
        .table("hospitals")
        .select("id, name")
        .order("name")
        .execute()
    )

    if request.method == "POST":
        supabase.table("doctor_profiles").upsert({
            "user_id": session["user_id"],
            "full_name": request.form.get("full_name"),
            "email": request.form.get("email"),
            "license_number": request.form.get("license"),
            "specialization": request.form.get("specialization"),
            "hospital_id": request.form.get("hospital_id"),
            "verified": False
        }).execute()

        return redirect("/doctor/pending-verification")

    return render_template(
        "doctor/doctor_create_profile.html",
        hospitals=hospitals.data
    )


@dashboard_bp.route("/doctor/dashboard", methods=["GET"])
def doctor_dashboard():
    if session.get("role") != "doctor" or not session.get("user_id"):
        return redirect("/doctor")

    doctor_profile = (
        supabase
        .table("doctor_profiles")
        .select("hospital_id")
        .eq("user_id", session["user_id"])
        .execute()
    )

    if not doctor_profile.data:
        return redirect("/doctor/create-profile")

    hospital_id = doctor_profile.data[0]["hospital_id"]

    doctors = (
        supabase
        .table("doctor_profiles")
        .select("full_name, specialization")
        .eq("hospital_id", hospital_id)
        .execute()
    )

    return render_template(
        "doctor/doctor_dashboard.html",
        doctors=doctors.data
    )


@dashboard_bp.route("/doctor/pending-verification", methods=["GET"])
def doctor_pending():
    return render_template("doctor/doctor_pending.html")


# =====================================================
# HOSPITAL PROFILE & DASHBOARD
# =====================================================

@dashboard_bp.route("/hospital/create-profile", methods=["GET", "POST"])
def hospital_create_profile():
    if session.get("role") != "hospital" or not session.get("user_id"):
        return redirect("/hospital")

    hospitals = (
        supabase
        .table("hospitals")
        .select("id, name")
        .order("name")
        .execute()
    )

    if request.method == "POST":
        supabase.table("hospital_profiles").upsert({
            "user_id": session["user_id"],
            "hospital_id": request.form.get("hospital_id"),
            "registration_number": request.form.get("registration"),
            "verified": False
        }).execute()

        return redirect("/hospital/pending-verification")

    return render_template(
        "hospital/hospital_create_profile.html",
        hospitals=hospitals.data
    )


@dashboard_bp.route("/hospital/dashboard", methods=["GET"])
def hospital_dashboard():
    if session.get("role") != "hospital" or not session.get("user_id"):
        return redirect("/hospital")

    hospital_profile = (
        supabase
        .table("hospital_profiles")
        .select("hospital_id")
        .eq("user_id", session["user_id"])
        .execute()
    )

    if not hospital_profile.data:
        return redirect("/hospital/create-profile")

    hospital_id = hospital_profile.data[0]["hospital_id"]

    doctors = (
        supabase
        .table("doctor_profiles")
        .select("full_name, specialization, verified")
        .eq("hospital_id", hospital_id)
        .execute()
    )

    newborns = (
        supabase
        .table("newborns")
        .select("baby_name, dob, gender, health_id, created_at")
        .eq("hospital_id", hospital_id)
        .order("created_at", desc=True)
        .execute()
    )

    return render_template(
        "hospital/hospital_dashboard.html",
        doctors=doctors.data,
        newborns=newborns.data
    )


@dashboard_bp.route("/hospital/pending-verification", methods=["GET"])
def hospital_pending():
    return render_template("hospital/hospital_pending.html")
