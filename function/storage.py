from config import supabase
from werkzeug.utils import secure_filename
import uuid

def upload_to_supabase(bucket, file, user_id, folder):
    if not file or file.filename == "":
        return None

    filename = secure_filename(file.filename)
    ext = filename.rsplit(".", 1)[-1].lower()

    path = f"{user_id}/{folder}/{uuid.uuid4()}.{ext}"

    file_bytes = file.read()

    supabase.storage.from_(bucket).upload(
        path,
        file_bytes,
        file_options={
            "content-type": file.content_type
        }
    )

    return path


def get_signed_url(bucket: str, file_path: str, expires_in: int = 300):
    """
    Generate a temporary signed URL for a private file.
    Works with all Supabase Python SDK versions.
    """
    if not file_path:
        return None

    res = supabase.storage.from_(bucket).create_signed_url(
        file_path,
        expires_in
    )

    # 🔥 Handle list or dict response safely
    if isinstance(res, list) and len(res) > 0:
        return res[0].get("signedURL")

    if isinstance(res, dict):
        return res.get("signedURL")

    return None

