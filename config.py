import os
from supabase import create_client
from dotenv import load_dotenv
from twilio.rest import Client

load_dotenv()

# ------------------------------------
# SUPABASE CONFIG
# ------------------------------------
SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_SERVICE_KEY = os.getenv("SUPABASE_SERVICE_ROLE_KEY")

if not SUPABASE_URL or not SUPABASE_SERVICE_KEY:
    raise RuntimeError("Supabase credentials are missing")

# 🔐 Server-side Supabase client (bypasses RLS safely)
supabase = create_client(SUPABASE_URL, SUPABASE_SERVICE_KEY)

# ------------------------------------
# TWILIO CONFIG
# ------------------------------------
TWILIO_ACCOUNT_SID = os.getenv("TWILIO_ACCOUNT_SID")
TWILIO_AUTH_TOKEN = os.getenv("TWILIO_AUTH_TOKEN")
TWILIO_PHONE = os.getenv("TWILIO_PHONE")

if not TWILIO_ACCOUNT_SID or not TWILIO_AUTH_TOKEN or not TWILIO_PHONE:
    raise RuntimeError("Twilio credentials are missing")

twilio_client = Client(TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN)
