import os
from supabase import create_client
from dotenv import load_dotenv
from twilio.rest import Client

load_dotenv()

SUPABASE_URL = os.getenv("SUPABASE_URL")

# 🔐 USE SERVICE ROLE KEY (NOT ANON)
SUPABASE_SERVICE_KEY = os.getenv("SUPABASE_SERVICE_ROLE_KEY")

TWILIO_ACCOUNT_SID = os.getenv("TWILIO_ACCOUNT_SID")
TWILIO_AUTH_TOKEN = os.getenv("TWILIO_AUTH_TOKEN")
TWILIO_PHONE = os.getenv("TWILIO_PHONE")

# ✅ Server-side Supabase client
supabase = create_client(SUPABASE_URL, SUPABASE_SERVICE_KEY)

# ✅ Twilio client
twilio_client = Client(TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN)
