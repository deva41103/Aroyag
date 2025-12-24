import qrcode
import io
import base64
from datetime import datetime, timedelta
from config import supabase

def upload_patient_qr(patient_id):
    bucket = supabase.storage.from_("patient-qrs")
    path = f"{patient_id}.png"

    # 1️⃣ Check if QR already exists
    try:
        existing = bucket.list()
        if any(obj["name"] == path for obj in existing):
            return bucket.get_public_url(path)
    except Exception:
        pass  # ignore list errors

    # 2️⃣ Generate QR
    qr = qrcode.make(patient_id)
    buffer = io.BytesIO()
    qr.save(buffer, format="PNG")

    # 3️⃣ Upload bytes
    bucket.upload(
        path,
        buffer.getvalue(),
        {"content-type": "image/png"}
    )

    return bucket.get_public_url(path)