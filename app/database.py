import os
import re
from datetime import datetime
from bson import ObjectId
import pymongo
from pymongo import MongoClient
from werkzeug.security import generate_password_hash
from app.config import Config

_client = None

def get_client():
    """Create and return a cached MongoClient, connecting to MongoDB Atlas or falling back to local store."""
    global _client
    if _client is not None:
        return _client

    uri = (Config.MONGO_URI or "").strip()
    if uri and (uri.startswith("mongodb://") or uri.startswith("mongodb+srv://")):
        print(f"[*] Connecting to MongoDB Atlas ({Config.MONGO_DB_NAME})...")
        client = MongoClient(uri, serverSelectionTimeoutMS=10000)
        try:
            client.admin.command("ping")
        except Exception as e:
            # Fail loudly: silently falling back to memory would lose every write.
            raise RuntimeError(f"Could not connect to MongoDB Atlas: {e}") from e
        print("[*] Successfully connected to MongoDB Atlas!")
        _client = client
        return _client

    print("[!] MONGO_URI not set - using temporary in-memory database (data is lost on restart).")
    try:
        import mongomock
        _client = mongomock.MongoClient()
    except ImportError:
        _client = MongoClient("mongodb://localhost:27017/", serverSelectionTimeoutMS=2000)
    return _client

def get_db():
    """Return the active MongoDB database object."""
    client = get_client()
    return client[Config.MONGO_DB_NAME]

def get_next_sequence_value(sequence_name):
    """Generate an atomic auto-increment integer ID for collections."""
    db = get_db()
    seq = db.counters.find_one_and_update(
        {"_id": sequence_name},
        {"$inc": {"seq": 1}},
        upsert=True,
        return_document=pymongo.ReturnDocument.AFTER
    )
    return seq["seq"]

def to_query_id(val):
    """Normalize ID lookup to match either auto-increment integer 'id' or ObjectId '_id'."""
    if isinstance(val, int):
        return {"$or": [{"id": val}, {"id": str(val)}]}
    s = str(val).strip()
    if s.isdigit():
        return {"$or": [{"id": int(s)}, {"id": s}]}
    if ObjectId.is_valid(s):
        return {"$or": [{"_id": ObjectId(s)}, {"id": s}]}
    return {"id": s}

def serialize_doc(doc):
    """Convert MongoDB BSON document to clean dict with 'id' and stringified '_id'."""
    if not doc:
        return None
    d = dict(doc)
    if "_id" in d:
        oid_str = str(d["_id"])
        d["_id"] = oid_str
        if "id" not in d:
            d["id"] = oid_str
    return d

def migrate_login_history(db):
    """Move entries from the legacy `login_history` collection into
    `admin_login_history` / `client_login_history`, keeping their ids, then
    drop the legacy collection so this runs once."""
    if "login_history" not in db.list_collection_names():
        return
    try:
        moved = {"admin_login_history": 0, "client_login_history": 0}
        for doc in db.login_history.find({}):
            target = "admin_login_history" if doc.get("role") == "admin" else "client_login_history"
            db[target].replace_one({"_id": doc["_id"]}, doc, upsert=True)
            moved[target] += 1
        for name in moved:
            top = db[name].find_one({"id": {"$type": "int"}}, sort=[("id", pymongo.DESCENDING)])
            if top:
                db.counters.update_one({"_id": f"{name}_id"}, {"$max": {"seq": top["id"]}}, upsert=True)
        db.login_history.drop()
        print(f"[*] Split login history: {moved['admin_login_history']} admin, "
              f"{moved['client_login_history']} client entries (old login_history collection removed).")
    except Exception as mig_err:
        print(f"[!] Login history migration error: {mig_err}")


def init_db(app=None, run_seed=True):
    """Initialize MongoDB collections, indexes, and seed default data."""
    os.makedirs(Config.UPLOAD_FOLDER, exist_ok=True)
    db = get_db()

    # 1. Ensure indexes
    try:
        db.users.create_index([("username", pymongo.ASCENDING)], unique=True)
        db.users.create_index([("email", pymongo.ASCENDING)], unique=True)
        db.blogs.create_index([("slug", pymongo.ASCENDING)], unique=True)
        db.portfolio.create_index([("slug", pymongo.ASCENDING)], unique=True)
        db.services.create_index([("slug", pymongo.ASCENDING)], unique=True)
        db.settings.create_index([("key", pymongo.ASCENDING)], unique=True)
        db.subscribers.create_index([("email", pymongo.ASCENDING)], unique=True)
    except Exception as idx_err:
        print(f"[*] Notice on index creation: {idx_err}")

    # 1b. Split the old shared login_history collection into admin/client collections (runs once)
    migrate_login_history(db)

    # 2. Check if we have exported data from sqlite_dump.json to migrate
    dump_path = os.path.join(str(Config.BASE_DIR.parent), "sqlite_dump.json")
    actual_dump = dump_path if os.path.exists(dump_path) else None

    if actual_dump and os.path.exists(actual_dump) and db.portfolio.count_documents({}) == 0:
        import json
        try:
            with open(actual_dump, "r", encoding="utf-8") as f:
                dump_data = json.load(f)

            print("[*] Migrating SQLite data to MongoDB Atlas collections...")
            for table_name, rows in dump_data.items():
                if not rows:
                    continue
                col = getattr(db, table_name)
                if col.count_documents({}) == 0:
                    for row in rows:
                        row_copy = dict(row)
                        col.insert_one(row_copy)
                    # Update sequence counter
                    max_id = max((r.get("id") or 0 for r in rows if isinstance(r.get("id"), int)), default=0)
                    if max_id > 0:
                        seq_key = {
                            "users": "user_id",
                            "inquiries": "inquiry_id",
                            "blogs": "blog_id",
                            "portfolio": "portfolio_id",
                            "services": "service_id",
                            "subscribers": "subscriber_id",
                        }.get(table_name, f"{table_name}_id")

                        db.counters.update_one(
                            {"_id": seq_key},
                            {"$set": {"seq": max_id}},
                            upsert=True
                        )
            print("[*] Successfully migrated all records into MongoDB Atlas collections!")
        except Exception as mig_err:
            print(f"[!] SQLite migration error: {mig_err}")

    # 3. Seed default admin user if not exists
    if db.users.count_documents({}) == 0:
        hashed = generate_password_hash(Config.DEFAULT_ADMIN_PASSWORD)
        admin_id = get_next_sequence_value("user_id")
        db.users.insert_one({
            "id": admin_id,
            "username": Config.DEFAULT_ADMIN_USERNAME,
            "email": Config.DEFAULT_ADMIN_EMAIL,
            "password_hash": hashed,
            "role": "admin",
            "full_name": "Studio Admin",
            "company": "Storyworks Studio",
            "phone": "+91 73492 51972",
            "created_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "last_login": None,
        })
        print(f"[*] Created default admin user: {Config.DEFAULT_ADMIN_USERNAME}")

    # 4. Seed default settings if not present
    default_settings = [
        {"key": "site_name", "value": "Storyworks Studio", "category": "general"},
        {"key": "site_tagline", "value": "Where Strategy Meets Storytelling", "category": "general"},
        {"key": "contact_email", "value": "hello@storyworks.studio", "category": "contact"},
        {"key": "contact_phone", "value": "+91 98765 43210", "category": "contact"},
        {"key": "contact_address", "value": "Bengaluru, Karnataka, India", "category": "contact"},
        {"key": "instagram_url", "value": "https://www.instagram.com/storyworks.studio?igsi=aG5jY2w3YjA0amRy&utm_source=qr", "category": "social"},
        {"key": "linkedin_url", "value": "https://linkedin.com", "category": "social"},
        {"key": "twitter_url", "value": "https://x.com", "category": "social"},
    ]
    for s in default_settings:
        db.settings.update_one({"key": s["key"]}, {"$setOnInsert": s}, upsert=True)

    # 5. Seed default 9 portfolio items if empty
    if db.portfolio.count_documents({}) == 0:
        initial_portfolios = [
            {
                "id": 1,
                "title": "Shaanvi",
                "slug": "shaanvi",
                "client": "Shaanvi",
                "category": "Branding & Packaging",
                "badge": "SHAANVI",
                "cover_image": "assets/images/portfolio/hp/4.jpg",
                "thumbnail_image": "assets/images/portfolio/hp/4.jpg",
                "banner_image": "/assets/portfolio_page/shaanvi posts/1_shaanvi.png",
                "approach_image": "/assets/portfolio_page/shaanvi posts/shaanvi-works.png",
                "approach": "We adopted an architectural minimalism philosophy focusing on light, form, and texture.",
                "middle_banner_image": "/assets/portfolio_page/shaanvi posts/portfolio-works.png",
                "gallery_images": "[]",
                "short_desc": "End-to-end brand identity, packaging design, and visual art direction for premium organic foods.",
                "full_desc": "Shaanvi approached Story Works Studio to create a timeless visual identity.",
                "quote": "We finally have a brand voice that feels as premium as our products. The level of intentionality in every design choice has given our team a clear North Star for all future growth.",
                "year": "2026",
                "project_url": "1_shaanvi.html",
                "is_featured": 1,
                "status": "published",
                "created_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            },
            {
                "id": 2,
                "title": "Mantras",
                "slug": "mantras",
                "client": "Mantras",
                "category": "Brand Strategy & Identity",
                "badge": "MANTRAS",
                "cover_image": "assets/images/portfolio/hp/2.jpg",
                "thumbnail_image": "assets/images/portfolio/hp/2.jpg",
                "banner_image": "/assets/portfolio_page/mantras/matras-banner.png",
                "approach_image": "/assets/portfolio_page/mantras/matra-works.png",
                "approach": "We built a clean and informative digital presence that balances clinical expertise with approachability.",
                "middle_banner_image": "/assets/portfolio_page/mantras/phnbnr.png",
                "gallery_images": "[]",
                "short_desc": "Holistic brand positioning and serene packaging for modern wellness lifestyle products.",
                "full_desc": "Holistic brand positioning and serene packaging for modern wellness lifestyle products.",
                "quote": "The transition from a concept to a living brand felt seamless under their guidance. They have a rare ability to bridge the gap between creative storytelling and real-world business logic.",
                "year": "2026",
                "project_url": "2_mantras.html",
                "is_featured": 1,
                "status": "published",
                "created_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            },
            {
                "id": 3,
                "title": "Bhruhadrupi Hanuman Temple",
                "slug": "bhruhadrupi-temple",
                "client": "Bhruhadrupi",
                "category": "Architectural Visuals & Print",
                "badge": "BHRUHADRUPI",
                "cover_image": "assets/images/portfolio/hp/6.jpg",
                "thumbnail_image": "assets/images/portfolio/hp/6.jpg",
                "banner_image": "/assets/portfolio_page/temple/portfolio-banners.png",
                "approach_image": "/assets/portfolio_page/temple/postfolio-about.png",
                "approach": "We crafted a spiritual and cultural preservation narrative that documents sacred temple architecture.",
                "middle_banner_image": "/assets/portfolio_page/temple/portfolio-works.png",
                "gallery_images": "[]",
                "short_desc": "Sacred architecture documentation, commemorative coffee table book, and cultural preservation.",
                "full_desc": "Sacred architecture documentation, commemorative coffee table book, and cultural preservation.",
                "quote": "Preserving sacred tradition while ensuring modern accessibility is a delicate balance. The studio handled our narrative with immense respect, creating a visual identity that is both timeless and resonant.",
                "year": "2025",
                "project_url": "6_temple.html",
                "is_featured": 1,
                "status": "published",
                "created_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            },
            {
                "id": 4,
                "title": "Fishland",
                "slug": "fishland",
                "client": "Fishland",
                "category": "Retail & Environmental Branding",
                "badge": "FISHLAND",
                "cover_image": "assets/images/portfolio/hp/7.jpg",
                "thumbnail_image": "assets/images/portfolio/hp/7.jpg",
                "banner_image": "/assets/portfolio_page/fishland/portfolio-banners.png",
                "approach_image": "/assets/portfolio_page/fishland/postfolio-about.png",
                "approach": "We positioned Fishland with bold, clean compositions and vibrant storytelling.",
                "middle_banner_image": "/assets/portfolio_page/fishland/portfolio-works.png",
                "gallery_images": "[]",
                "short_desc": "Coastal culinary branding, retail store graphics, and fresh seafood packaging.",
                "full_desc": "Coastal culinary branding, retail store graphics, and fresh seafood packaging.",
                "quote": "They helped us cut through a crowded market by finding our unique 'signal.' Our brand now speaks with a clarity and consistency that has significantly improved our customer trust and recall.",
                "year": "2025",
                "project_url": "5_fishland.html",
                "is_featured": 1,
                "status": "published",
                "created_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            },
            {
                "id": 5,
                "title": "SBL Farms",
                "slug": "sbl-farms",
                "client": "SBL-Farms",
                "category": "Sustainable Agri-Branding",
                "badge": "SBL-FARMS",
                "cover_image": "assets/images/portfolio/hp/1.jpg",
                "thumbnail_image": "assets/images/portfolio/hp/1.jpg",
                "banner_image": "/assets/portfolio_page/sbl_farm/portfolio-banners.png",
                "approach_image": "/assets/portfolio_page/sbl_farm/postfolio-about.png",
                "approach": "We articulated the heritage of our land and connected farm-to-table ethos with modern consumers.",
                "middle_banner_image": "/assets/portfolio_page/sbl_farm/portfolio-works.png",
                "gallery_images": "[]",
                "short_desc": "Organic farming branding, farm-gate packaging, and environmental storytelling.",
                "full_desc": "Organic farming branding, farm-gate packaging, and environmental storytelling.",
                "quote": "Story Works Studio didn't just design our packaging; they articulated the heritage of our land. They transformed our agricultural roots into a sophisticated brand that commands a premium market position.",
                "year": "2025",
                "project_url": "8_farms.html",
                "is_featured": 1,
                "status": "published",
                "created_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            },
            {
                "id": 6,
                "title": "Achuthan Publications",
                "slug": "achuthan-publications",
                "client": "Achuthan",
                "category": "Editorial & Book Design",
                "badge": "ACHUTHAN PUBLICATIONS",
                "cover_image": "assets/images/portfolio/hp/9.jpg",
                "thumbnail_image": "assets/images/portfolio/hp/9.jpg",
                "banner_image": "/assets/portfolio_page/books/portfolio-banners.png",
                "approach_image": "/assets/portfolio_page/books/postfolio-about.png",
                "approach": "We crafted an authoritative presence celebrating literature, typography and scholarship.",
                "middle_banner_image": "/assets/portfolio_page/books/portfolio-works.png",
                "gallery_images": "[]",
                "short_desc": "Fine typography, custom book covers, and artisanal print binding.",
                "full_desc": "Fine typography, custom book covers, and artisanal print binding.",
                "quote": "Working with Story Works Studio was an exercise in precision. They took decades of published history and distilled it into a cohesive, modern framework without losing our original soul.",
                "year": "2025",
                "project_url": "9_book.html",
                "is_featured": 1,
                "status": "published",
                "created_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            },
            {
                "id": 7,
                "title": "SBL Foods",
                "slug": "sbl-foods",
                "client": "SBL-Foods",
                "category": "FMCG Brand Architecture",
                "badge": "SBL-FOODS",
                "cover_image": "assets/images/portfolio/hp/11.jpg",
                "thumbnail_image": "assets/images/portfolio/hp/11.jpg",
                "banner_image": "/assets/portfolio_page/sbl_food/portfolio-banners.png",
                "approach_image": "/assets/portfolio_page/sbl_food/postfolio-about.png",
                "approach": "We helped position SBL Food as an emotion-led household brand celebrating purity and culinary heritage.",
                "middle_banner_image": "/assets/portfolio_page/sbl_food/portfolio-works.png",
                "gallery_images": "[]",
                "short_desc": "Multi-category FMCG packaging suite and corporate brand architecture.",
                "full_desc": "Multi-category FMCG packaging suite and corporate brand architecture.",
                "quote": "Story Works Studio didn't just design our packaging; they articulated the heritage of our land. They transformed our agricultural roots into a sophisticated brand that commands a premium market position.",
                "year": "2026",
                "project_url": "7_sblfood.html",
                "is_featured": 1,
                "status": "published",
                "created_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            },
            {
                "id": 8,
                "title": "Bship",
                "slug": "bship",
                "client": "Bship",
                "category": "Corporate Digital Identity",
                "badge": "BSHIP",
                "cover_image": "assets/images/portfolio/hp/8.jpg",
                "thumbnail_image": "assets/images/portfolio/hp/8.jpg",
                "banner_image": "/assets/portfolio_page/bship/bshipbnr.png",
                "approach_image": "/assets/portfolio_page/bship/postfolio-about.png",
                "approach": "We positioned BShip with clear structured communication reflecting logistics reliability.",
                "middle_banner_image": "/assets/portfolio_page/bship/portfolio-works.png",
                "gallery_images": "[]",
                "short_desc": "High-impact visual identity and interactive web experience for freight & maritime operations.",
                "full_desc": "High-impact visual identity and interactive web experience for freight & maritime operations.",
                "quote": "Launch strategy is where this studio truly shines. They orchestrated our market entry with surgical precision, ensuring our brand was not just seen, but immediately understood by our audience.",
                "year": "2026",
                "project_url": "4_bship.html",
                "is_featured": 1,
                "status": "published",
                "created_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            },
            {
                "id": 9,
                "title": "PickleJar",
                "slug": "picklejar",
                "client": "PickleJar",
                "category": "Packaging & Art Direction",
                "badge": "PICKLEJAR",
                "cover_image": "assets/images/portfolio/hp/10.jpg",
                "thumbnail_image": "assets/images/portfolio/hp/10.jpg",
                "banner_image": "/assets/portfolio_page/picklejar/portfolio-banners.png",
                "approach_image": "/assets/portfolio_page/picklejar/postfolio-about.png",
                "approach": "We built a warm visual identity bringing out the richness and nostalgia of homemade flavours.",
                "middle_banner_image": "/assets/portfolio_page/picklejar/portfolio_bnr.png",
                "gallery_images": "[]",
                "short_desc": "Nostalgic culinary roots reimagined with vibrant modern shelf appeal.",
                "full_desc": "Nostalgic culinary roots reimagined with vibrant modern shelf appeal.",
                "quote": "Launch strategy is where this studio truly shines. They orchestrated our market entry with surgical precision, ensuring our brand was not just seen, but immediately understood by our audience.",
                "year": "2025",
                "project_url": "3_picklejar.html",
                "is_featured": 1,
                "status": "published",
                "created_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            }
        ]
        db.portfolio.insert_many(initial_portfolios)
        db.counters.update_one({"_id": "portfolio_id"}, {"$set": {"seq": 9}}, upsert=True)

    # 6. Seed default services if empty
    if db.services.count_documents({}) == 0:
        standard_services = [
            {"id": 1, "title": "Brand Strategy", "slug": "brand-strategy", "short_desc": "We move beyond aesthetics to architect the strategic soul of your business. By synthesizing market intelligence with intuition, we build the narrative frameworks that drive your brand’s future.", "full_desc": "We move beyond aesthetics to architect the strategic soul of your business. By synthesizing market intelligence with intuition, we build the narrative frameworks that drive your brand’s future.", "icon": "fas fa-chart-line", "display_order": 1, "is_active": 1, "created_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S")},
            {"id": 2, "title": "Brand Identity & Design", "slug": "brand-identity-design", "short_desc": "We craft visual legacies through intentional design, from signature logos to multi-sensory systems. Every touchpoint is engineered for flawless consistency, creating a timeless invitation into your brand’s world.", "full_desc": "We craft visual legacies through intentional design, from signature logos to multi-sensory systems. Every touchpoint is engineered for flawless consistency, creating a timeless invitation into your brand’s world.", "icon": "fas fa-search", "display_order": 2, "is_active": 1, "created_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S")},
            {"id": 3, "title": "Content & Copywriting", "slug": "content-copywriting", "short_desc": "Our narratives do more than fill space; they command attention and build lasting rapport. We translate complex value propositions into persuasive human stories that sell a philosophy, not just a product.", "full_desc": "Our narratives do more than fill space; they command attention and build lasting rapport. We translate complex value propositions into persuasive human stories that sell a philosophy, not just a product.", "icon": "fas fa-thumbs-up", "display_order": 3, "is_active": 1, "created_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S")},
            {"id": 4, "title": "Digital Marketing", "slug": "digital-marketing", "short_desc": "Our approach integrates high-intent SEO and strategic social storytelling into performance-driven ecosystems that grow your community and your revenue in equal measure.", "full_desc": "Our approach integrates high-intent SEO and strategic social storytelling into performance-driven ecosystems that grow your community and your revenue in equal measure.", "icon": "fab fa-google", "display_order": 4, "is_active": 1, "created_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S")},
            {"id": 5, "title": "Web & Experience Design", "slug": "web-experience-design", "short_desc": "We view the digital interface as a premier storefront. Our team designs high-conversion digital environments where elegant minimalism meets functional rigor, ensuring every click feels intuitive and every interaction reinforces trust.", "full_desc": "We view the digital interface as a premier storefront. Our team designs high-conversion digital environments where elegant minimalism meets functional rigor, ensuring every click feels intuitive and every interaction reinforces trust.", "icon": "fas fa-laptop-code", "display_order": 5, "is_active": 1, "created_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S")},
            {"id": 6, "title": "Launch & Campaign Strategy", "slug": "launch-campaign-strategy", "short_desc": "We transform entries into arrivals through strategic blueprints and high-impact storytelling. By orchestrating the pivotal moments where brands meet the world, we ensure your debut is both seen and felt.", "full_desc": "We transform entries into arrivals through strategic blueprints and high-impact storytelling. By orchestrating the pivotal moments where brands meet the world, we ensure your debut is both seen and felt.", "icon": "fas fa-code", "display_order": 6, "is_active": 1, "created_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S")},
        ]
        db.services.insert_many(standard_services)
        db.counters.update_one({"_id": "service_id"}, {"$set": {"seq": 6}}, upsert=True)

    # 7. Seed default blogs if empty
    if db.blogs.count_documents({}) == 0:
        default_blogs = [
            {"id": 1, "title": "Dominate the Namma Bengaluru Market: A Local SEO Guide for Local Businesses", "slug": "dominate-namma-bengaluru-market-local-seo", "category": "Local SEO", "author": "Storyworks Studio", "published_date": "FEB 19, 2026", "cover_image": "/assets/blogs/a1.jpg", "excerpt": "If your business is not showing up when someone searches for your service in Bengaluru, you are losing customers in real time.", "content": "If your business is not showing up when someone searches for your service in Bengaluru, you are losing customers in real time. Every day, potential buyers are searching for exactly what you offer.", "status": "published", "views": 0, "created_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S"), "updated_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S")},
            {"id": 2, "title": "Stop Buying Likes & Start Driving Sales: The ROI-First Social Media Strategy", "slug": "stop-buying-likes-start-driving-sales", "category": "Performance Marketing", "author": "Storyworks Studio", "published_date": "FEB 25, 2026", "cover_image": "/assets/blogs/b1.jpg", "excerpt": "Most businesses put money into social media with the hope that being seen will lead to sales, but in reality, a lot of marketing spend goes to waste without an ROI-driven architecture.", "content": "Most businesses put money into social media with the hope that being seen will lead to sales, but in reality, a lot of vanity metrics distract from what actually moves the needle.", "status": "published", "views": 0, "created_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S"), "updated_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S")},
            {"id": 3, "title": "Why Your Beautiful Website Is Losing Customers (And How to Fix It)", "slug": "why-your-website-is-losing-customers", "category": "Web Design & CRO", "author": "Storyworks Studio", "published_date": "MAR 07, 2026", "cover_image": "/assets/blogs/c1.jpg", "excerpt": "A well-designed website can make a strong first impression, but design alone doesn't guarantee sales.", "content": "A well-designed website can make a strong first impression, but design alone doesn't guarantee sales. Here is why pretty websites fail and how conversion architecture solves it.", "status": "published", "views": 0, "created_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S"), "updated_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S")},
            {"id": 4, "title": "In-House Marketing vs Hiring a Bangalore Agency: What’s the Real Cost?", "slug": "in-house-marketing-vs-hiring-agency-cost", "category": "Strategy & Scaling", "author": "Storyworks Studio", "published_date": "MAR 16, 2026", "cover_image": "/assets/blogs/d1.jpg", "excerpt": "The choice between creating an internal marketing team and outsourcing to an external agency is frequently presented as a matter of comparing costs.", "content": "The choice between creating an internal marketing team and outsourcing to an external agency is frequently presented as a matter of comparing costs. For a founder, though the true issue isn't how much you spend, it's the return you receive for it.", "status": "published", "views": 0, "created_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S"), "updated_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S")},
            {"id": 5, "title": "The 2026 Digital Marketing Playbook for Bangalore SMEs: What Actually Works", "slug": "digital-marketing-playbook-bangalore-smes", "category": "Digital Growth", "author": "Storyworks Studio", "published_date": "MAR 20, 2026", "cover_image": "/assets/blogs/e1.jpg", "excerpt": "Digital marketing has advanced to the stage where fragmented initiatives no longer yield significant outcomes.", "content": "Digital marketing has advanced to the stage where fragmented initiatives no longer yield significant outcomes. For small and medium-sized enterprises in Bengaluru, the issue is not an absence of avenues but rather clarity on what truly fuels expansion.", "status": "published", "views": 0, "created_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S"), "updated_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S")},
            {"id": 6, "title": "Why Most Businesses Struggle With Marketing Even After Spending on It", "slug": "why-businesses-struggle-with-marketing", "category": "Marketing Strategy", "author": "Storyworks Studio", "published_date": "MAR 26, 2026", "cover_image": "/assets/blogs/f1.jpg", "excerpt": "Building a brand today comes with far more challenges than just creating a product and putting it online.", "content": "Building a brand today comes with far more challenges than just creating a product and putting it online. The absence of a suitable marketing framework is one of the most serious difficulties companies confront.", "status": "published", "views": 0, "created_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S"), "updated_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S")},
        ]
        db.blogs.insert_many(default_blogs)
        db.counters.update_one({"_id": "blog_id"}, {"$set": {"seq": 6}}, upsert=True)

    print("[*] MongoDB Atlas database initialized successfully.")
