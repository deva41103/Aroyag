from flask import Blueprint, render_template, request, redirect, session, flash
from config import supabase

medical_bp = Blueprint("medical", __name__)


# ----------------------------------------
# SEARCH PATIENT BY HEALTH ID
# ----------------------------------------
@medical_bp.route("/doctor/search-patient", methods=["GET", "POST"])
def doctor_search_patient():
    if session.get("role") != "doctor":
        return redirect("/doctor/login")

    if request.method == "POST":
        health_id = request.form.get("health_id")

        res = (
            supabase
            .table("patient_profiles")
            .select("user_id, health_id")
            .eq("health_id", health_id)
            .execute()
        )

        if not res.data:
            flash("Patient not found")
            return redirect("/doctor/search-patient")

        patient_id = res.data[0]["user_id"]
        return redirect(f"/doctor/patient/{patient_id}")

    return render_template("doctor/doctor_patient_search.html")


# ----------------------------------------
# VIEW ALL MEDICAL RECORDS (ANY DOCTOR)
# ----------------------------------------
@medical_bp.route("/doctor/patient/<patient_id>")
def doctor_view_patient_records(patient_id):
    if session.get("role") != "doctor":
        return redirect("/doctor/login")

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


# ----------------------------------------
# ADD MEDICAL RECORD
# ----------------------------------------
@medical_bp.route("/doctor/patient/<patient_id>/add", methods=["GET", "POST"])
def doctor_add_medical_record(patient_id):
    if session.get("role") != "doctor":
        return redirect("/doctor/login")

    if request.method == "POST":
        title = request.form.get("title")
        description = request.form.get("description")
        doctor_id = session["user_id"]

        record = (
            supabase
            .table("medical_records")
            .insert({
                "patient_id": patient_id,
                "doctor_id": doctor_id,
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

                public_url = supabase.storage.from_("medical-files").get_public_url(path)

                supabase.table("medical_attachments").insert({
                    "medical_record_id": record_id,
                    "file_name": file.filename,
                    "file_type": file.content_type,
                    "file_url": public_url
                }).execute()

        flash("Medical record added successfully")
        return redirect(f"/doctor/patient/{patient_id}")

    return render_template(
        "doctor/doctor_add_record.html",
        patient_id=patient_id
    )
