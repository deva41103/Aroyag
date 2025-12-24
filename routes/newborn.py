import random
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
# REGISTER NEWBORN
# --------------------------------------
@newborn_bp.route("/hospital/newborn/register", methods=["GET", "POST"])
def register_newborn():
    # 🔐 Role & session check
    if session.get("role") != "hospital" or not session.get("user_id"):
        return redirect("/hospital")

    # --------------------------------------------------
    # Fetch actual hospital_id from hospital_profiles
    # --------------------------------------------------
    hospital_profile = (
        supabase
        .table("hospital_profiles")
        .select("hospital_id")
        .eq("user_id", session["user_id"])
        .execute()
    )

    if not hospital_profile.data:
        # Hospital profile not completed yet
        return redirect("/hospital/create-profile")

    hospital_id = hospital_profile.data[0]["hospital_id"]

    # --------------------------------------------------
    # HANDLE FORM SUBMIT
    # --------------------------------------------------
    if request.method == "POST":
        # Basic validation
        required_fields = [
            "baby_name", "dob", "gender", "blood_group",
            "mother_name", "parent_phone", "city", "state"
        ]

        for field in required_fields:
            if not request.form.get(field):
                flash("All required fields must be filled")
                return redirect(request.url)

        # Generate newborn health ID
        health_id = f"NB-{datetime.now().year}-{random.randint(100000, 999999)}"

        data = {
            "hospital_id": hospital_id,
            "baby_name": request.form.get("baby_name"),
            "dob": request.form.get("dob"),
            "gender": request.form.get("gender"),
            "blood_group": request.form.get("blood_group"),
            "mother_name": request.form.get("mother_name"),
            "father_name": request.form.get("father_name"),
            "parent_phone": request.form.get("parent_phone"),
            "city": request.form.get("city"),
            "state": request.form.get("state"),
            "health_id": health_id,
            "documents": {}
        }

        # Insert newborn record
        supabase.table("newborns").insert(data).execute()

        return render_template(
            "hospital/newborn/newborn_success.html",
            health_id=health_id
        )

    # --------------------------------------------------
    # SHOW REGISTRATION FORM
    # --------------------------------------------------
    return render_template("hospital/newborn/newborn_register.html")
