import sys
import os
from pathlib import Path

# Add project root to sys.path
BASE_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(BASE_DIR))

from app.database import get_db, init_db
from app.models import Blog, Portfolio, Service, Inquiry, Subscriber, Setting, User

def seed_all():
    print("[*] Initializing MongoDB Atlas database collections and schema...")
    init_db(run_seed=False)
    db = get_db()
    print("[*] Seeding status:")
    print(f"  - Users: {db.users.count_documents({})}")
    print(f"  - Blogs: {db.blogs.count_documents({})}")
    print(f"  - Portfolio: {db.portfolio.count_documents({})}")
    print(f"  - Services: {db.services.count_documents({})}")
    print(f"  - Settings: {db.settings.count_documents({})}")
    print(f"  - Subscribers: {db.subscribers.count_documents({})}")
    print(f"  - Inquiries: {db.inquiries.count_documents({})}")
    print("[*] Seeding completed successfully.")

if __name__ == "__main__":
    seed_all()
