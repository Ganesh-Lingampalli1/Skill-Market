import hashlib
import secrets
from datetime import datetime, timedelta
from flask import current_app
from models import db, EmailVerification

class OTPService:
    SALT = "skillmarket-secure-otp-salt-v1"

    @classmethod
    def _hash_otp(cls, otp: str) -> str:
        return hashlib.sha256(f"{cls.SALT}:{otp.strip()}".encode('utf-8')).hexdigest()

    @classmethod
    def generate_otp(cls) -> str:
        # Cryptographically secure 6-digit number between 100000 and 999999
        return f"{secrets.randbelow(900000) + 100000}"

    @classmethod
    def create_verification_entry(cls, email: str, username: str = None, user_id: int = None) -> str:
        clean_email = email.lower().strip()
        clean_username = username.strip() if username else None

        # Expire and delete all previous unverified OTPs for this email to prevent reuse
        EmailVerification.query.filter_by(email=clean_email, verified=False).delete()

        otp = cls.generate_otp()
        otp_hash = cls._hash_otp(otp)
        
        # 5-minute expiration
        expiry_minutes = current_app.config.get('OTP_EXPIRATION_MINUTES', 5)
        expires_at = datetime.utcnow() + timedelta(minutes=expiry_minutes)

        verification = EmailVerification(
            user_id=user_id,
            email=clean_email,
            username=clean_username,
            otp_hash=otp_hash,
            expires_at=expires_at,
            attempts=0,
            verified=False,
            created_at=datetime.utcnow()
        )
        db.session.add(verification)
        db.session.commit()
        return otp

    @classmethod
    def verify_otp(cls, email: str, entered_otp: str) -> tuple[bool, str]:
        clean_email = email.lower().strip()
        record = EmailVerification.query.filter_by(
            email=clean_email,
            verified=False
        ).order_by(EmailVerification.created_at.desc()).first()

        if not record:
            return False, "No pending verification request found. Please request a new OTP."

        # Check expiration (5 minutes)
        if datetime.utcnow() > record.expires_at:
            return False, "OTP expired. Please request a new OTP."

        # Check maximum attempts to prevent brute force
        max_attempts = current_app.config.get('OTP_MAX_ATTEMPTS', 5)
        if record.attempts >= max_attempts:
            return False, "Maximum verification attempts exceeded. Please request a new OTP."

        record.attempts += 1
        db.session.commit()

        # Compare hashed OTP
        if record.otp_hash == cls._hash_otp(entered_otp.strip()):
            record.verified = True
            db.session.commit()
            return True, "✓ Email verified successfully!"

        return False, "Invalid OTP. Please try again."

    @classmethod
    def can_resend(cls, email: str) -> tuple[bool, int]:
        clean_email = email.lower().strip()
        record = EmailVerification.query.filter_by(
            email=clean_email,
            verified=False
        ).order_by(EmailVerification.created_at.desc()).first()

        if not record:
            return True, 0

        cooldown = current_app.config.get('OTP_RESEND_COOLDOWN_SECONDS', 60)
        time_since_creation = (datetime.utcnow() - record.created_at).total_seconds()
        if time_since_creation < cooldown:
            return False, int(cooldown - time_since_creation)
        return True, 0
