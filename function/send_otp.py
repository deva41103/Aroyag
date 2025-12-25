import random
from datetime import datetime, timedelta
from config import supabase, twilio_client, TWILIO_PHONE


def send_patient_otp(patient_id: str, doctor_id: str) -> bool:
    # 1️⃣ Fetch phone
    phone_res = (
        supabase
        .table("users")
        .select("phone")
        .eq("id", patient_id)
        .limit(1)
        .execute()
    )

    if not phone_res.data:
        return False

    patient_phone = phone_res.data[0]["phone"]

    # 2️⃣ Check existing valid OTP (cooldown)
    existing = (
        supabase
        .table("patient_access_otps")
        .select("id, expires_at")
        .eq("patient_id", patient_id)
        .eq("doctor_id", doctor_id)
        .eq("verified", False)
        .gt("expires_at", datetime.utcnow().isoformat())
        .limit(1)
        .execute()
    )

    if existing.data:
        print("⚠️ Existing OTP still valid. Not sending new one.")
        return True

    # 3️⃣ Generate new OTP
    otp = str(random.randint(100000, 999999))
    expires_at = datetime.utcnow() + timedelta(minutes=5)

    supabase.table("patient_access_otps").insert({
        "patient_id": patient_id,
        "doctor_id": doctor_id,
        "otp": otp,
        "verified": False,
        "expires_at": expires_at.isoformat()
    }).execute()

    # 4️⃣ DEV MODE
    print("===================================")
    print("🚧 DEVELOPMENT MODE")
    print(f"📞 Patient Phone: {patient_phone}")
    print(f"🔐 OTP: {otp}")
    print("⏱ Valid for 5 minutes")
    print("===================================")


    # 5️⃣ Send OTP via Twilio
    """twilio_client.messages.create(
        body=f"Aroyagm: Your OTP for doctor access is {otp}. Valid for 5 minutes.",
        from_=TWILIO_PHONE,
        to=patient_phone
    )"""
    
    return True
