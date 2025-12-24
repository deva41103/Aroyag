import qrcode
import io
from config import supabase


def upload_patient_qr(patient_id: str) -> str:
    """
    Generates and uploads a QR code for a patient.
    If QR already exists, returns the existing public URL.
    """

    bucket = supabase.storage.from_("patient-qrs")
    path = f"{patient_id}.png"

    # --------------------------------------------------
    # 1️⃣ Check if QR already exists (safe approach)
    # --------------------------------------------------
    try:
        objects = bucket.list()
        for obj in objects:
            if obj.get("name") == path:
                return bucket.get_public_url(path)
    except Exception:
        # Storage listing can fail due to permissions or network
        pass

    # --------------------------------------------------
    # 2️⃣ Generate QR Code
    # --------------------------------------------------
    qr = qrcode.make(patient_id)

    buffer = io.BytesIO()
    qr.save(buffer, format="PNG")
    buffer.seek(0)

    # --------------------------------------------------
    # 3️⃣ Upload QR to Supabase Storage
    # --------------------------------------------------
    bucket.upload(
        path=path,
        file=buffer.read(),
        file_options={"content-type": "image/png"}
    )

    # --------------------------------------------------
    # 4️⃣ Return Public URL
    # --------------------------------------------------
    return bucket.get_public_url(path)
