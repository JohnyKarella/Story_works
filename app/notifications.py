import json
import smtplib
import ssl
import urllib.request
from email.message import EmailMessage
from app.config import Config


def mask_email(email):
    """alex.smith@gmail.com -> al*******@gmail.com"""
    if not email or "@" not in email:
        return ""
    name, domain = email.split("@", 1)
    return f"{name[:2]}{'*' * max(len(name) - 2, 3)}@{domain}"


def mask_phone(phone):
    """+91 73492 51972 -> ******1972"""
    digits = "".join(c for c in (phone or "") if c.isdigit())
    return f"******{digits[-4:]}" if len(digits) >= 10 else ""


def send_email(to, subject, body):
    """Send a plain-text email through the configured SMTP account (Gmail by default)."""
    if not (Config.SMTP_USER and Config.SMTP_PASSWORD and to):
        return False
    msg = EmailMessage()
    msg["Subject"] = subject
    msg["From"] = f"{Config.MAIL_FROM_NAME} <{Config.SMTP_USER}>"
    msg["To"] = to
    msg.set_content(body)
    try:
        with smtplib.SMTP(Config.SMTP_HOST, Config.SMTP_PORT, timeout=15) as server:
            server.starttls(context=ssl.create_default_context())
            server.login(Config.SMTP_USER, Config.SMTP_PASSWORD)
            server.send_message(msg)
        return True
    except Exception as e:
        print(f"[!] Email send failed: {e}")
        return False


def send_sms_otp(phone, otp):
    """Send an OTP SMS through Fast2SMS (Indian 10-digit mobile numbers)."""
    digits = "".join(c for c in (phone or "") if c.isdigit())[-10:]
    if not Config.FAST2SMS_API_KEY or len(digits) != 10:
        return False
    payload = json.dumps({"route": "otp", "variables_values": otp, "numbers": digits}).encode()
    req = urllib.request.Request(
        "https://www.fast2sms.com/dev/bulkV2",
        data=payload,
        headers={"authorization": Config.FAST2SMS_API_KEY, "Content-Type": "application/json"},
        method="POST",
    )
    try:
        with urllib.request.urlopen(req, timeout=15) as resp:
            result = json.loads(resp.read().decode() or "{}")
        if not result.get("return"):
            print(f"[!] Fast2SMS rejected the SMS: {result.get('message')}")
            return False
        return True
    except Exception as e:
        print(f"[!] SMS send failed: {e}")
        return False


def send_password_reset_otp(user, otp):
    """Send the reset code to the user's email and mobile. Returns the masked destinations that succeeded."""
    name = user.get("full_name") or user.get("username", "")
    body = (
        f"Hi {name},\n\n"
        f"Your Storyworks Client Portal password reset code is: {otp}\n\n"
        f"This code expires in {Config.OTP_EXPIRY_MINUTES} minutes. "
        "If you did not request a password reset, you can ignore this email.\n\n"
        f"— {Config.MAIL_FROM_NAME}"
    )
    sent_to = []
    if send_email(user.get("email"), "Your password reset code", body):
        sent_to.append(mask_email(user.get("email")))
    if send_sms_otp(user.get("phone"), otp):
        sent_to.append(mask_phone(user.get("phone")))
    return sent_to
