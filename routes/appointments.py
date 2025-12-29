from flask import Blueprint, render_template, request, redirect, session
from config import supabase

appointments_bp = Blueprint("appointments", __name__)

# ----------------------------------------
# PATIENT – LIST DOCTORS
# ----------------------------------------
@appointments_bp.route("/patient/doctors")
def patient_doctors():
    if session.get("role") != "patient":
        return redirect("/patient/login")

    doctors = (
        supabase
        .table("doctor_profiles")
        .select("user_id, full_name, specialization, years_of_experience")
        .eq("verified", True)
        .eq("completed", True)
        .execute()
    )

    return render_template(
        "patient/patient_doctors.html",
        doctors=doctors.data
    )


# ----------------------------------------
# PATIENT – BOOK APPOINTMENT
# ----------------------------------------
@appointments_bp.route("/patient/book/<doctor_id>", methods=["GET", "POST"])
def book_appointment(doctor_id):
    if session.get("role") != "patient":
        return redirect("/patient/login")

    if request.method == "POST":
        supabase.table("appointments").insert({
            "patient_id": session["user_id"],
            "doctor_id": doctor_id,
            "appointment_date": request.form["date"],
            "reason": request.form["reason"]
        }).execute()

        return redirect("/patient/appointments")

    doctor = (
        supabase
        .table("doctor_profiles")
        .select("full_name, specialization")
        .eq("user_id", doctor_id)
        .single()
        .execute()
    )

    return render_template(
        "patient/patient_book_appointment.html",
        doctor=doctor.data
    )


# ----------------------------------------
# PATIENT – VIEW APPOINTMENTS
# ----------------------------------------
@appointments_bp.route("/patient/appointments")
def patient_appointments():
    if session.get("role") != "patient":
        return redirect("/patient/login")

    appointments = (
        supabase
        .table("appointments")
        .select("""
            id,
            appointment_date,
            appointment_time,
            status,
            doctor_profiles(full_name, specialization)
        """)
        .eq("patient_id", session["user_id"])
        .order("created_at", desc=True)
        .execute()
    )

    return render_template(
        "patient/patient_appointments.html",
        appointments=appointments.data
    )


# ----------------------------------------
# DOCTOR – VIEW & UPDATE APPOINTMENTS
# ----------------------------------------
@appointments_bp.route("/doctor/appointments", methods=["GET", "POST"])
def doctor_appointments():
    if session.get("role") != "doctor":
        return redirect("/doctor/login")

    if request.method == "POST":
        supabase.table("appointments").update({
            "status": request.form["status"],
            "appointment_time": request.form.get("time"),
            "doctor_note": request.form.get("note")
        }).eq("id", request.form["appointment_id"]).execute()

        return redirect("/doctor/appointments")

    appointments = (
        supabase
        .table("appointments")
        .select("""
            id,
            appointment_date,
            status,
            patient_profiles(full_name)
        """)
        .eq("doctor_id", session["user_id"])
        .order("created_at", desc=True)
        .execute()
    )

    return render_template(
        "doctor/doctor_appointments.html",
        appointments=appointments.data
    )

@appointments_bp.route("/doctor/all-appointments", methods=["GET", "POST"])
def doctor_all_appointments():
    if not session.get("user_id") or session.get("role") != "doctor":
        return redirect("/doctor/login")

    # Handle approve / reject
    if request.method == "POST":
        update_data = {
            "status": request.form["status"]
        }

        # ✅ add time ONLY if provided
        time_value = request.form.get("time")
        if time_value:
            update_data["appointment_time"] = time_value

        # ✅ add note ONLY if provided
        note_value = request.form.get("note")
        if note_value:
            update_data["doctor_note"] = note_value

        supabase.table("appointments") \
            .update(update_data) \
            .eq("id", request.form["appointment_id"]) \
            .execute()

        return redirect("/doctor/all-appointments")


    # Fetch ALL appointments
    appointments = (
        supabase
        .table("appointments")
        .select("""
            id,
            appointment_date,
            appointment_time,
            status,
            patient_profiles(full_name)
        """)
        .eq("doctor_id", session["user_id"])
        .order("appointment_date", desc=True)
        .execute()
    )

    return render_template(
        "doctor/doctor_all_appointments.html",
        appointments=appointments.data
    )
