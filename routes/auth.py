from flask import Blueprint, render_template, request, redirect, session
from config import supabase

auth_bp = Blueprint("auth", __name__)

# --------------------------------------------------
# PATIENT LOGIN
# --------------------------------------------------
@auth_bp.route("/patient", methods=["GET", "POST"])
def patient_login():
    if request.method == "POST":
        phone = request.form["phone"]

        supabase.auth.sign_in_with_otp({
            "phone": phone
        })

        session["phone"] = phone
        session["login_role"] = "patient"

        return render_template("patient/patient_login.html", otp_sent=True)

    return render_template("patient/patient_login.html", otp_sent=False)


# --------------------------------------------------
# DOCTOR LOGIN
# --------------------------------------------------
@auth_bp.route("/doctor", methods=["GET", "POST"])
def doctor_login():
    if request.method == "POST":
        phone = request.form["phone"]

        supabase.auth.sign_in_with_otp({
            "phone": phone
        })

        session["phone"] = phone
        session["login_role"] = "doctor"

        return render_template("doctor/doctor_login.html", otp_sent=True)

    return render_template("doctor/doctor_login.html", otp_sent=False)

# --------------------------------------------------
# HOSPITAL LOGIN
# --------------------------------------------------
@auth_bp.route("/hospital", methods=["GET", "POST"])
def hospital_login():
    if request.method == "POST":
        phone = request.form["phone"]

        supabase.auth.sign_in_with_otp({
            "phone": phone
        })

        session["phone"] = phone
        session["login_role"] = "hospital"

        return render_template("hospital/hospital_login.html", otp_sent=True)

    return render_template("hospital/hospital_login.html", otp_sent=False)


# --------------------------------------------------
# VERIFY OTP (COMMON FOR ALL ROLES)
# --------------------------------------------------
@auth_bp.route("/verify-otp", methods=["POST"])
def verify_otp():
    otp = request.form["otp"]
    phone = session.get("phone")
    login_role = session.get("login_role")  # patient / doctor

    if not phone or not login_role:
        return redirect("/")

    # Verify OTP with Supabase
    auth_res = supabase.auth.verify_otp({
        "phone": phone,
        "token": otp,
        "type": "sms"
    })

    user = auth_res.user
    user_id = user.id

    # --------------------------------------------------
    # USERS TABLE (ROLE BASE)
    # --------------------------------------------------
    existing_user = (
        supabase
        .table("users")
        .select("*")
        .eq("id", user_id)
        .execute()
    )

    if not existing_user.data:
        supabase.table("users").insert({
            "id": user_id,
            "phone": phone,
            "role": login_role
        }).execute()

    session["user_id"] = user_id
    session["role"] = login_role

    # --------------------------------------------------
    # PATIENT FLOW
    # --------------------------------------------------
    if login_role == "patient":
        profile = (
            supabase
            .table("patient_profiles")
            .select("*")
            .eq("user_id", user_id)
            .execute()
        )

        if not profile.data:
            return redirect("/patient/create-profile")

        if not profile.data[0]["completed"]:
            return redirect("/patient/create-profile")

        return redirect("/patient/dashboard")

    # --------------------------------------------------
    # DOCTOR FLOW
    # --------------------------------------------------
    if login_role == "doctor":
        profile = (
            supabase
            .table("doctor_profiles")
            .select("*")
            .eq("user_id", user_id)
            .execute()
        )

        if not profile.data:
            return redirect("/doctor/create-profile")

        if not profile.data[0]["verified"]:
            return redirect("/doctor/pending-verification")

        return redirect("/doctor/dashboard")
    
    # --------------------------------------------------
    # HOSPITAL FLOW
    # --------------------------------------------------
    if login_role == "hospital":
        profile = (
            supabase
            .table("hospital_profiles")
            .select("*")
            .eq("user_id", user_id)
            .execute()
        )

        if not profile.data:
            return redirect("/hospital/create-profile")

        if not profile.data[0]["verified"]:
            return redirect("/hospital/pending-verification")

        return redirect("/hospital/dashboard")


    # Fallback
    return redirect("/")
