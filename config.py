import os
from pathlib import Path
from dotenv import load_dotenv

BASE_DIR = Path(__file__).resolve().parent

# Ensure .env or .env.txt from project root is loaded before reading values
for env_name in ('.env', '.env.txt'):
    env_path = BASE_DIR / env_name
    if env_path.is_file():
        load_dotenv(dotenv_path=env_path, override=True)

class Config:
    SECRET_KEY = os.getenv('SECRET_KEY', 'skillmarket-production-secret-key-replace-in-production')
    SQLALCHEMY_DATABASE_URI = os.getenv('DATABASE_URL', f"sqlite:///{BASE_DIR / 'skillmarket.db'}")
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    
    # Gmail SMTP Configuration for Real Email Delivery
    MAIL_SERVER = os.getenv('MAIL_SERVER', 'smtp.gmail.com').strip()
    MAIL_PORT = int(os.getenv('MAIL_PORT', 587))
    MAIL_USE_TLS = os.getenv('MAIL_USE_TLS', 'true').lower() in ('true', '1', 't')
    MAIL_USE_SSL = os.getenv('MAIL_USE_SSL', 'false').lower() in ('true', '1', 't')
    MAIL_USERNAME = os.getenv('MAIL_USERNAME', '').strip().strip('\'"')
    MAIL_PASSWORD = os.getenv('MAIL_PASSWORD', '').strip().strip('\'"')
    MAIL_DEFAULT_SENDER = os.getenv('MAIL_DEFAULT_SENDER', '').strip().strip('\'"')
    
    # OTP Security Thresholds
    OTP_EXPIRATION_MINUTES = int(os.getenv('OTP_EXPIRATION_MINUTES', 5))  # 5 minutes expiration
    OTP_MAX_ATTEMPTS = int(os.getenv('OTP_MAX_ATTEMPTS', 5))              # Max 5 attempts
    OTP_RESEND_COOLDOWN_SECONDS = int(os.getenv('OTP_RESEND_COOLDOWN_SECONDS', 60)) # 60s cooldown

    # AI Career Assistant & Resume Analyzer
    AI_API_KEY = os.getenv('AI_API_KEY', '').strip()
    AI_MODEL = os.getenv('AI_MODEL', 'gemini-1.5-flash').strip()
    MAX_RESUME_SIZE_MB = int(os.getenv('MAX_RESUME_SIZE_MB', 5))
