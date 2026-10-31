import json
import re
from datetime import datetime, timedelta
from bson import ObjectId
import pymongo
from werkzeug.security import check_password_hash, generate_password_hash
from app.database import get_db, get_next_sequence_value, to_query_id, serialize_doc


def slugify(text: str) -> str:
    """Convert text to URL-friendly slug."""
    text = text.lower().strip()
    text = re.sub(r"[^\w\s-]", "", text)
    text = re.sub(r"[\s_-]+", "-", text)
    return text.strip("-")


class User:
    @staticmethod
    def get_by_id(user_id):
        db = get_db()
        doc = db.users.find_one(to_query_id(user_id))
        return serialize_doc(doc)

    @staticmethod
    def get_by_username(username):
        db = get_db()
        u = (username or "").strip()
        doc = db.users.find_one({
            "$or": [
                {"username": u},
                {"email": u.lower()}
            ]
        })
        return serialize_doc(doc)

    @staticmethod
    def get_by_email(email):
        db = get_db()
        e = (email or "").strip().lower()
        doc = db.users.find_one({"email": e})
        return serialize_doc(doc)

    @staticmethod
    def create(username, email, password, role="client", full_name="", company="", phone=""):
        db = get_db()
        user_id = get_next_sequence_value("user_id")
        hashed = generate_password_hash(password)
        doc = {
            "id": user_id,
            "username": username.strip(),
            "email": email.strip().lower(),
            "password_hash": hashed,
            "role": role,
            "full_name": full_name.strip(),
            "company": company.strip(),
            "phone": phone.strip(),
            "created_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "last_login": None,
        }
        db.users.insert_one(doc)
        return user_id

    @staticmethod
    def update_client_profile(user_id, full_name, company, phone):
        db = get_db()
        db.users.update_one(
            to_query_id(user_id),
            {"$set": {
                "full_name": full_name.strip(),
                "company": company.strip(),
                "phone": phone.strip()
            }}
        )

    @staticmethod
    def verify_password(stored_hash, password):
        return check_password_hash(stored_hash, password)

    @staticmethod
    def update_password(user_id, new_password):
        db = get_db()
        hashed = generate_password_hash(new_password)
        db.users.update_one(to_query_id(user_id), {"$set": {"password_hash": hashed}})

    @staticmethod
    def update_profile(user_id, username, email):
        db = get_db()
        db.users.update_one(
            to_query_id(user_id),
            {"$set": {"username": username.strip(), "email": email.strip().lower()}}
        )

    @staticmethod
    def record_login(user_id):
        db = get_db()
        now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        db.users.update_one(to_query_id(user_id), {"$set": {"last_login": now}})


class Inquiry:
    @staticmethod
    def create(data):
        db = get_db()
        timeline = (data.get("timeline") or "").strip()
        msg = data.get("message", "") or ""
        if not timeline and "[Target Timeline:" in msg:
            m = re.search(r"\[Target Timeline:\s*([^\]]+)\]", msg)
            if m:
                timeline = m.group(1).strip()

        now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        new_id = get_next_sequence_value("inquiry_id")

        raw_uid = data.get("user_id")
        uid = int(raw_uid) if raw_uid is not None and str(raw_uid).isdigit() else raw_uid

        doc = {
            "id": new_id,
            "user_id": uid,
            "first_name": (data.get("first_name") or "").strip(),
            "last_name": (data.get("last_name") or "").strip(),
            "email": (data.get("email") or "").strip(),
            "phone": (data.get("phone") or "").strip(),
            "company": (data.get("company") or "").strip(),
            "budget": (data.get("budget") or "").strip(),
            "timeline": timeline,
            "services": data.get("services", "") or "",
            "message": msg.strip(),
            "status": "new",
            "notes": "",
            "ip_address": data.get("ip_address", "") or "",
            "created_at": now,
            "updated_at": now,
        }
        db.inquiries.insert_one(doc)
        return new_id

    @staticmethod
    def get_for_client(user_id, email=None):
        db = get_db()
        conds = []
        if user_id is not None:
            conds.append({"user_id": user_id})
            if str(user_id).isdigit():
                conds.append({"user_id": int(user_id)})
                conds.append({"user_id": str(user_id)})
        if email:
            clean_email = email.strip()
            conds.append({"email": {"$regex": f"^{re.escape(clean_email)}$", "$options": "i"}})

        q = {"$or": conds} if conds else {}
        docs = list(db.inquiries.find(q).sort("id", pymongo.DESCENDING))
        return [serialize_doc(d) for d in docs]

    @staticmethod
    def get_client_stats(user_id, email=None):
        inquiries = Inquiry.get_for_client(user_id, email)
        total = len(inquiries)
        new_count = sum(1 for i in inquiries if i.get("status") == "new")
        in_progress = sum(1 for i in inquiries if i.get("status") in ("in_progress", "contacted"))
        completed = sum(1 for i in inquiries if i.get("status") in ("closed", "completed"))
        return {
            "total": total,
            "new": new_count,
            "in_progress": in_progress,
            "completed": completed,
        }

    @staticmethod
    def get_all(status=None, search=None, date_from=None, date_to=None):
        db = get_db()
        q = {}
        if status and status != "all":
            q["status"] = status

        if search:
            s_param = re.escape(search.strip())
            s_regex = {"$regex": s_param, "$options": "i"}
            q["$or"] = [
                {"first_name": s_regex},
                {"last_name": s_regex},
                {"email": s_regex},
                {"company": s_regex},
                {"phone": s_regex},
                {"services": s_regex},
            ]

        if date_from:
            q.setdefault("created_at", {})["$gte"] = str(date_from)
        if date_to:
            q.setdefault("created_at", {})["$lte"] = f"{date_to} 23:59:59"

        docs = list(db.inquiries.find(q).sort("id", pymongo.DESCENDING))
        users_cache = {u["id"]: u for u in [serialize_doc(x) for x in db.users.find({})]}

        result = []
        for d in docs:
            item = serialize_doc(d)
            uid = item.get("user_id")
            client_user = users_cache.get(uid) or users_cache.get(int(uid) if str(uid).isdigit() else None)
            if client_user:
                item["client_username"] = client_user.get("username")
                item["client_full_name"] = client_user.get("full_name")
                item["client_company"] = client_user.get("company")
                item["client_phone"] = client_user.get("phone")
                item["client_created_at"] = client_user.get("created_at")
                item["client_last_login"] = client_user.get("last_login")
            else:
                item["client_username"] = None
                item["client_full_name"] = None
                item["client_company"] = None
                item["client_phone"] = None
                item["client_created_at"] = None
                item["client_last_login"] = None
            result.append(item)
        return result

    @staticmethod
    def get_by_id(inquiry_id):
        db = get_db()
        doc = db.inquiries.find_one(to_query_id(inquiry_id))
        if not doc:
            return None
        item = serialize_doc(doc)
        uid = item.get("user_id")
        if uid:
            client_user = User.get_by_id(uid)
            if client_user:
                item["client_username"] = client_user.get("username")
                item["client_full_name"] = client_user.get("full_name")
                item["client_company"] = client_user.get("company")
                item["client_phone"] = client_user.get("phone")
                item["client_created_at"] = client_user.get("created_at")
                item["client_last_login"] = client_user.get("last_login")
        return item

    @staticmethod
    def update_status(inquiry_id, status):
        db = get_db()
        now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        db.inquiries.update_one(to_query_id(inquiry_id), {"$set": {"status": status, "updated_at": now}})

    @staticmethod
    def update_notes(inquiry_id, notes):
        db = get_db()
        now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        db.inquiries.update_one(to_query_id(inquiry_id), {"$set": {"notes": notes, "updated_at": now}})

    @staticmethod
    def delete(inquiry_id):
        db = get_db()
        db.inquiries.delete_one(to_query_id(inquiry_id))

    @staticmethod
    def delete_all():
        db = get_db()
        db.inquiries.delete_many({})
        db.counters.update_one({"_id": "inquiry_id"}, {"$set": {"seq": 0}}, upsert=True)

    @staticmethod
    def get_stats():
        db = get_db()
        total = db.inquiries.count_documents({})
        new_count = db.inquiries.count_documents({"status": "new"})
        contacted = db.inquiries.count_documents({"status": "contacted"})
        in_progress = db.inquiries.count_documents({"status": "in_progress"})
        closed = db.inquiries.count_documents({"status": "closed"})
        not_interested = db.inquiries.count_documents({"status": "not_interested"})
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
        db = get_db()
        q = {"status": status} if status else {}
        docs = list(db.blogs.find(q).sort("id", pymongo.DESCENDING))
        return [serialize_doc(d) for d in docs]

    @staticmethod
    def get_by_id(blog_id):
        db = get_db()
        doc = db.blogs.find_one(to_query_id(blog_id))
        return serialize_doc(doc)

    @staticmethod
    def get_by_slug(slug):
        db = get_db()
        doc = db.blogs.find_one({"slug": slug})
        return serialize_doc(doc)

    @staticmethod
    def create(data):
        db = get_db()
        slug = data.get("slug") or slugify(data.get("title", ""))
        base_slug = slug
        counter = 1
        while db.blogs.find_one({"slug": slug}):
            slug = f"{base_slug}-{counter}"
            counter += 1

        new_id = get_next_sequence_value("blog_id")
        doc = {
            "id": new_id,
            "title": data.get("title"),
            "slug": slug,
            "category": data.get("category", "Blog"),
            "author": data.get("author", "Storyworks Studio"),
            "published_date": data.get("published_date") or datetime.now().strftime("%b %d, %Y"),
            "cover_image": data.get("cover_image", "") or "",
            "excerpt": data.get("excerpt", "") or "",
            "content": data.get("content", "") or "",
            "status": data.get("status", "published"),
            "views": 0,
            "created_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "updated_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        }
        db.blogs.insert_one(doc)
        return new_id

    @staticmethod
    def update(blog_id, data):
        db = get_db()
        now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        slug = data.get("slug") or slugify(data.get("title", ""))
        fields = {
            "title": data.get("title"),
            "slug": slug,
            "category": data.get("category", "Blog"),
            "author": data.get("author", "Storyworks Studio"),
            "published_date": data.get("published_date"),
            "cover_image": data.get("cover_image"),
            "excerpt": data.get("excerpt"),
            "content": data.get("content"),
            "status": data.get("status", "published"),
            "updated_at": now,
        }
        db.blogs.update_one(to_query_id(blog_id), {"$set": fields})

    @staticmethod
    def delete(blog_id):
        db = get_db()
        db.blogs.delete_one(to_query_id(blog_id))

    @staticmethod
    def increment_views(blog_id):
        db = get_db()
        db.blogs.update_one(to_query_id(blog_id), {"$inc": {"views": 1}})


class Portfolio:
    @staticmethod
    def get_all(category=None, status=None):
        db = get_db()
        q = {}
        if status:
            q["status"] = status
        if category and category != "all":
            q["category"] = category
        docs = list(db.portfolio.find(q).sort("id", pymongo.ASCENDING))
        return [serialize_doc(d) for d in docs]

    @staticmethod
    def get_by_id(item_id):
        db = get_db()
        doc = db.portfolio.find_one(to_query_id(item_id))
        return serialize_doc(doc)

    @staticmethod
    def get_by_slug(slug):
        db = get_db()
        doc = db.portfolio.find_one({"slug": slug})
        return serialize_doc(doc)

    @staticmethod
    def get_by_project_url(url):
        db = get_db()
        clean_url = url.split("?")[0].lstrip("/")
        doc = db.portfolio.find_one({
            "$or": [
                {"project_url": clean_url},
                {"project_url": "/" + clean_url},
                {"slug": clean_url}
            ]
        })
        return serialize_doc(doc)

    @staticmethod
    def create(data):
        db = get_db()
        slug = data.get("slug") or slugify(data.get("title", ""))
        base_slug = slug
        counter = 1
        while db.portfolio.find_one({"slug": slug}):
            slug = f"{base_slug}-{counter}"
            counter += 1

        thumbnail_image = (data.get("thumbnail_image") or data.get("cover_image") or "").strip()
        cover_image = (data.get("cover_image") or thumbnail_image).strip()
        banner_image = (data.get("banner_image") or "").strip()
        approach_image = (data.get("approach_image") or "").strip()
        approach = (data.get("approach") or "").strip()
        middle_banner_image = (data.get("middle_banner_image") or "").strip()

        new_id = get_next_sequence_value("portfolio_id")
        doc = {
            "id": new_id,
            "title": data.get("title"),
            "slug": slug,
            "client": data.get("client", "") or "",
            "category": data.get("category", "") or "",
            "badge": data.get("badge", "") or "",
            "cover_image": cover_image,
            "thumbnail_image": thumbnail_image,
            "banner_image": banner_image,
            "approach_image": approach_image,
            "approach": approach,
            "middle_banner_image": middle_banner_image,
            "gallery_images": data.get("gallery_images", "[]"),
            "short_desc": data.get("short_desc", "") or "",
            "full_desc": data.get("full_desc", "") or "",
            "quote": data.get("quote", "") or "",
            "year": data.get("year", "2026"),
            "project_url": data.get("project_url", "") or "",
            "is_featured": 1 if data.get("is_featured") else 0,
            "status": data.get("status", "published"),
            "created_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        }
        db.portfolio.insert_one(doc)
        return new_id

    @staticmethod
    def update(item_id, data):
        db = get_db()
        slug = data.get("slug") or slugify(data.get("title", ""))
        thumbnail_image = (data.get("thumbnail_image") or data.get("cover_image") or "").strip()
        cover_image = (data.get("cover_image") or thumbnail_image).strip()
        banner_image = (data.get("banner_image") or "").strip()
        approach_image = (data.get("approach_image") or "").strip()
        approach = (data.get("approach") or "").strip()
        middle_banner_image = (data.get("middle_banner_image") or "").strip()

        fields = {
            "title": data.get("title"),
            "slug": slug,
            "client": data.get("client"),
            "category": data.get("category"),
            "badge": data.get("badge"),
            "cover_image": cover_image,
            "thumbnail_image": thumbnail_image,
            "banner_image": banner_image,
            "approach_image": approach_image,
            "approach": approach,
            "middle_banner_image": middle_banner_image,
            "gallery_images": data.get("gallery_images", "[]"),
            "short_desc": data.get("short_desc"),
            "full_desc": data.get("full_desc"),
            "quote": data.get("quote"),
            "year": data.get("year"),
            "project_url": data.get("project_url"),
            "is_featured": 1 if data.get("is_featured") else 0,
            "status": data.get("status", "published"),
        }
        db.portfolio.update_one(to_query_id(item_id), {"$set": fields})

    @staticmethod
    def delete(item_id):
        db = get_db()
        db.portfolio.delete_one(to_query_id(item_id))


class Service:
    @staticmethod
    def get_all(only_active=False):
        db = get_db()
        q = {"is_active": 1} if only_active else {}
        docs = list(db.services.find(q).sort([("display_order", pymongo.ASCENDING), ("id", pymongo.ASCENDING)]))
        return [serialize_doc(d) for d in docs]

    @staticmethod
    def get_by_id(service_id):
        db = get_db()
        doc = db.services.find_one(to_query_id(service_id))
        return serialize_doc(doc)

    @staticmethod
    def create(data):
        db = get_db()
        slug = data.get("slug") or slugify(data.get("title", ""))
        new_id = get_next_sequence_value("service_id")
        doc = {
            "id": new_id,
            "title": data.get("title"),
            "slug": slug,
            "short_desc": data.get("short_desc", "") or "",
            "full_desc": data.get("full_desc", "") or "",
            "icon": data.get("icon", "") or "",
            "display_order": int(data.get("display_order", 0)),
            "is_active": 1 if data.get("is_active", 1) else 0,
            "created_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        }
        db.services.insert_one(doc)
        return new_id

    @staticmethod
    def update(service_id, data):
        db = get_db()
        slug = data.get("slug") or slugify(data.get("title", ""))
        fields = {
            "title": data.get("title"),
            "slug": slug,
            "short_desc": data.get("short_desc"),
            "full_desc": data.get("full_desc"),
            "icon": data.get("icon"),
            "display_order": int(data.get("display_order", 0)),
            "is_active": 1 if data.get("is_active", 1) else 0,
        }
        db.services.update_one(to_query_id(service_id), {"$set": fields})

    @staticmethod
    def delete(service_id):
        db = get_db()
        db.services.delete_one(to_query_id(service_id))


class Setting:
    @staticmethod
    def get_all_dict():
        try:
            db = get_db()
            docs = list(db.settings.find({}))
            return {d["key"]: d.get("value", "") for d in docs}
        except Exception:
            return {}

    @staticmethod
    def get(key, default=""):
        try:
            db = get_db()
            doc = db.settings.find_one({"key": key})
            return doc.get("value", default) if doc else default
        except Exception:
            return default

    @staticmethod
    def set(key, value, category="general"):
        db = get_db()
        db.settings.update_one(
            {"key": key},
            {"$set": {"key": key, "value": value, "category": category}},
            upsert=True
        )


class Subscriber:
    @staticmethod
    def add(email):
        db = get_db()
        clean = (email or "").strip().lower()
        if not clean:
            return False
        try:
            sub_id = get_next_sequence_value("subscriber_id")
            db.subscribers.update_one(
                {"email": clean},
                {"$setOnInsert": {
                    "id": sub_id,
                    "email": clean,
                    "created_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                }},
                upsert=True
            )
            return True
        except Exception:
            return False

    @staticmethod
    def get_all():
        db = get_db()
        docs = list(db.subscribers.find({}).sort("id", pymongo.DESCENDING))
        return [serialize_doc(d) for d in docs]

    @staticmethod
    def delete(sub_id):
        db = get_db()
        db.subscribers.delete_one(to_query_id(sub_id))


class LoginHistory:
    """Admin-portal and client-portal logins are kept in separate collections,
    each with its own id sequence. `portal` is "admin" or "client"."""

    COLLECTIONS = {"admin": "admin_login_history", "client": "client_login_history"}

    @staticmethod
    def collection_name(portal):
        return LoginHistory.COLLECTIONS["admin" if portal == "admin" else "client"]

    @staticmethod
    def record_login(user, portal, ip_address="", user_agent=""):
        db = get_db()
        name = LoginHistory.collection_name(portal)
        new_id = get_next_sequence_value(f"{name}_id")
        doc = {
            "id": new_id,
            "user_id": user.get("id"),
            "username": user.get("username", ""),
            "role": user.get("role", ""),
            "login_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "logout_at": None,
            "ip_address": ip_address or "",
            "user_agent": user_agent or "",
        }
        db[name].insert_one(doc)
        return new_id

    @staticmethod
    def record_logout(entry_id, portal):
        db = get_db()
        now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        db[LoginHistory.collection_name(portal)].update_one(to_query_id(entry_id), {"$set": {"logout_at": now}})

    @staticmethod
    def get_all(portal=None, limit=200):
        """Entries for one portal, or (portal=None) both collections merged newest first."""
        db = get_db()
        names = [LoginHistory.collection_name(portal)] if portal else list(LoginHistory.COLLECTIONS.values())
        docs = []
        for name in names:
            docs.extend(db[name].find({}).sort("login_at", pymongo.DESCENDING).limit(limit))
        docs.sort(key=lambda d: d.get("login_at") or "", reverse=True)
        return [serialize_doc(d) for d in docs[:limit]]


class PasswordReset:
    """One pending OTP per user. The OTP itself is never stored, only its hash."""

    @staticmethod
    def create(user_id, otp, expiry_minutes):
        db = get_db()
        now = datetime.now()
        db.password_resets.delete_many({"user_id": user_id})
        db.password_resets.insert_one({
            "user_id": user_id,
            "otp_hash": generate_password_hash(otp),
            "attempts": 0,
            "sent_at": now,
            "expires_at": now + timedelta(minutes=expiry_minutes),
        })

    @staticmethod
    def seconds_since_sent(user_id):
        db = get_db()
        doc = db.password_resets.find_one({"user_id": user_id})
        return (datetime.now() - doc["sent_at"]).total_seconds() if doc else None

    @staticmethod
    def verify(user_id, otp, max_attempts):
        """Return "ok", "invalid", "expired" or "locked"."""
        db = get_db()
        doc = db.password_resets.find_one({"user_id": user_id})
        if not doc:
            return "expired"
        if datetime.now() > doc["expires_at"]:
            db.password_resets.delete_one({"_id": doc["_id"]})
            return "expired"
        if doc.get("attempts", 0) >= max_attempts:
            return "locked"
        if not check_password_hash(doc["otp_hash"], otp):
            db.password_resets.update_one({"_id": doc["_id"]}, {"$inc": {"attempts": 1}})
            return "locked" if doc.get("attempts", 0) + 1 >= max_attempts else "invalid"
        return "ok"

    @staticmethod
    def clear(user_id):
        db = get_db()
        db.password_resets.delete_many({"user_id": user_id})
