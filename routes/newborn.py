from flask import Blueprint, render_template, request, session, redirect
from config import supabase
import random
from datetime import datetime

newborn_bp = Blueprint("newborn", __name__)

# --------------------------------------
# REGISTER NEWBORN
# --------------------------------------
@newborn_bp.route("/hospital/newborn/register", methods=["GET", "POST"])
def register_newborn():
    if session.get("role") != "hospital":
        return redirect("/hospital")

    # ✅ STEP 1: Get actual hospital_id from hospital_profiles
    hospital_profile = (
        supabase
        .table("hospital_profiles")
        .select("hospital_id")
        .eq("user_id", session["user_id"])
        .execute()
    )

    if not hospital_profile.data:
        # No hospital profile found
        return redirect("/hospital/create-profile")

    hospital_id = hospital_profile.data[0]["hospital_id"]


    if request.method == "POST":
        health_id = f"NB-{datetime.now().year}-{random.randint(100000, 999999)}"

        data = {
            "hospital_id": hospital_id,  # ✅ FIXED
            "baby_name": request.form["baby_name"],
            "dob": request.form["dob"],
            "gender": request.form["gender"],
            "blood_group": request.form["blood_group"],
            "mother_name": request.form["mother_name"],
            "father_name": request.form["father_name"],
            "parent_phone": request.form["parent_phone"],
            "city": request.form["city"],
            "state": request.form["state"],
            "health_id": health_id,
            "documents": {}
        }

        supabase.table("newborns").insert(data).execute()

        return render_template(
            "hospital/newborn/newborn_success.html",
            health_id=health_id
        )

    return render_template("hospital/newborn/newborn_register.html")
