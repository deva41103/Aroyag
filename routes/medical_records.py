from datetime import datetime, timedelta
import random
from flask import (
    Blueprint,
    render_template,
    request,
    session,
    redirect,
    flash
)
from config import supabase, twilio_client, TWILIO_PHONE
from function.send_otp import send_patient_otp

# -------------------------------
# Medical Records Blueprint
# -------------------------------
medical_bp = Blueprint(
    "medical",
    __name__,
    template_folder="templates"
)

# ------------------------------------------------
# SEARCH PATIENT BY HEALTH ID → SEND OTP
# ------------------------------------------------
@medical_bp.route("/doctor/search-patient", methods=["POST"])
def doctor_search_patient():
    if session.get("role") != "doctor" or not session.get("user_id"):
        return redirect("/doctor")

    health_id = request.form.get("health_id")

    if not health_id:
        flash("Health ID is required")
        return redirect("/doctor/dashboard")

    # 1️⃣ Find patient
    res = (
        supabase
        .table("patient_profiles")
        .select("user_id")
        .eq("health_id", health_id)
        .limit(1)
        .execute()
    )

    if not res.data:
        flash("Patient not found")
        return redirect("/doctor/dashboard")

    patient_id = res.data[0]["user_id"]

    # 2️⃣ Get patient phone
    phone_res = (
        supabase
        .table("users")
        .select("phone")
        .eq("id", patient_id)
        .limit(1)
        .execute()
    )

    if not phone_res.data or not phone_res.data[0].get("phone"):
        flash("Patient phone number not available")
        return redirect("/doctor/dashboard")

    patient_phone = phone_res.data[0]["phone"]

    # 3️⃣ Generate OTP
    otp = str(random.randint(100000, 999999))

    supabase.table("patient_access_otps").insert({
        "patient_id": patient_id,
        "doctor_id": session["user_id"],
        "otp": otp,
        "verified": False,
        "expires_at": (datetime.utcnow() + timedelta(minutes=5)).isoformat()
    }).execute()

    # 4️⃣ Send OTP via Twilio
    twilio_client.messages.create(
        body=f"Aroyagm: Your OTP for doctor access is {otp}. Valid for 5 minutes.",
        from_=TWILIO_PHONE,
        to=patient_phone
    )

    flash("OTP sent to patient")
    return redirect(f"/doctor/verify-otp/{patient_id}")


# -------------------------------
# VERIFY OTP
# -------------------------------
@medical_bp.route("/doctor/verify-otp/<patient_id>", methods=["GET", "POST"])
def verify_patient_otp(patient_id):
    if session.get("role") != "doctor" or not session.get("user_id"):
        return redirect("/doctor")

    if request.method == "POST":
        otp = request.form.get("otp")

        if not otp:
            flash("OTP is required")
            return redirect(request.url)

        res = (
            supabase
            .table("patient_access_otps")
            .select("id")
            .eq("patient_id", patient_id)
            .eq("doctor_id", session["user_id"])
            .eq("otp", otp)
            .eq("verified", False)
            .gt("expires_at", datetime.utcnow().isoformat())
            .execute()
        )

        if not res.data:
            flash("Invalid or expired OTP")
            return redirect(request.url)

        supabase.table("patient_access_otps") \
            .update({"verified": True}) \
            .eq("id", res.data[0]["id"]) \
            .execute()

        session["verified_patient"] = patient_id
        return redirect(f"/doctor/patient/{patient_id}")

    return render_template("doctor/verify_otp.html")


# ------------------------------------------------
# VIEW PATIENT MEDICAL RECORDS (OTP PROTECTED)
# ------------------------------------------------
@medical_bp.route("/doctor/patient/<patient_id>", methods=["GET"])
def doctor_view_patient_records(patient_id):
    if session.get("role") != "doctor" or not session.get("user_id"):
        return redirect("/doctor")

    # 🔐 OTP check
    if session.get("verified_patient") != patient_id:
        flash("Patient consent (OTP) required")
        return redirect("/doctor/dashboard")

    records = (
        supabase
        .table("medical_records")
        .select("*, medical_attachments(*)")
        .eq("patient_id", patient_id)
        .order("created_at", desc=True)
        .execute()
    )

    return render_template(
        "doctor/doctor_patient_records.html",
        records=records.data,
        patient_id=patient_id
    )


# ------------------------------------------------
# ADD MEDICAL RECORD (OTP PROTECTED)
# ------------------------------------------------
@medical_bp.route("/doctor/patient/<patient_id>/add", methods=["GET", "POST"])
def doctor_add_medical_record(patient_id):
    if session.get("role") != "doctor" or not session.get("user_id"):
        return redirect("/doctor")

    if session.get("verified_patient") != patient_id:
        flash("Patient consent (OTP) required")
        return redirect("/doctor/dashboard")

    if request.method == "POST":
        title = request.form.get("title")
        description = request.form.get("description")

        if not title:
            flash("Title is required")
            return redirect(request.url)

        record = (
            supabase
            .table("medical_records")
            .insert({
                "patient_id": patient_id,
                "doctor_id": session["user_id"],
                "title": title,
                "description": description
            })
            .execute()
        )

        record_id = record.data[0]["id"]

        files = request.files.getlist("attachments")
        for file in files:
            if file and file.filename:
                path = f"{record_id}/{file.filename}"

                supabase.storage.from_("medical-files").upload(
                    path,
                    file.read(),
                    {"content-type": file.content_type}
                )

                file_url = supabase.storage.from_("medical-files").get_public_url(path)

                supabase.table("medical_attachments").insert({
                    "medical_record_id": record_id,
                    "file_name": file.filename,
                    "file_type": file.content_type,
                    "file_url": file_url
                }).execute()

        flash("Medical record added successfully")
        return redirect(f"/doctor/patient/{patient_id}")

    return render_template(
        "doctor/doctor_add_record.html",
        patient_id=patient_id
    )


# ------------------------------------------------
# QR SCAN
# ------------------------------------------------
@medical_bp.route("/doctor/scan", methods=["GET"])
def doctor_scan():
    if session.get("role") != "doctor" or not session.get("user_id"):
        return redirect("/doctor")

    return render_template("doctor/scan_qr.html")


# ------------------------------------------------
# REQUEST OTP VIA QR
# ------------------------------------------------
@medical_bp.route("/doctor/request-otp/<patient_id>", methods=["POST"])
def doctor_request_otp(patient_id):
    if session.get("role") != "doctor" or not session.get("user_id"):
        return redirect("/doctor")

    if not send_patient_otp(patient_id, session["user_id"]):
        flash("Patient phone number not available")
        return redirect("/doctor/dashboard")

    flash("OTP sent to patient")
    return redirect(f"/doctor/verify-otp/{patient_id}")
