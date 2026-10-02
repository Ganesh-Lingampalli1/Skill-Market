import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import logging
from flask import current_app

logger = logging.getLogger('skillmarket.email')

class EmailService:
    @classmethod
    def send_verification_otp(cls, email: str, username: str, otp: str) -> tuple[bool, str]:
        """
        Sends verification OTP using Gmail SMTP or configured mail server.
        Does NOT expose the OTP in any return message or public store.
        """
        clean_email = email.strip()
        clean_username = username.strip() if username else "User"

        mail_username = current_app.config.get('MAIL_USERNAME', '').strip()
        mail_password = current_app.config.get('MAIL_PASSWORD', '').strip()
        mail_server = current_app.config.get('MAIL_SERVER', 'smtp.gmail.com').strip()
        mail_port = current_app.config.get('MAIL_PORT', 587)
        mail_use_tls = current_app.config.get('MAIL_USE_TLS', True)
        mail_use_ssl = current_app.config.get('MAIL_USE_SSL', False)
        sender = current_app.config.get('MAIL_DEFAULT_SENDER', '').strip() or f"SkillMarket Team <{mail_username or 'noreply@skillmarket.com'}>"

        if not mail_username or not mail_password:
            error_msg = (
                "Email delivery is not configured on the server. "
                "Please configure MAIL_USERNAME and MAIL_PASSWORD in your .env file."
            )
            logger.error(f"[SkillMarket Email] {error_msg}")
            return False, error_msg

        subject = "Verify your SkillMarket account"

        # Plain text fallback
        text_content = f"""Hello {clean_username},

Your SkillMarket verification OTP is:

{otp}

This OTP is valid for 5 minutes.

If you did not request this, please ignore this email.

Regards,
SkillMarket Team
"""

        # Styled HTML email
        html_content = f"""
        <!DOCTYPE html>
        <html>
        <head>
          <meta charset="utf-8">
          <style>
            body {{ font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Helvetica, Arial, sans-serif; background-color: #f8fafc; margin: 0; padding: 32px 16px; }}
            .card {{ max-width: 520px; margin: 0 auto; background: #ffffff; border-radius: 12px; padding: 40px; border: 1px solid #e2e8f0; box-shadow: 0 4px 6px -1px rgba(0,0,0,0.06); }}
            .logo {{ font-size: 24px; font-weight: 800; color: #0284c7; margin-bottom: 24px; }}
            .logo span {{ color: #0f172a; }}
            .otp-box {{ background-color: #f0f9ff; border: 2px dashed #0284c7; border-radius: 10px; padding: 20px; text-align: center; font-size: 36px; font-weight: 800; letter-spacing: 8px; color: #0369a1; margin: 28px 0; font-family: monospace, monospace; }}
            .footer {{ margin-top: 32px; padding-top: 20px; border-top: 1px solid #f1f5f9; font-size: 13px; color: #64748b; line-height: 1.5; }}
          </style>
        </head>
        <body>
          <div class="card">
            <div class="logo">Skill<span>Market</span></div>
            <h2 style="color: #0f172a; margin-top: 0; font-size: 22px; font-weight: 700;">Verify your SkillMarket account</h2>
            <p style="color: #334155; font-size: 15px; line-height: 1.6;">Hello <strong>{clean_username}</strong>,</p>
            <p style="color: #334155; font-size: 15px; line-height: 1.6;">Your SkillMarket verification OTP is:</p>
            <div class="otp-box">{otp}</div>
            <p style="color: #475569; font-size: 14px; line-height: 1.6;">
              This code is valid for <strong>5 minutes</strong>. For your security, do not share this code with anyone.
            </p>
            <p style="color: #94a3b8; font-size: 13px; margin-top: 20px;">
              If you did not request this account verification, you can safely disregard this email.
            </p>
            <div class="footer">
              Regards,<br>
              <strong>The SkillMarket Team</strong><br>
              <span style="color: #94a3b8;">Discover Skills That Actually Pay</span>
            </div>
          </div>
        </body>
        </html>
        """

        try:
            msg = MIMEMultipart('alternative')
            msg['Subject'] = subject
            msg['From'] = sender
            msg['To'] = clean_email

            msg.attach(MIMEText(text_content, 'plain'))
            msg.attach(MIMEText(html_content, 'html'))

            if mail_use_ssl:
                server = smtplib.SMTP_SSL(mail_server, mail_port, timeout=12)
            else:
                server = smtplib.SMTP(mail_server, mail_port, timeout=12)
                if mail_use_tls:
                    server.starttls()

            login_pass = mail_password.replace(' ', '') if ('gmail' in mail_server.lower() and ' ' in mail_password) else mail_password
            server.login(mail_username, login_pass)
            server.sendmail(sender, [clean_email], msg.as_string())
            server.quit()

            logger.info(f"OTP successfully delivered via SMTP to {clean_email}")
            return True, f"Verification code sent to {clean_email}"
        except Exception as e:
            logger.error(f"SMTP delivery failure for {clean_email}: {e}")
            return False, f"Failed to deliver verification email: {str(e)}"
