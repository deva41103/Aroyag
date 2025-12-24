import random
from datetime import datetime, timedelta
from config import supabase, twilio_client, TWILIO_PHONE


def send_patient_otp(patient_id, doctor_id):
    phone_res = (
        supabase
        .table("users")
        .select("phone")
        .eq("id", patient_id)
        .limit(1)
        .execute()
    )

    if not phone_res.data or not phone_res.data[0]["phone"]:
        return False

    patient_phone = phone_res.data[0]["phone"]

    otp = str(random.randint(100000, 999999))
    expires_at = datetime.utcnow() + timedelta(minutes=5)

    supabase.table("patient_access_otps").insert({
        "patient_id": patient_id,
        "doctor_id": doctor_id,
        "otp": otp,
        "verified": False,
        "expires_at": expires_at.isoformat()
    }).execute()

    twilio_client.messages.create(
        body=f"Aroyagm: Your OTP for doctor access is {otp}. Valid for 5 minutes.",
        from_=TWILIO_PHONE,
        to=patient_phone
    )

    return True
