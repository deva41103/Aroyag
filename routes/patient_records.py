from flask import Blueprint, render_template, session, redirect
from config import supabase

patient_records_bp = Blueprint("patient_records", __name__)


@patient_records_bp.route("/patient/medical-records")
def patient_medical_records():
    if session.get("role") != "patient":
        return redirect("/patient/login")

    patient_id = session.get("user_id")

    records = (
        supabase
        .table("medical_records")
        .select("""
            id,
            title,
            description,
            created_at,
            medical_attachments (
                id,
                file_name,
                file_url
            ),
            users:doctor_id (
                doctor_profiles (
                    full_name,
                    specialization
                )
            )
        """)
        .eq("patient_id", patient_id)
        .order("created_at", desc=True)
        .execute()
    )


    return render_template(
        "patient/patient_medical_records.html",
        records=records.data
    )
