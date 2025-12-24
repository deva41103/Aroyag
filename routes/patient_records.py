from flask import Blueprint, render_template, session, redirect
from config import supabase

# -------------------------------
# Patient Medical Records Blueprint
# -------------------------------
patient_records_bp = Blueprint(
    "patient_records",
    __name__,
    template_folder="templates"
)


@patient_records_bp.route("/patient/medical-records", methods=["GET"])
def patient_medical_records():
    # 🔐 Session & role check
    if session.get("role") != "patient" or not session.get("user_id"):
        return redirect("/patient")

    patient_id = session["user_id"]

    # --------------------------------------------------
    # Fetch patient's medical records (read-only)
    # --------------------------------------------------
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
