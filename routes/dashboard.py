from datetime import datetime
import random
from flask import Blueprint, render_template, request, session, redirect
from config import supabase
from function.qr_generator import upload_patient_qr

dashboard_bp = Blueprint("dashboard", __name__)

# =========================
# PATIENT DASHBOARD
# =========================

@dashboard_bp.route("/patient/dashboard")
def patient_dashboard():
    if session.get("role") != "patient":
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
    if session.get("role") != "patient":
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
            "email": request.form["email"],
            "blood_group": request.form["blood_group"],
            "city": request.form["city"],
            "state": request.form["state"],
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
    if session.get("role") != "doctor":
        return redirect("/doctor")

    # 🔽 Fetch hospital master list
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
            "full_name": request.form["full_name"],
            "email": request.form["email"],
            "license_number": request.form["license"],
            "specialization": request.form["specialization"],
            "hospital_id": request.form["hospital_id"],
            "verified": False
        }).execute()

        return redirect("/doctor/pending-verification")

    return render_template(
        "doctor/doctor_create_profile.html",
        hospitals=hospitals.data
    )


@dashboard_bp.route("/doctor/dashboard")
def doctor_dashboard():
    if session.get("role") != "doctor":
        return redirect("/doctor")

    # Get doctor's hospital
    doctor = (
        supabase
        .table("doctor_profiles")
        .select("hospital_id")
        .eq("user_id", session["user_id"])
        .single()
        .execute()
    )

    hospital_id = doctor.data["hospital_id"]

    # Doctors from same hospital
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


@dashboard_bp.route("/doctor/pending-verification")
def doctor_pending():
    return render_template("doctor/doctor_pending.html")


# =====================================================
# HOSPITAL PROFILE & DASHBOARD
# =====================================================

@dashboard_bp.route("/hospital/create-profile", methods=["GET", "POST"])
def hospital_create_profile():
    if session.get("role") != "hospital":
        return redirect("/hospital")

    # 🔽 Select hospital from master list
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
            "hospital_id": request.form["hospital_id"],
            "registration_number": request.form["registration"],
            "verified": False
        }).execute()

        return redirect("/hospital/pending-verification")

    return render_template(
        "hospital/hospital_create_profile.html",
        hospitals=hospitals.data
    )


@dashboard_bp.route("/hospital/dashboard")
def hospital_dashboard():
    if session.get("role") != "hospital":
        return redirect("/hospital")

    # Get hospital_id of logged-in hospital staff
    hospital_profile = (
        supabase
        .table("hospital_profiles")
        .select("hospital_id")
        .eq("user_id", session["user_id"])
        .single()
        .execute()
    )

    hospital_id = hospital_profile.data["hospital_id"]

    # Fetch doctors of this hospital
    doctors = (
        supabase
        .table("doctor_profiles")
        .select("full_name, specialization, verified")
        .eq("hospital_id", hospital_id)
        .execute()
    )

    # Fetch newborns of this hospital
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



@dashboard_bp.route("/hospital/pending-verification")
def hospital_pending():
    return render_template("hospital/hospital_pending.html")
