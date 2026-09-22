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
        role TEXT DEFAULT 'client',
        full_name TEXT,
        company TEXT,
        phone TEXT,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        last_login TIMESTAMP
    );
    """)
    # 2. Contact Inquiries table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS inquiries (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER,
        first_name TEXT NOT NULL,
        last_name TEXT,
        email TEXT NOT NULL,
        phone TEXT,
        company TEXT,
        budget TEXT,
        timeline TEXT,
        services TEXT,
        message TEXT NOT NULL,
        status TEXT DEFAULT 'new',
        notes TEXT,
        ip_address TEXT,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
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
        thumbnail_image TEXT,
        banner_image TEXT,
        approach_image TEXT,
        approach TEXT,
        middle_banner_image TEXT,
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
    # Migration: Ensure client-related columns exist in users table
    cursor.execute("PRAGMA table_info(users)")
    user_cols = {row["name"] for row in cursor.fetchall()}
    if "full_name" not in user_cols:
        cursor.execute("ALTER TABLE users ADD COLUMN full_name TEXT")
    if "company" not in user_cols:
        cursor.execute("ALTER TABLE users ADD COLUMN company TEXT")
    if "phone" not in user_cols:
        cursor.execute("ALTER TABLE users ADD COLUMN phone TEXT")

    # Migration: Ensure user_id, timeline, and updated_at columns exist in inquiries table
    cursor.execute("PRAGMA table_info(inquiries)")
    inquiry_cols = {row["name"] for row in cursor.fetchall()}
    if "user_id" not in inquiry_cols:
        cursor.execute("ALTER TABLE inquiries ADD COLUMN user_id INTEGER")
    if "timeline" not in inquiry_cols:
        cursor.execute("ALTER TABLE inquiries ADD COLUMN timeline TEXT")
    if "updated_at" not in inquiry_cols:
        cursor.execute("ALTER TABLE inquiries ADD COLUMN updated_at TIMESTAMP")

    # Backfill timeline from message if present
    try:
        cursor.execute("""
            UPDATE inquiries 
            SET timeline = SUBSTR(message, INSTR(message, '[Target Timeline: ') + 17, 
                                  INSTR(message, ']') - (INSTR(message, '[Target Timeline: ') + 17))
            WHERE (timeline IS NULL OR timeline = '') AND message LIKE '%[Target Timeline:%'
        """)
    except Exception:
        pass
    # Migration: Ensure portfolio-related columns exist
    cursor.execute("PRAGMA table_info(portfolio)")
    port_cols = {row["name"] for row in cursor.fetchall()}
    if "banner_image" not in port_cols:
        cursor.execute("ALTER TABLE portfolio ADD COLUMN banner_image TEXT")
    if "thumbnail_image" not in port_cols:
        cursor.execute("ALTER TABLE portfolio ADD COLUMN thumbnail_image TEXT")
    if "approach_image" not in port_cols:
        cursor.execute("ALTER TABLE portfolio ADD COLUMN approach_image TEXT")
    if "approach" not in port_cols:
        cursor.execute("ALTER TABLE portfolio ADD COLUMN approach TEXT")
    if "middle_banner_image" not in port_cols:
        cursor.execute("ALTER TABLE portfolio ADD COLUMN middle_banner_image TEXT")

    # Sync thumbnail_image and cover_image
    cursor.execute("UPDATE portfolio SET thumbnail_image = cover_image WHERE (thumbnail_image IS NULL OR thumbnail_image = '') AND cover_image IS NOT NULL AND cover_image != ''")
    cursor.execute("UPDATE portfolio SET cover_image = thumbnail_image WHERE (cover_image IS NULL OR cover_image = '') AND thumbnail_image IS NOT NULL AND thumbnail_image != ''")

    # Initial data backfill for standard case studies
    initial_portfolio_data = {
        1: {
            "banner_image": "/assets/portfolio_page/shaanvi posts/1_shaanvi.png",
            "thumbnail_image": "/assets/images/portfolio/hp/4.jpg",
            "approach_image": "/assets/portfolio_page/shaanvi posts/shaanvi-works.png",
            "approach": "We created a cohesive visual direction that places the fabric at the centre, using minimal design and balanced compositions to highlight texture, colour and detail. The focus was on building a clean, consistent and premium aesthetic that enhances the brand’s identity, resulting in a more refined presence and stronger visual recall.",
            "middle_banner_image": "/assets/portfolio_page/shaanvi posts/portfolio-works.png",
        },
        2: {
            "banner_image": "/assets/portfolio_page/mantras/matras-banner.png",
            "thumbnail_image": "/assets/images/portfolio/hp/2.jpg",
            "approach_image": "/assets/portfolio_page/mantras/matra-works.png",
            "approach": "We built a clean and informative digital presence that balances clinical expertise with approachability. Through minimal, structured design and educational-led content, we simplified complex treatments while maintaining a refined, premium aesthetic. The focus was on creating clarity, building trust and positioning Mantras as a credible and reliable clinic thus resulting in stronger engagement and a more consistent brand presence.",
            "middle_banner_image": "/assets/portfolio_page/mantras/phnbnr.png",
        },
        3: {
            "banner_image": "/assets/portfolio_page/picklejar/portfolio-banners.png",
            "thumbnail_image": "/assets/images/portfolio/hp/3.jpg",
            "approach_image": "/assets/portfolio_page/picklejar/postfolio-about.png",
            "approach": "We built a warm and engaging visual identity that brings out the richness and nostalgia of homemade flavours. Through vibrant, appetising visuals and relatable storytelling the focus was on making the product feel both authentic and desirable. The result is a distinctive and inviting brand presence that enhances recall and connects with audiences through taste, tradition and emotion.",
            "middle_banner_image": "/assets/portfolio_page/picklejar/portfolio_bnr.png",
        },
        4: {
            "banner_image": "/assets/portfolio_page/bship/bshipbnr.png",
            "thumbnail_image": "/assets/images/portfolio/hp/1.jpg",
            "approach_image": "/assets/portfolio_page/bship/postfolio-about.png",
            "approach": "We positioned BShip with a clear and structured communication style that reflects reliability, efficiency, and end-to-end logistics support. By organising core services into distinct, easily digestible segments, we streamlined complex supply-chain capabilities into an intuitive digital experience.",
            "middle_banner_image": "/assets/portfolio_page/bship/portfolio-works.png",
        },
        5: {
            "banner_image": "/assets/portfolio_page/fishland/portfolio-banners.png",
            "thumbnail_image": "/assets/images/portfolio/hp/5.jpg",
            "approach_image": "/assets/portfolio_page/fishland/postfolio-about.png",
            "approach": "We built a visually rich and appetite-led content direction that highlights freshness, quality and maritime authenticity. Through bold, clean compositions and vibrant storytelling, the focus was on positioning Fishland as a trusted destination for premium seafood.",
            "middle_banner_image": "/assets/portfolio_page/fishland/portfolio-works.png",
        },
        6: {
            "banner_image": "/assets/portfolio_page/temple/portfolio-banners.png",
            "thumbnail_image": "/assets/images/portfolio/hp/6.jpg",
            "approach_image": "/assets/portfolio_page/temple/postfolio-about.png",
            "approach": "We crafted a spiritual and cultural preservation narrative that documents sacred temple architecture, intricate sculptures, and timeless ritual traditions with profound dignity and visual grandeur.",
            "middle_banner_image": "/assets/portfolio_page/temple/portfolio-works.png",
        },
        7: {
            "banner_image": "/assets/portfolio_page/sbl_food/portfolio-banners.png",
            "thumbnail_image": "/assets/images/portfolio/hp/7.jpg",
            "approach_image": "/assets/portfolio_page/sbl_food/postfolio-about.png",
            "approach": "We helped position SBL Food as a brand with a simplified and emotion-led communication style. By highlighting purity, tradition and everyday nourishment, we crafted an identity that connects deeply with modern households while celebrating culinary heritage.",
            "middle_banner_image": "/assets/portfolio_page/sbl_food/portfolio-works.png",
        },
        8: {
            "banner_image": "/assets/portfolio_page/sbl_farm/portfolio-banners.png",
            "thumbnail_image": "/assets/images/portfolio/hp/8.jpg",
            "approach_image": "/assets/portfolio_page/sbl_farm/postfolio-about.png",
            "approach": "We positioned SBL Farms with a storytelling-led communication style that captures the authenticity of the land, fresh produce, and regenerative farming. Through natural visuals and grounded narratives, we connected the farm-to-table ethos with modern consumers.",
            "middle_banner_image": "/assets/portfolio_page/sbl_farm/portfolio-works.png",
        },
        9: {
            "banner_image": "/assets/portfolio_page/books/portfolio-banners.png",
            "thumbnail_image": "/assets/images/portfolio/hp/9.jpg",
            "approach_image": "/assets/portfolio_page/books/postfolio-about.png",
            "approach": "We positioned Achuthan Publications with a clear and academically grounded communication style. By balancing timeless editorial elegance with structured layouts, we crafted an authoritative presence celebrating literature and scholarship.",
            "middle_banner_image": "/assets/portfolio_page/books/portfolio-works.png",
        },
    }
    for pid, vals in initial_portfolio_data.items():
        cursor.execute("""
            UPDATE portfolio
            SET banner_image = COALESCE(NULLIF(banner_image, ''), ?),
                thumbnail_image = COALESCE(NULLIF(thumbnail_image, ''), ?),
                approach_image = COALESCE(NULLIF(approach_image, ''), ?),
                approach = COALESCE(NULLIF(approach, ''), ?),
                middle_banner_image = COALESCE(NULLIF(middle_banner_image, ''), ?)
            WHERE id = ?
        """, (vals["banner_image"], vals["thumbnail_image"], vals["approach_image"], vals["approach"], vals["middle_banner_image"], pid))

    conn.commit()
    # Seed default admin if no user exists
    cursor.execute("SELECT COUNT(*) FROM users")
    if cursor.fetchone()[0] == 0:
        hashed = generate_password_hash(Config.DEFAULT_ADMIN_PASSWORD)
        cursor.execute(
            "INSERT INTO users (username, email, password_hash, role, full_name) VALUES (?, ?, ?, ?, ?)",
            (Config.DEFAULT_ADMIN_USERNAME, Config.DEFAULT_ADMIN_EMAIL, hashed, "admin", "Studio Admin")
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
    # Ensure standard services match website offerings
    cursor.execute("SELECT slug FROM services")
    existing_slugs = {row[0] for row in cursor.fetchall()}
    if "brand-strategy-identity" in existing_slugs or len(existing_slugs) == 0:
        # Clear legacy seeded services if present
        cursor.execute("DELETE FROM services WHERE slug IN ('brand-strategy-identity', 'web-design-digital-experiences', 'photography-visual-craft', 'local-seo-performance-marketing')")
        standard_services = [
            ("Brand Strategy", "brand-strategy", "We move beyond aesthetics to architect the strategic soul of your business. By synthesizing market intelligence with intuition, we build the narrative frameworks that drive your brand’s future.", "We move beyond aesthetics to architect the strategic soul of your business. By synthesizing market intelligence with intuition, we build the narrative frameworks that drive your brand’s future.", "fas fa-chart-line", 1, 1),
            ("Brand Identity & Design", "brand-identity-design", "We craft visual legacies through intentional design, from signature logos to multi-sensory systems. Every touchpoint is engineered for flawless consistency, creating a timeless invitation into your brand’s world.", "We craft visual legacies through intentional design, from signature logos to multi-sensory systems. Every touchpoint is engineered for flawless consistency, creating a timeless invitation into your brand’s world.", "fas fa-search", 2, 1),
            ("Content & Copywriting", "content-copywriting", "Our narratives do more than fill space; they command attention and build lasting rapport. We translate complex value propositions into persuasive human stories that sell a philosophy, not just a product.", "Our narratives do more than fill space; they command attention and build lasting rapport. We translate complex value propositions into persuasive human stories that sell a philosophy, not just a product.", "fas fa-thumbs-up", 3, 1),
            ("Digital Marketing", "digital-marketing", "Our approach integrates high-intent SEO and strategic social storytelling into performance-driven ecosystems that grow your community and your revenue in equal measure.", "Our approach integrates high-intent SEO and strategic social storytelling into performance-driven ecosystems that grow your community and your revenue in equal measure.", "fab fa-google", 4, 1),
            ("Web & Experience Design", "web-experience-design", "We view the digital interface as a premier storefront. Our team designs high-conversion digital environments where elegant minimalism meets functional rigor, ensuring every click feels intuitive and every interaction reinforces trust.", "We view the digital interface as a premier storefront. Our team designs high-conversion digital environments where elegant minimalism meets functional rigor, ensuring every click feels intuitive and every interaction reinforces trust.", "fas fa-laptop-code", 5, 1),
            ("Launch & Campaign Strategy", "launch-campaign-strategy", "We transform entries into arrivals through strategic blueprints and high-impact storytelling. By orchestrating the pivotal moments where brands meet the world, we ensure your debut is both seen and felt.", "We transform entries into arrivals through strategic blueprints and high-impact storytelling. By orchestrating the pivotal moments where brands meet the world, we ensure your debut is both seen and felt.", "fas fa-code", 6, 1),
        ]
        for title, slug, sdesc, fdesc, icon, order, active in standard_services:
            cursor.execute(
                """
                INSERT OR IGNORE INTO services (title, slug, short_desc, full_desc, icon, display_order, is_active)
                VALUES (?, ?, ?, ?, ?, ?, ?)
                """,
                (title, slug, sdesc, fdesc, icon, order, active),
            )
        conn.commit()
    # Ensure all cover_image paths in blogs and portfolio start with '/'
    cursor.execute("UPDATE blogs SET cover_image = '/' || cover_image WHERE cover_image IS NOT NULL AND cover_image != '' AND cover_image NOT LIKE '/%' AND cover_image NOT LIKE 'http%'")
    cursor.execute("UPDATE portfolio SET cover_image = '/' || cover_image WHERE cover_image IS NOT NULL AND cover_image != '' AND cover_image NOT LIKE '/%' AND cover_image NOT LIKE 'http%'")
    # Check if legacy blog seeds exist (e.g. power-of-visual-storytelling)
    cursor.execute("SELECT slug FROM blogs")
    blog_slugs = {row[0] for row in cursor.fetchall()}
    if "power-of-visual-storytelling" in blog_slugs:
        cursor.execute("DELETE FROM blogs WHERE slug IN ('power-of-visual-storytelling', 'building-a-distinct-brand-voice', 'data-driven-creative-growth')")
        new_blogs = [
            ("In-House Marketing vs Hiring a Bangalore Agency: What’s the Real Cost?", "in-house-marketing-vs-hiring-agency-cost", "Strategy & Scaling", "Storyworks Studio", "MAR 16, 2026", "/assets/blogs/d1.jpg", "The choice between creating an internal marketing team and outsourcing to an external agency is frequently presented as a matter of comparing costs. For a founder, though the true issue isn't how much you spend, it's the return you receive for it.", "The choice between creating an internal marketing team and outsourcing to an external agency is frequently presented as a matter of comparing costs. For a founder, though the true issue isn't how much you spend, it's the return you receive for it. Revenue, speed and reliability are far more important than mere superficial savings.\nMarketing today is not a single role, it demands strategy, content, design, performance marketing, analytics and ongoing optimization. Assembling an in-house team that performs effectively in all these functions is costly and time-consuming.", "published"),
            ("The 2026 Digital Marketing Playbook for Bangalore SMEs: What Actually Works", "digital-marketing-playbook-bangalore-smes", "Digital Growth", "Storyworks Studio", "MAR 20, 2026", "/assets/blogs/e1.jpg", "Digital marketing has advanced to the stage where fragmented initiatives no longer yield significant outcomes. For small and medium-sized enterprises in Bengaluru, the issue is not an absence of avenues but rather clarity on what truly fuels expansion.", "Digital marketing has advanced to the stage where fragmented initiatives no longer yield significant outcomes. For small and medium-sized enterprises in Bengaluru, the issue is not an absence of avenue but rather uncertainty about what truly fuels expansion.\nThe approach for 2026 emphasizes building a targeted system aligned with customer behavior and business goals, rather than experimenting across every platform.", "published"),
            ("Why Most Businesses Struggle With Marketing Even After Spending on It", "why-businesses-struggle-with-marketing", "Marketing Strategy", "Storyworks Studio", "MAR 26, 2026", "/assets/blogs/f1.jpg", "Building a brand today comes with far more challenges than just creating a product and putting it online. The absence of a suitable marketing framework is one of the most serious difficulties companies confront.", "Building a brand today comes with far more challenges than just creating a product and putting it online. The absence of a suitable marketing framework is one of the most serious difficulties companies confront, not the absence of marketing activity.\nHow effectively several departments cooperate concurrently determines the modern success of brand expansion. Performance marketing, customer psychology, SEO, analytics, design, storytelling, and conversion optimization all have to work in perfect harmony.", "published")
        ]
        for title, slug, cat, author, pdate, cimg, excerpt, content, status in new_blogs:
            cursor.execute(
                """
                INSERT OR IGNORE INTO blogs (title, slug, category, author, published_date, cover_image, excerpt, content, status)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (title, slug, cat, author, pdate, cimg, excerpt, content, status)
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
