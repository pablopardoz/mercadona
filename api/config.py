import os
from dotenv import load_dotenv

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
load_dotenv(os.path.join(BASE_DIR, '.env'))


class Config:
    SECRET_KEY = os.environ['SECRET_KEY']
    JWT_EXPIRATION_HOURS = 24

    SUPABASE_DB_URL = os.environ['SUPABASE_DB_URL']
    SUPABASE_URL = os.environ.get('SUPABASE_URL', '')
    SUPABASE_KEY = os.environ.get('SUPABASE_KEY', '')

    GEMINI_API_KEY = os.environ.get('GEMINI_API_KEY', '')
