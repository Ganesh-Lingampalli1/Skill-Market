import functools
import re
from datetime import datetime
from flask import (
    Blueprint, render_template, request, redirect,
    url_for, flash, session, g, jsonify
)
from models import db, User, EmailVerification
from services.otp_service import OTPService
from services.email_service import EmailService

auth_bp = Blueprint('auth', __name__)

def login_required(view):
    @functools.wraps(view)
    def wrapped_view(**kwargs):
        if g.user is None:
            flash("Please log in to access this page.", "warning")
            return redirect(url_for('auth.login', next=request.url))
        return view(**kwargs)
    return wrapped_view

def admin_required(view):
    @functools.wraps(view)
    def wrapped_view(**kwargs):
        if g.user is None:
            flash("Administrator login required.", "warning")
            return redirect(url_for('admin.login', next=request.url))
        if not g.user.is_admin:
            flash("Access denied: Administrator privileges required.", "error")
            return redirect(url_for('dashboard.index'))
        return view(**kwargs)
    return wrapped_view

EMAIL_REGEX = r'^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$'

@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    if g.user:
        return redirect(url_for('dashboard.index'))

    if request.method == 'POST':
        username = request.form.get('username', '').strip()
        email = request.form.get('email', '').strip().lower()

        if not username or not email:
            flash("Both username and email are required.", "error")
            return render_template('auth/login.html', username=username, email=email)

        user = User.query.filter(
            (User.username.ilike(username)) & (User.email.ilike(email))
        ).first()

        if not user:
            flash("Account not found. Please create an account first.", "error")
            return render_template('auth/login.html', username=username, email=email, account_not_found=True)

        if not user.is_verified:
            otp = OTPService.create_verification_entry(user.email, user.username, user_id=user.id)
            sent, send_msg = EmailService.send_verification_otp(user.email, user.username, otp)
            if not sent:
                flash(send_msg, "error")
            else:
                flash("Your account is not verified yet. A verification OTP has been sent to your email.", "info")
            return redirect(url_for('auth.verify_otp', email=user.email, username=user.username))

        # Successfully authenticate
        session.clear()
        session['user_id'] = user.id
        user.last_login = datetime.utcnow()
        db.session.commit()

        flash(f"Welcome back, {user.username}!", "success")
        next_url = request.args.get('next')
        if next_url and next_url.startswith('/'):
            return redirect(next_url)
        return redirect(url_for('dashboard.index'))

    return render_template('auth/login.html')

@auth_bp.route('/register', methods=['GET', 'POST'])
def register():
    if g.user:
        return redirect(url_for('dashboard.index'))

    if request.method == 'POST':
        username = request.form.get('username', '').strip()
        email = request.form.get('email', '').strip().lower()

        # Validation
        if not username:
            flash("Username is required.", "error")
            return render_template('auth/register.html', username=username, email=email)

        if len(username) < 3 or len(username) > 30:
            flash("Username must be between 3 and 30 characters.", "error")
            return render_template('auth/register.html', username=username, email=email)

        if not email or not re.match(EMAIL_REGEX, email):
            flash("Please enter a valid email address.", "error")
            return render_template('auth/register.html', username=username, email=email)

        existing_user_by_name = User.query.filter(User.username.ilike(username)).first()
        if existing_user_by_name and existing_user_by_name.is_verified:
            flash(f"Username '{username}' is already registered. Please login or choose another.", "error")
            return render_template('auth/register.html', username=username, email=email)

        existing_user_by_email = User.query.filter(User.email.ilike(email)).first()
        if existing_user_by_email and existing_user_by_email.is_verified:
            flash(f"Email '{email}' is already registered. Please login.", "error")
            return render_template('auth/register.html', username=username, email=email)

        # Generate secure OTP
        otp = OTPService.create_verification_entry(email, username)
        sent, send_msg = EmailService.send_verification_otp(email, username, otp)
        
        if not sent:
            flash(send_msg, "error")
        else:
            flash(f"A verification code has been sent to {email}. It will expire in 5 minutes.", "info")

        return redirect(url_for('auth.verify_otp', email=email, username=username))

    return render_template('auth/register.html')

@auth_bp.route('/verify-otp', methods=['GET', 'POST'])
def verify_otp():
    email = request.args.get('email', '') or request.form.get('email', '')
    username = request.args.get('username', '') or request.form.get('username', '')

    if not email:
        flash("Email address is required for verification.", "warning")
        return redirect(url_for('auth.register'))

    if request.method == 'POST':
        otp_digits = [request.form.get(f'digit{i}', '') for i in range(1, 7)]
        if all(otp_digits):
            entered_otp = "".join(otp_digits).strip()
        else:
            entered_otp = request.form.get('otp', '').strip()

        if not entered_otp:
            flash("Please enter the 6-digit verification code.", "error")
            return render_template('auth/verify_otp.html', email=email, username=username)

        success, message = OTPService.verify_otp(email, entered_otp)
        if success:
            user = User.query.filter(User.email.ilike(email)).first()
            if not user:
                if not username:
                    rec = EmailVerification.query.filter_by(email=email).order_by(EmailVerification.id.desc()).first()
                    username = rec.username if (rec and rec.username) else email.split('@')[0]

                user = User(
                    username=username,
                    email=email.lower(),
                    is_verified=True,
                    theme_preference='light',
                    created_at=datetime.utcnow()
                )
                db.session.add(user)
            else:
                user.is_verified = True
                if username:
                    user.username = username

            db.session.commit()
            flash("✓ Email verified successfully! You can now log in.", "success")
            return redirect(url_for('auth.login', prefill_username=user.username, prefill_email=user.email))
        else:
            flash(message, "error")
            return render_template('auth/verify_otp.html', email=email, username=username)

    return render_template('auth/verify_otp.html', email=email, username=username)

@auth_bp.route('/resend-otp', methods=['POST'])
def resend_otp():
    email = request.form.get('email', '').strip().lower()
    if not email:
        return jsonify({'success': False, 'message': 'Email is required'}), 400

    can_resend, wait_seconds = OTPService.can_resend(email)
    if not can_resend:
        return jsonify({
            'success': False,
            'message': f"Please wait {wait_seconds} seconds before requesting a new OTP."
        }), 429

    last_rec = EmailVerification.query.filter_by(email=email).order_by(EmailVerification.id.desc()).first()
    username = last_rec.username if last_rec else "User"

    # Generates new OTP and automatically expires prior unverified OTPs
    otp = OTPService.create_verification_entry(email, username)
    sent, send_msg = EmailService.send_verification_otp(email, username, otp)

    if not sent:
        return jsonify({
            'success': False,
            'message': send_msg
        }), 500

    return jsonify({
        'success': True,
        'message': f"A new 6-digit verification code has been sent to {email}."
    })

@auth_bp.route('/logout')
def logout():
    session.clear()
    flash("You have been successfully logged out.", "info")
    return redirect(url_for('auth.login'))
