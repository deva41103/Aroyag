from datetime import datetime
import random
from flask import Blueprint, render_template, request, session, redirect
from config import supabase
from function.qr_generator import upload_patient_qr
from function.storage import get_signed_url, upload_to_supabase

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
        .select("*")
        .eq("user_id", session["user_id"])
        .single()
        .execute()
    )

    if not profile.data:
        return redirect("/patient/create-profile")

    data = profile.data

    # 🔐 Generate signed URLs (temporary)
    data["aadhaar_signed_url"] = get_signed_url(
        "patient-documents",
        data.get("aadhaar_file_path")
    )

    data["insurance_signed_url"] = get_signed_url(
        "patient-documents",
        data.get("insurance_file_path")
    )

    return render_template(
        "patient/patient_dashboard.html",
        profile=data
    )


@dashboard_bp.route("/patient/create-profile", methods=["GET", "POST"])
def patient_create_profile():
    if session.get("role") != "patient" or not session.get("user_id"):
        return redirect("/patient")

    user_id = session["user_id"]

    # -------------------------------------------------
    # 1️⃣ Fetch existing profile (OLD LOGIC PRESERVED)
    # -------------------------------------------------
    existing = (
        supabase
        .table("patient_profiles")
        .select("health_id, qr_url, current_step")
        .eq("user_id", user_id)
        .execute()
    )

    if existing.data:
        health_id = existing.data[0]["health_id"]
        qr_url = existing.data[0]["qr_url"]
        current_step = existing.data[0].get("current_step", 0) or 0
    else:
        # 🔥 EXACT OLD BEHAVIOR
        health_id = f"HL-{datetime.now().year}-{random.randint(100000, 999999)}"
        qr_url = upload_patient_qr(user_id)
        current_step = 0

    # -------------------------------------------------
    # 2️⃣ Handle POST (NEW FORM + OLD CORE)
    # -------------------------------------------------
    if request.method == "POST":
        is_final = request.form.get("is_final") == "true"

        aadhaar_path = upload_to_supabase(
            "patient-documents",
            request.files.get("aadhaar_file"),
            user_id,
            "aadhaar"
        )

        insurance_path = upload_to_supabase(
            "patient-documents",
            request.files.get("insurance_file"),
            user_id,
            "insurance"
        )

        supabase.table("patient_profiles").upsert({
            "user_id": user_id,

            # 🔒 CORE IDENTITY (DO NOT CHANGE)
            "health_id": health_id,
            "qr_url": qr_url,

            # 🧍 Personal info
            "full_name": request.form.get("full_name"),
            "email": request.form.get("email"),
            "dob": request.form.get("dob"),
            "gender": request.form.get("gender"),
            "blood_group": request.form.get("blood_group"),  # ✅ FIXED
            "state": request.form.get("state"),
            "city": request.form.get("city"),
            "pincode": request.form.get("pincode"),

            # 📄 Documents
            "aadhaar_number": request.form.get("aadhaar_number"),
            "aadhaar_file_path": aadhaar_path,
            "insurance_file_path": insurance_path,

            # 🩺 Medical info
            "allergies": request.form.get("allergies"),
            "medical_conditions": request.form.get("medical_conditions"),
            "disabilities": request.form.get("disabilities"),

            # 🚨 Emergency
            "emergency_contact": {
                "name": request.form.get("emergency_name"),
                "relation": request.form.get("emergency_relation"),
                "phone": request.form.get("emergency_phone")
            },

            # 🧭 Stepper state
            "completed": is_final,
            "current_step": int(request.form.get("current_step", 0))
        }).execute()

        return redirect("/patient/dashboard" if is_final else "/patient/create-profile")

    # -------------------------------------------------
    # 3️⃣ Render form (resume support)
    # -------------------------------------------------
    return render_template(
        "patient/patient_create_profile.html",
        current_step=current_step
    )


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
