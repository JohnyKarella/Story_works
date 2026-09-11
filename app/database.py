import sqlite3
import os
from pathlib import Path
from werkzeug.security import generate_password_hash
from app.config import Config
def get_db():
    """Create and return a database connection with dict-like Row factory."""
    db_path = Config.DATABASE_PATH
    os.makedirs(os.path.dirname(os.path.abspath(db_path)), exist_ok=True)
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON;")
    return conn
def init_db(app=None, run_seed=True):
    """Initialize database tables and create default admin user if not exists."""
    # Ensure uploads folder exists
    os.makedirs(Config.UPLOAD_FOLDER, exist_ok=True)
    conn = get_db()
    cursor = conn.cursor()
    # 1. Users table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT UNIQUE NOT NULL,
        email TEXT UNIQUE NOT NULL,
        password_hash TEXT NOT NULL,
        role TEXT DEFAULT 'admin',
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        last_login TIMESTAMP
    );
    """)
    # 2. Contact Inquiries table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS inquiries (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        first_name TEXT NOT NULL,
        last_name TEXT,
        email TEXT NOT NULL,
        phone TEXT,
        company TEXT,
        budget TEXT,
        services TEXT,
        message TEXT NOT NULL,
        status TEXT DEFAULT 'new',
        notes TEXT,
        ip_address TEXT,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    );
    """)
    # 3. Blogs table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS blogs (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        title TEXT NOT NULL,
        slug TEXT UNIQUE NOT NULL,
        category TEXT DEFAULT 'Blog',
        author TEXT DEFAULT 'Storyworks Studio',
        published_date TEXT,
        cover_image TEXT,
        excerpt TEXT,
        content TEXT,
        status TEXT DEFAULT 'published',
        views INTEGER DEFAULT 0,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    );
    """)
    # 4. Portfolio Projects table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS portfolio (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        title TEXT NOT NULL,
        slug TEXT UNIQUE NOT NULL,
        client TEXT,
        category TEXT,
        badge TEXT,
        cover_image TEXT,
        gallery_images TEXT,
        short_desc TEXT,
        full_desc TEXT,
        quote TEXT,
        year TEXT,
        project_url TEXT,
        is_featured INTEGER DEFAULT 0,
        status TEXT DEFAULT 'published',
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    );
    """)
    # 5. Services table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS services (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        title TEXT NOT NULL,
        slug TEXT UNIQUE,
        short_desc TEXT,
        full_desc TEXT,
        icon TEXT,
        display_order INTEGER DEFAULT 0,
        is_active INTEGER DEFAULT 1,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    );
    """)
    # 6. Subscribers table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS subscribers (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        email TEXT UNIQUE NOT NULL,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    );
    """)
    # 7. Site Settings table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS settings (
        key TEXT PRIMARY KEY,
        value TEXT,
        category TEXT DEFAULT 'general'
    );
    """)
    conn.commit()
    # Seed default admin if no user exists
    cursor.execute("SELECT COUNT(*) FROM users")
    if cursor.fetchone()[0] == 0:
        hashed = generate_password_hash(Config.DEFAULT_ADMIN_PASSWORD)
        cursor.execute(
            "INSERT INTO users (username, email, password_hash, role) VALUES (?, ?, ?, ?)",
            (Config.DEFAULT_ADMIN_USERNAME, Config.DEFAULT_ADMIN_EMAIL, hashed, "admin")
        )
        conn.commit()
        print(f"[*] Created default admin user: {Config.DEFAULT_ADMIN_USERNAME}")
    # Seed default site settings if not present
    default_settings = [
        ("site_name", "Storyworks Studio", "general"),
        ("site_tagline", "Where Strategy Meets Storytelling", "general"),
        ("contact_email", "hello@storyworks.studio", "contact"),
        ("contact_phone", "+91 98765 43210", "contact"),
        ("contact_address", "Bengaluru, Karnataka, India", "contact"),
        ("instagram_url", "https://www.instagram.com/storyworks.studio?igsi=aG5jY2w3YjA0amRy&utm_source=qr", "social"),
        ("linkedin_url", "https://linkedin.com", "social"),
        ("twitter_url", "https://x.com", "social"),
    ]
    for key, val, cat in default_settings:
        cursor.execute(
            "INSERT OR IGNORE INTO settings (key, value, category) VALUES (?, ?, ?)",
            (key, val, cat)
        )
    conn.commit()
    # Auto-seed initial content if database was freshly created
    if run_seed:
        cursor.execute("SELECT COUNT(*) FROM blogs")
        if cursor.fetchone()[0] == 0:
            try:
                from database.seed_data import seed_all
                seed_all()
            except Exception as seed_err:
                print(f"[*] Auto-seed notice: {seed_err}")
    conn.close()
    print("[*] Database initialized successfully.")
