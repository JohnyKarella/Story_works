import json
import re
from datetime import datetime
from werkzeug.security import check_password_hash, generate_password_hash
from app.database import get_db
def slugify(text: str) -> str:
    """Convert text to URL-friendly slug."""
    text = text.lower().strip()
    text = re.sub(r"[^\w\s-]", "", text)
    text = re.sub(r"[\s_-]+", "-", text)
    return text.strip("-")
class User:
    @staticmethod
    def get_by_id(user_id):
        conn = get_db()
        user = conn.execute("SELECT * FROM users WHERE id = ?", (user_id,)).fetchone()
        conn.close()
        return dict(user) if user else None
    @staticmethod
    def get_by_username(username):
        conn = get_db()
        user = conn.execute("SELECT * FROM users WHERE username = ? OR email = ?", (username, username)).fetchone()
        conn.close()
        return dict(user) if user else None
    @staticmethod
    def verify_password(stored_hash, password):
        return check_password_hash(stored_hash, password)
    @staticmethod
    def update_password(user_id, new_password):
        conn = get_db()
        hashed = generate_password_hash(new_password)
        conn.execute("UPDATE users SET password_hash = ? WHERE id = ?", (hashed, user_id))
        conn.commit()
        conn.close()
    @staticmethod
    def update_profile(user_id, username, email):
        conn = get_db()
        conn.execute("UPDATE users SET username = ?, email = ? WHERE id = ?", (username, email, user_id))
        conn.commit()
        conn.close()
    @staticmethod
    def record_login(user_id):
        conn = get_db()
        now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        conn.execute("UPDATE users SET last_login = ? WHERE id = ?", (now, user_id))
        conn.commit()
        conn.close()
class Inquiry:
    @staticmethod
    def create(data):
        conn = get_db()
        cursor = conn.cursor()
        cursor.execute(
            """
            INSERT INTO inquiries (first_name, last_name, email, phone, company, budget, services, message, ip_address)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                data.get("first_name", "").strip(),
                data.get("last_name", "").strip(),
                data.get("email", "").strip(),
                data.get("phone", "").strip(),
                data.get("company", "").strip(),
                data.get("budget", "").strip(),
                data.get("services", ""),
                data.get("message", "").strip(),
                data.get("ip_address", ""),
            ),
        )
        new_id = cursor.lastrowid
        conn.commit()
        conn.close()
        return new_id
    @staticmethod
    def get_all(status=None, search=None, date_from=None, date_to=None):
        conn = get_db()
        query = "SELECT * FROM inquiries WHERE 1=1"
        params = []
        if status and status != "all":
            query += " AND status = ?"
            params.append(status)
        if search:
            query += " AND (first_name LIKE ? OR last_name LIKE ? OR email LIKE ? OR company LIKE ? OR phone LIKE ? OR services LIKE ?)"
            s_param = f"%{search}%"
            params.extend([s_param, s_param, s_param, s_param, s_param, s_param])
        if date_from:
            query += " AND DATE(created_at) >= DATE(?)"
            params.append(date_from)
        if date_to:
            query += " AND DATE(created_at) <= DATE(?)"
            params.append(date_to)
        query += " ORDER BY id DESC"
        rows = conn.execute(query, params).fetchall()
        conn.close()
        return [dict(r) for r in rows]
    @staticmethod
    def get_by_id(inquiry_id):
        conn = get_db()
        row = conn.execute("SELECT * FROM inquiries WHERE id = ?", (inquiry_id,)).fetchone()
        conn.close()
        return dict(row) if row else None
    @staticmethod
    def update_status(inquiry_id, status):
        conn = get_db()
        conn.execute("UPDATE inquiries SET status = ? WHERE id = ?", (status, inquiry_id))
        conn.commit()
        conn.close()
    @staticmethod
    def update_notes(inquiry_id, notes):
        conn = get_db()
        conn.execute("UPDATE inquiries SET notes = ? WHERE id = ?", (notes, inquiry_id))
        conn.commit()
        conn.close()
    @staticmethod
    def delete(inquiry_id):
        conn = get_db()
        conn.execute("DELETE FROM inquiries WHERE id = ?", (inquiry_id,))
        conn.commit()
        conn.close()
    @staticmethod
    def delete_all():
        conn = get_db()
        conn.execute("DELETE FROM inquiries")
        try:
            conn.execute("DELETE FROM sqlite_sequence WHERE name = 'inquiries'")
        except Exception:
            pass
        conn.commit()
        conn.close()
    @staticmethod
    def get_stats():
        conn = get_db()
        total = conn.execute("SELECT COUNT(*) FROM inquiries").fetchone()[0]
        new_count = conn.execute("SELECT COUNT(*) FROM inquiries WHERE status = 'new'").fetchone()[0]
        contacted = conn.execute("SELECT COUNT(*) FROM inquiries WHERE status = 'contacted'").fetchone()[0]
        in_progress = conn.execute("SELECT COUNT(*) FROM inquiries WHERE status = 'in_progress'").fetchone()[0]
        closed = conn.execute("SELECT COUNT(*) FROM inquiries WHERE status = 'closed'").fetchone()[0]
        not_interested = conn.execute("SELECT COUNT(*) FROM inquiries WHERE status = 'not_interested'").fetchone()[0]
        conn.close()
        return {
            "total": total,
            "new": new_count,
            "contacted": contacted,
            "in_progress": in_progress,
            "closed": closed,
            "not_interested": not_interested,
        }
class Blog:
    @staticmethod
    def get_all(status=None):
        conn = get_db()
        if status:
            rows = conn.execute("SELECT * FROM blogs WHERE status = ? ORDER BY id DESC", (status,)).fetchall()
        else:
            rows = conn.execute("SELECT * FROM blogs ORDER BY id DESC").fetchall()
        conn.close()
        return [dict(r) for r in rows]
    @staticmethod
    def get_by_id(blog_id):
        conn = get_db()
        row = conn.execute("SELECT * FROM blogs WHERE id = ?", (blog_id,)).fetchone()
        conn.close()
        return dict(row) if row else None
    @staticmethod
    def get_by_slug(slug):
        conn = get_db()
        row = conn.execute("SELECT * FROM blogs WHERE slug = ?", (slug,)).fetchone()
        conn.close()
        return dict(row) if row else None
    @staticmethod
    def create(data):
        conn = get_db()
        cursor = conn.cursor()
        slug = data.get("slug") or slugify(data.get("title", ""))
        # Ensure unique slug
        base_slug = slug
        counter = 1
        while cursor.execute("SELECT id FROM blogs WHERE slug = ?", (slug,)).fetchone():
            slug = f"{base_slug}-{counter}"
            counter += 1
        cursor.execute(
            """
            INSERT INTO blogs (title, slug, category, author, published_date, cover_image, excerpt, content, status)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                data.get("title"),
                slug,
                data.get("category", "Blog"),
                data.get("author", "Storyworks Studio"),
                data.get("published_date", datetime.now().strftime("%b %d, %Y")),
                data.get("cover_image", ""),
                data.get("excerpt", ""),
                data.get("content", ""),
                data.get("status", "published"),
            ),
        )
        new_id = cursor.lastrowid
        conn.commit()
        conn.close()
        return new_id
    @staticmethod
    def update(blog_id, data):
        conn = get_db()
        now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        slug = data.get("slug") or slugify(data.get("title", ""))
        conn.execute(
            """
            UPDATE blogs
            SET title = ?, slug = ?, category = ?, author = ?, published_date = ?, cover_image = ?, excerpt = ?, content = ?, status = ?, updated_at = ?
            WHERE id = ?
            """,
            (
                data.get("title"),
                slug,
                data.get("category", "Blog"),
                data.get("author", "Storyworks Studio"),
                data.get("published_date"),
                data.get("cover_image"),
                data.get("excerpt"),
                data.get("content"),
                data.get("status", "published"),
                now,
                blog_id,
            ),
        )
        conn.commit()
        conn.close()
    @staticmethod
    def delete(blog_id):
        conn = get_db()
        conn.execute("DELETE FROM blogs WHERE id = ?", (blog_id,))
        conn.commit()
        conn.close()
    @staticmethod
    def increment_views(blog_id):
        conn = get_db()
        conn.execute("UPDATE blogs SET views = views + 1 WHERE id = ?", (blog_id,))
        conn.commit()
        conn.close()
class Portfolio:
    @staticmethod
    def get_all(category=None, status=None):
        conn = get_db()
        query = "SELECT * FROM portfolio WHERE 1=1"
        params = []
        if status:
            query += " AND status = ?"
            params.append(status)
        if category and category != "all":
            query += " AND category = ?"
            params.append(category)
        query += " ORDER BY id ASC"
        rows = conn.execute(query, params).fetchall()
        conn.close()
        return [dict(r) for r in rows]
    @staticmethod
    def get_by_id(item_id):
        conn = get_db()
        row = conn.execute("SELECT * FROM portfolio WHERE id = ?", (item_id,)).fetchone()
        conn.close()
        return dict(row) if row else None
    @staticmethod
    def get_by_slug(slug):
        conn = get_db()
        row = conn.execute("SELECT * FROM portfolio WHERE slug = ?", (slug,)).fetchone()
        conn.close()
        return dict(row) if row else None
    @staticmethod
    def create(data):
        conn = get_db()
        cursor = conn.cursor()
        slug = data.get("slug") or slugify(data.get("title", ""))
        base_slug = slug
        counter = 1
        while cursor.execute("SELECT id FROM portfolio WHERE slug = ?", (slug,)).fetchone():
            slug = f"{base_slug}-{counter}"
            counter += 1
        cursor.execute(
            """
            INSERT INTO portfolio (title, slug, client, category, badge, cover_image, gallery_images, short_desc, full_desc, quote, year, project_url, is_featured, status)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                data.get("title"),
                slug,
                data.get("client", ""),
                data.get("category", ""),
                data.get("badge", ""),
                data.get("cover_image", ""),
                data.get("gallery_images", "[]"),
                data.get("short_desc", ""),
                data.get("full_desc", ""),
                data.get("quote", ""),
                data.get("year", "2026"),
                data.get("project_url", ""),
                1 if data.get("is_featured") else 0,
                data.get("status", "published"),
            ),
        )
        new_id = cursor.lastrowid
        conn.commit()
        conn.close()
        return new_id
    @staticmethod
    def update(item_id, data):
        conn = get_db()
        slug = data.get("slug") or slugify(data.get("title", ""))
        conn.execute(
            """
            UPDATE portfolio
            SET title = ?, slug = ?, client = ?, category = ?, badge = ?, cover_image = ?, gallery_images = ?, short_desc = ?, full_desc = ?, quote = ?, year = ?, project_url = ?, is_featured = ?, status = ?
            WHERE id = ?
            """,
            (
                data.get("title"),
                slug,
                data.get("client"),
                data.get("category"),
                data.get("badge"),
                data.get("cover_image"),
                data.get("gallery_images", "[]"),
                data.get("short_desc"),
                data.get("full_desc"),
                data.get("quote"),
                data.get("year"),
                data.get("project_url"),
                1 if data.get("is_featured") else 0,
                data.get("status", "published"),
                item_id,
            ),
        )
        conn.commit()
        conn.close()
    @staticmethod
    def delete(item_id):
        conn = get_db()
        conn.execute("DELETE FROM portfolio WHERE id = ?", (item_id,))
        conn.commit()
        conn.close()
class Service:
    @staticmethod
    def get_all(only_active=False):
        conn = get_db()
        if only_active:
            rows = conn.execute("SELECT * FROM services WHERE is_active = 1 ORDER BY display_order ASC, id ASC").fetchall()
        else:
            rows = conn.execute("SELECT * FROM services ORDER BY display_order ASC, id ASC").fetchall()
        conn.close()
        return [dict(r) for r in rows]
    @staticmethod
    def get_by_id(service_id):
        conn = get_db()
        row = conn.execute("SELECT * FROM services WHERE id = ?", (service_id,)).fetchone()
        conn.close()
        return dict(row) if row else None
    @staticmethod
    def create(data):
        conn = get_db()
        cursor = conn.cursor()
        slug = data.get("slug") or slugify(data.get("title", ""))
        cursor.execute(
            """
            INSERT INTO services (title, slug, short_desc, full_desc, icon, display_order, is_active)
            VALUES (?, ?, ?, ?, ?, ?, ?)
            """,
            (
                data.get("title"),
                slug,
                data.get("short_desc", ""),
                data.get("full_desc", ""),
                data.get("icon", ""),
                int(data.get("display_order", 0)),
                1 if data.get("is_active", 1) else 0,
            ),
        )
        new_id = cursor.lastrowid
        conn.commit()
        conn.close()
        return new_id
    @staticmethod
    def update(service_id, data):
        conn = get_db()
        slug = data.get("slug") or slugify(data.get("title", ""))
        conn.execute(
            """
            UPDATE services
            SET title = ?, slug = ?, short_desc = ?, full_desc = ?, icon = ?, display_order = ?, is_active = ?
            WHERE id = ?
            """,
            (
                data.get("title"),
                slug,
                data.get("short_desc"),
                data.get("full_desc"),
                data.get("icon"),
                int(data.get("display_order", 0)),
                1 if data.get("is_active", 1) else 0,
                service_id,
            ),
        )
        conn.commit()
        conn.close()
    @staticmethod
    def delete(service_id):
        conn = get_db()
        conn.execute("DELETE FROM services WHERE id = ?", (service_id,))
        conn.commit()
        conn.close()
class Setting:
    @staticmethod
    def get_all_dict():
        conn = get_db()
        rows = conn.execute("SELECT key, value FROM settings").fetchall()
        conn.close()
        return {r["key"]: r["value"] for r in rows}
    @staticmethod
    def get(key, default=""):
        conn = get_db()
        row = conn.execute("SELECT value FROM settings WHERE key = ?", (key,)).fetchone()
        conn.close()
        return row["value"] if row else default
    @staticmethod
    def set(key, value, category="general"):
        conn = get_db()
        conn.execute(
            "INSERT INTO settings (key, value, category) VALUES (?, ?, ?) ON CONFLICT(key) DO UPDATE SET value = excluded.value",
            (key, value, category),
        )
        conn.commit()
        conn.close()
class Subscriber:
    @staticmethod
    def add(email):
        conn = get_db()
        try:
            conn.execute("INSERT INTO subscribers (email) VALUES (?)", (email.strip().lower(),))
            conn.commit()
            success = True
        except Exception:
            success = False
        finally:
            conn.close()
        return success
    @staticmethod
    def get_all():
        conn = get_db()
        rows = conn.execute("SELECT * FROM subscribers ORDER BY id DESC").fetchall()
        conn.close()
        return [dict(r) for r in rows]
    @staticmethod
    def delete(sub_id):
        conn = get_db()
        conn.execute("DELETE FROM subscribers WHERE id = ?", (sub_id,))
        conn.commit()
        conn.close()
