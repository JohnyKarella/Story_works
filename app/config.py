import os
from pathlib import Path
from dotenv import load_dotenv

BASE_DIR = Path(__file__).resolve().parent.parent

# Load environment variables from .env if present
load_dotenv(BASE_DIR / ".env")


class Config:
    BASE_DIR = BASE_DIR
    SECRET_KEY = os.getenv("SECRET_KEY", "storyworks-secret-key-2026-production-ready")

    # Database: MongoDB Atlas
    DATABASE_TYPE = "mongodb"
    MONGO_URI = os.getenv("MONGO_URI", os.getenv("MONGODB_URI", "")).strip()
    MONGO_DB_NAME = os.getenv("MONGO_DB_NAME", os.getenv("MONGODB_DB_NAME", "storyworks")).strip() or "storyworks"

    # CORS: comma-separated allowed origins, e.g. "https://storyworks.studio,https://www.storyworks.studio"
    CORS_ORIGINS = [o.strip() for o in os.getenv("CORS_ORIGINS", "*").split(",") if o.strip()] or "*"

    # Uploads
    UPLOAD_FOLDER = os.getenv("UPLOAD_FOLDER", str(BASE_DIR / "uploads"))
    MAX_CONTENT_LENGTH = 16 * 1024 * 1024  # 16 MB max upload
    ALLOWED_EXTENSIONS = {"png", "jpg", "jpeg", "gif", "webp", "svg", "mp4", "pdf"}

    # Default Admin
    DEFAULT_ADMIN_USERNAME = os.getenv("DEFAULT_ADMIN_USERNAME", "admin")
    DEFAULT_ADMIN_EMAIL = os.getenv("DEFAULT_ADMIN_EMAIL", "admin@storyworks.studio")
    DEFAULT_ADMIN_PASSWORD = os.getenv("DEFAULT_ADMIN_PASSWORD", "SBL@Admin2026")

    # Forgot-password OTP: email via Gmail SMTP, SMS via Fast2SMS
    SMTP_HOST = os.getenv("SMTP_HOST", "").strip() or "smtp.gmail.com"
    SMTP_PORT = int(os.getenv("SMTP_PORT", "").strip() or "587")
    SMTP_USER = os.getenv("SMTP_USER", "").strip()
    SMTP_PASSWORD = os.getenv("SMTP_PASSWORD", "").replace(" ", "")  # Gmail shows App Passwords with spaces
    MAIL_FROM_NAME = os.getenv("MAIL_FROM_NAME", "Storyworks Studio")
    FAST2SMS_API_KEY = os.getenv("FAST2SMS_API_KEY", "").strip()
    OTP_EXPIRY_MINUTES = int(os.getenv("OTP_EXPIRY_MINUTES", "10"))
    OTP_MAX_ATTEMPTS = int(os.getenv("OTP_MAX_ATTEMPTS", "5"))
    OTP_RESEND_SECONDS = int(os.getenv("OTP_RESEND_SECONDS", "60"))

    # Session config
    SESSION_COOKIE_HTTPONLY = True
    SESSION_COOKIE_SAMESITE = "Lax"
    SESSION_COOKIE_SECURE = os.getenv("SESSION_COOKIE_SECURE", "False").lower() in ("true", "1", "yes")  # True on HTTPS hosting
