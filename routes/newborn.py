import random
import uuid
from datetime import datetime
from flask import Blueprint, render_template, request, session, redirect, flash
from config import supabase

# -------------------------------
# Newborn Blueprint
# -------------------------------
newborn_bp = Blueprint(
    "newborn",
    __name__,
    template_folder="templates"
)

# --------------------------------------
# REGISTER NEWBORN (NO OTP)
# --------------------------------------
@newborn_bp.route("/hospital/newborn/register", methods=["GET", "POST"])
def register_newborn():

    # 🔐 Role & session check
    if session.get("role") != "hospital" or not session.get("user_id"):
        return redirect("/hospital")

    # ----------------------------------
    # Get hospital_id (place of birth)
    # ----------------------------------
    hospital_profile = (
        supabase
        .table("hospital_profiles")
        .select("hospital_id")
        .eq("user_id", session["user_id"])
        .single()
        .execute()
    )

    if not hospital_profile.data:
        return redirect("/hospital/create-profile")

    hospital_id = hospital_profile.data["hospital_id"]

    # ----------------------------------
    # HANDLE FORM SUBMISSION
    # ----------------------------------
    if request.method == "POST":

        required_fields = [
            "baby_name",
            "dob",
            "gender",
            "blood_group",
            "mother_name",
            "parent_phone",
            "city"
        ]

        for field in required_fields:
            if not request.form.get(field):
                flash("Please fill all required fields")
                return redirect(request.url)

        newborn_id = str(uuid.uuid4())

        # ✅ Generate Baby Health ID
        baby_health_id = f"NB-{datetime.now().year}-{random.randint(100000, 999999)}"

        # ----------------------------------
        # COLLECT DATA
        # ----------------------------------
        data = {
            "id": newborn_id,
            "hospital_id": hospital_id,

            # Baby details
            "baby_name": request.form.get("baby_name"),
            "dob": request.form.get("dob"),
            "time_of_birth": request.form.get("time_of_birth"),
            "gender": request.form.get("gender"),
            "birth_weight": request.form.get("birth_weight"),
            "birth_height": request.form.get("birth_height"),
            "blood_group": request.form.get("blood_group"),
            "city": request.form.get("city"),
            "state": request.form.get("state"),

            # Parent details
            "mother_name": request.form.get("mother_name"),
            "father_name": request.form.get("father_name"),
            "parent_phone": request.form.get("parent_phone"),
            "email": request.form.get("email"),
            "address": request.form.get("address"),

            # Medical info
            "term": request.form.get("term"),
            "delivery_type": request.form.get("delivery_type"),
            "birth_complications": request.form.get("birth_complications") == "yes",
            "apgar_score": request.form.get("apgar_score"),
            "vaccinations": request.form.getlist("vaccinations"),
            "neonatal_conditions": request.form.get("neonatal_conditions"),

            # IDs
            "mother_aadhaar": request.form.get("mother_aadhaar"),
            "mother_health_id": request.form.get("mother_health_id"),  # OPTIONAL
            "baby_health_id": baby_health_id,

            "documents": {}
        }

        # ----------------------------------
        # INSERT INTO DATABASE
        # ----------------------------------
        supabase.table("newborns").insert(data).execute()

        # ----------------------------------
        # DOCUMENT UPLOAD (PRIVATE BUCKET)
        # ----------------------------------
        documents = {}

        def upload_doc(file, filename):
            if file and file.filename:
                path = f"{newborn_id}/{filename}"
                supabase.storage.from_("newborn-documents").upload(
                    path,
                    file.read(),
                    {"content-type": file.content_type}
                )
                documents[filename] = path

        upload_doc(request.files.get("mother_aadhaar_file"), "mother_aadhaar.pdf")
        upload_doc(request.files.get("arogyam_id_file"), "arogyam_id.pdf")
        upload_doc(request.files.get("discharge_summary_file"), "discharge_summary.pdf")

        if documents:
            supabase.table("newborns") \
                .update({"documents": documents}) \
                .eq("id", newborn_id) \
                .execute()

        flash(f"Newborn registered successfully. Health ID: {baby_health_id}")

        return render_template(
            "hospital/newborn/newborn_success.html",
            health_id=baby_health_id
        )

    # ----------------------------------
    # SHOW FORM
    # ----------------------------------
    return render_template("hospital/newborn/newborn_register.html")
