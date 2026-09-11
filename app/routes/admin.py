import os
import csv
import io
from functools import wraps
from datetime import datetime, timedelta
from flask import (
    Blueprint,
    render_template,
    request,
    redirect,
    url_for,
    flash,
    session,
    jsonify,
    Response,
    current_app,
)
from werkzeug.utils import secure_filename
from app.models import User, Inquiry, Blog, Portfolio, Service, Subscriber, Setting
from app.config import Config

admin_bp = Blueprint("admin", __name__, url_prefix="/admin")


def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not session.get("user_id"):
            flash("Please sign in to access the admin panel.", "warning")
            return redirect(url_for("admin.login", next=request.url))
        return f(*args, **kwargs)
    return decorated_function


def allowed_file(filename):
    return "." in filename and filename.rsplit(".", 1)[1].lower() in Config.ALLOWED_EXTENSIONS


# ─────────────────────────────────────────────────────────────
# AUTHENTICATION
# ─────────────────────────────────────────────────────────────

@admin_bp.route("/login", methods=["GET", "POST"], strict_slashes=False)
def login():
    if session.get("user_id"):
        return redirect(url_for("admin.dashboard"))

    if request.method == "POST":
        username = request.form.get("username", "").strip()
        password = request.form.get("password", "")
        remember = bool(request.form.get("remember"))

        user = User.get_by_username(username)
        if user and User.verify_password(user["password_hash"], password):
            session.permanent = remember
            session["user_id"] = user["id"]
            session["username"] = user["username"]
            session["email"] = user["email"]
            session["role"] = user["role"]
            User.record_login(user["id"])
            flash(f"Welcome back, {user['username']}!", "success")
            next_page = request.args.get("next")
            return redirect(next_page or url_for("admin.dashboard"))
        else:
            flash("Invalid username or password. Please try again.", "error")

    return render_template("admin/login.html")


@admin_bp.route("/logout")
def logout():
    session.clear()
    flash("You have been signed out.", "info")
    return redirect(url_for("admin.login"))


# ─────────────────────────────────────────────────────────────
# DASHBOARD
# ─────────────────────────────────────────────────────────────

@admin_bp.route("", strict_slashes=False)
@admin_bp.route("/", strict_slashes=False)
@admin_bp.route("/dashboard", strict_slashes=False)
@login_required
def dashboard():
    inquiry_stats = Inquiry.get_stats()
    recent_inquiries = Inquiry.get_all()[:6]
    blogs = Blog.get_all()
    portfolio_items = Portfolio.get_all()
    subscribers = Subscriber.get_all()
    service_items = Service.get_all()

    stats = {
        "total_inquiries": inquiry_stats["total"],
        "new_inquiries": inquiry_stats["new"],
        "total_blogs": len(blogs),
        "total_portfolio": len(portfolio_items),
        "total_subscribers": len(subscribers),
        "total_services": len(service_items),
    }

    return render_template(
        "admin/dashboard.html",
        stats=stats,
        recent_inquiries=recent_inquiries,
        recent_blogs=blogs,
        recent_portfolio=portfolio_items,
        recent_services=service_items,
        all_blogs=blogs,
        all_portfolio=portfolio_items,
        all_services=service_items,
    )


# ─────────────────────────────────────────────────────────────
# INQUIRIES (LEADS)
# ─────────────────────────────────────────────────────────────

@admin_bp.route("/inquiries")
@login_required
def inquiries():
    status = request.args.get("status", "all")
    search = request.args.get("search", "").strip()
    inquiries_list = Inquiry.get_all(status=status, search=search)
    stats = Inquiry.get_stats()
    return render_template(
        "admin/inquiries.html",
        inquiries=inquiries_list,
        current_status=status,
        search_query=search,
        stats=stats,
    )


@admin_bp.route("/inquiries/<int:inquiry_id>/status", methods=["POST"])
@login_required
def update_inquiry_status(inquiry_id):
    status = request.form.get("status")
    if status in ["new", "contacted", "in_progress", "closed"]:
        Inquiry.update_status(inquiry_id, status)
        if request.headers.get("X-Requested-With") == "XMLHttpRequest":
            return jsonify({"success": True, "status": status})
        flash("Inquiry status updated.", "success")
    return redirect(url_for("admin.inquiries"))


@admin_bp.route("/inquiries/<int:inquiry_id>/notes", methods=["POST"])
@login_required
def update_inquiry_notes(inquiry_id):
    notes = request.form.get("notes", "").strip()
    Inquiry.update_notes(inquiry_id, notes)
    flash("Internal notes updated.", "success")
    return redirect(url_for("admin.inquiries"))


@admin_bp.route("/inquiries/<int:inquiry_id>/delete", methods=["POST"])
@login_required
def delete_inquiry(inquiry_id):
    Inquiry.delete(inquiry_id)
    flash("Inquiry deleted successfully.", "info")
    return redirect(url_for("admin.inquiries"))


@admin_bp.route("/inquiries/delete-all", methods=["POST"])
@login_required
def delete_all_inquiries():
    Inquiry.delete_all()
    flash("All inquiries deleted successfully.", "info")
    return redirect(request.referrer or url_for("admin.dashboard"))


@admin_bp.route("/api/unread-inquiries", methods=["GET"])
@login_required
def api_unread_inquiries():
    """Return count and latest inquiry for real-time admin pop up notifications."""
    inquiries_list = Inquiry.get_all()
    unread_count = sum(1 for item in inquiries_list if item.get("status") == "new")
    latest = inquiries_list[0] if inquiries_list else None
    latest_data = None
    if latest:
        msg = latest.get("message", "")
        latest_data = {
            "id": latest["id"],
            "first_name": latest.get("first_name", ""),
            "last_name": latest.get("last_name", ""),
            "email": latest.get("email", ""),
            "company": latest.get("company", ""),
            "message": (msg[:75] + "…") if len(msg) > 75 else msg,
            "created_at": latest.get("created_at", ""),
            "status": latest.get("status", "new"),
        }
    return jsonify({
        "success": True,
        "unread_count": unread_count,
        "latest": latest_data,
    })


@admin_bp.route("/inquiries/export")
@login_required
def export_inquiries_csv():
    inquiries_list = Inquiry.get_all()
    output = io.StringIO()
    writer = csv.writer(output)
    writer.writerow([
        "ID", "First Name", "Last Name", "Email", "Phone",
        "Company", "Budget", "Services", "Message", "Status", "Notes", "Date"
    ])

    for item in inquiries_list:
        writer.writerow([
            item["id"],
            item["first_name"],
            item["last_name"] or "",
            item["email"],
            item["phone"] or "",
            item["company"] or "",
            item["budget"] or "",
            item["services"] or "",
            item["message"],
            item["status"],
            item["notes"] or "",
            item["created_at"],
        ])

    output.seek(0)
    filename = f"storyworks_inquiries_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
    return Response(
        output.getvalue(),
        mimetype="text/csv",
        headers={"Content-Disposition": f"attachment;filename={filename}"},
    )


# ─────────────────────────────────────────────────────────────
# BLOGS
# ─────────────────────────────────────────────────────────────

@admin_bp.route("/blogs")
@login_required
def blogs():
    blog_list = Blog.get_all()
    return render_template("admin/blogs.html", blogs=blog_list)


@admin_bp.route("/blogs/new", methods=["GET", "POST"])
@login_required
def new_blog():
    if request.method == "POST":
        title = request.form.get("title", "").strip()
        category = request.form.get("category", "Blog").strip()
        author = request.form.get("author", "Storyworks Studio").strip()
        published_date = request.form.get("published_date", datetime.now().strftime("%b %d, %Y"))
        cover_image = request.form.get("cover_image", "").strip()
        excerpt = request.form.get("excerpt", "").strip()
        content = request.form.get("content", "").strip()
        status = request.form.get("status", "published")

        # Handle uploaded image if provided
        if "cover_file" in request.files:
            file = request.files["cover_file"]
            if file and file.filename and allowed_file(file.filename):
                fname = f"blog_{int(datetime.now().timestamp())}_{secure_filename(file.filename)}"
                file.save(os.path.join(Config.UPLOAD_FOLDER, fname))
                cover_image = f"/uploads/{fname}"

        if not title:
            flash("Blog title is required.", "error")
            return render_template("admin/blog_form.html", blog=None)

        new_id = Blog.create({
            "title": title,
            "category": category,
            "author": author,
            "published_date": published_date,
            "cover_image": cover_image,
            "excerpt": excerpt,
            "content": content,
            "status": status,
        })
        flash("Blog post created successfully!", "success")
        return redirect(url_for("admin.blogs"))

    return render_template("admin/blog_form.html", blog=None)


@admin_bp.route("/blogs/<int:blog_id>/edit", methods=["GET", "POST"])
@login_required
def edit_blog(blog_id):
    blog = Blog.get_by_id(blog_id)
    if not blog:
        flash("Blog post not found.", "error")
        return redirect(url_for("admin.blogs"))

    if request.method == "POST":
        title = request.form.get("title", "").strip()
        slug = request.form.get("slug", "").strip()
        category = request.form.get("category", "Blog").strip()
        author = request.form.get("author", "Storyworks Studio").strip()
        published_date = request.form.get("published_date", blog["published_date"])
        cover_image = request.form.get("cover_image", blog["cover_image"]).strip()
        excerpt = request.form.get("excerpt", "").strip()
        content = request.form.get("content", "").strip()
        status = request.form.get("status", "published")

        if "cover_file" in request.files:
            file = request.files["cover_file"]
            if file and file.filename and allowed_file(file.filename):
                fname = f"blog_{int(datetime.now().timestamp())}_{secure_filename(file.filename)}"
                file.save(os.path.join(Config.UPLOAD_FOLDER, fname))
                cover_image = f"/uploads/{fname}"

        Blog.update(blog_id, {
            "title": title,
            "slug": slug,
            "category": category,
            "author": author,
            "published_date": published_date,
            "cover_image": cover_image,
            "excerpt": excerpt,
            "content": content,
            "status": status,
        })
        flash("Blog post updated successfully!", "success")
        return redirect(url_for("admin.blogs"))

    return render_template("admin/blog_form.html", blog=blog)


@admin_bp.route("/blogs/<int:blog_id>/delete", methods=["POST"])
@login_required
def delete_blog(blog_id):
    Blog.delete(blog_id)
    flash("Blog post deleted.", "info")
    return redirect(url_for("admin.blogs"))


# ─────────────────────────────────────────────────────────────
# PORTFOLIO
# ─────────────────────────────────────────────────────────────

@admin_bp.route("/portfolio")
@login_required
def portfolio():
    items = Portfolio.get_all()
    return render_template("admin/portfolio.html", items=items)


@admin_bp.route("/portfolio/new", methods=["GET", "POST"])
@login_required
def new_portfolio():
    if request.method == "POST":
        title = request.form.get("title", "").strip()
        client = request.form.get("client", "").strip()
        category = request.form.get("category", "").strip()
        badge = request.form.get("badge", client).strip()
        cover_image = request.form.get("cover_image", "").strip()
        short_desc = request.form.get("short_desc", "").strip()
        full_desc = request.form.get("full_desc", "").strip()
        quote = request.form.get("quote", "").strip()
        year = request.form.get("year", "2026").strip()
        project_url = request.form.get("project_url", "").strip()
        is_featured = bool(request.form.get("is_featured"))
        status = request.form.get("status", "published")

        if "cover_file" in request.files:
            file = request.files["cover_file"]
            if file and file.filename and allowed_file(file.filename):
                fname = f"port_{int(datetime.now().timestamp())}_{secure_filename(file.filename)}"
                file.save(os.path.join(Config.UPLOAD_FOLDER, fname))
                cover_image = f"/uploads/{fname}"

        if not title:
            flash("Project title is required.", "error")
            return render_template("admin/portfolio_form.html", item=None)

        Portfolio.create({
            "title": title,
            "client": client,
            "category": category,
            "badge": badge,
            "cover_image": cover_image,
            "short_desc": short_desc,
            "full_desc": full_desc,
            "quote": quote,
            "year": year,
            "project_url": project_url,
            "is_featured": is_featured,
            "status": status,
        })
        flash("Portfolio project added successfully!", "success")
        return redirect(url_for("admin.portfolio"))

    return render_template("admin/portfolio_form.html", item=None)


@admin_bp.route("/portfolio/<int:item_id>/edit", methods=["GET", "POST"])
@login_required
def edit_portfolio(item_id):
    item = Portfolio.get_by_id(item_id)
    if not item:
        flash("Portfolio item not found.", "error")
        return redirect(url_for("admin.portfolio"))

    if request.method == "POST":
        title = request.form.get("title", "").strip()
        slug = request.form.get("slug", item["slug"]).strip()
        client = request.form.get("client", "").strip()
        category = request.form.get("category", "").strip()
        badge = request.form.get("badge", client).strip()
        cover_image = request.form.get("cover_image", item["cover_image"]).strip()
        short_desc = request.form.get("short_desc", "").strip()
        full_desc = request.form.get("full_desc", "").strip()
        quote = request.form.get("quote", "").strip()
        year = request.form.get("year", "2026").strip()
        project_url = request.form.get("project_url", "").strip()
        is_featured = bool(request.form.get("is_featured"))
        status = request.form.get("status", "published")

        if "cover_file" in request.files:
            file = request.files["cover_file"]
            if file and file.filename and allowed_file(file.filename):
                fname = f"port_{int(datetime.now().timestamp())}_{secure_filename(file.filename)}"
                file.save(os.path.join(Config.UPLOAD_FOLDER, fname))
                cover_image = f"/uploads/{fname}"

        Portfolio.update(item_id, {
            "title": title,
            "slug": slug,
            "client": client,
            "category": category,
            "badge": badge,
            "cover_image": cover_image,
            "short_desc": short_desc,
            "full_desc": full_desc,
            "quote": quote,
            "year": year,
            "project_url": project_url,
            "is_featured": is_featured,
            "status": status,
        })
        flash("Portfolio project updated successfully!", "success")
        return redirect(url_for("admin.portfolio"))

    return render_template("admin/portfolio_form.html", item=item)


@admin_bp.route("/portfolio/<int:item_id>/delete", methods=["POST"])
@login_required
def delete_portfolio(item_id):
    Portfolio.delete(item_id)
    flash("Portfolio project deleted.", "info")
    return redirect(url_for("admin.portfolio"))


# ─────────────────────────────────────────────────────────────
# SERVICES
# ─────────────────────────────────────────────────────────────

@admin_bp.route("/services", methods=["GET", "POST"])
@login_required
def services():
    if request.method == "POST":
        title = request.form.get("title", "").strip()
        short_desc = request.form.get("short_desc", "").strip()
        full_desc = request.form.get("full_desc", "").strip()
        icon = request.form.get("icon", "").strip()
        order = request.form.get("display_order", 0)
        is_active = bool(request.form.get("is_active", 1))

        if title:
            Service.create({
                "title": title,
                "short_desc": short_desc,
                "full_desc": full_desc,
                "icon": icon,
                "display_order": order,
                "is_active": is_active,
            })
            flash("Service created successfully!", "success")
        return redirect(url_for("admin.services"))

    service_list = Service.get_all()
    return render_template("admin/services.html", services=service_list)


@admin_bp.route("/services/<int:service_id>/edit", methods=["GET", "POST"])
@login_required
def edit_service(service_id):
    service = Service.get_by_id(service_id)
    if not service:
        flash("Service not found.", "danger")
        return redirect(url_for("admin.services"))

    if request.method == "POST":
        title = request.form.get("title", "").strip()
        slug = request.form.get("slug", "").strip()
        short_desc = request.form.get("short_desc", "").strip()
        full_desc = request.form.get("full_desc", "").strip()
        icon = request.form.get("icon", "").strip()
        order = request.form.get("display_order", 0)
        is_active = bool(request.form.get("is_active"))

        if not title:
            flash("Service title is required.", "danger")
            return redirect(request.referrer or url_for("admin.services"))

        Service.update(service_id, {
            "title": title,
            "slug": slug or None,
            "short_desc": short_desc,
            "full_desc": full_desc,
            "icon": icon,
            "display_order": order,
            "is_active": is_active,
        })
        flash("Service updated successfully!", "success")
        return redirect(url_for("admin.services"))

    return render_template("admin/services_form.html", service=service)


@admin_bp.route("/services/<int:service_id>/delete", methods=["POST"])
@login_required
def delete_service(service_id):
    Service.delete(service_id)
    flash("Service deleted.", "info")
    return redirect(url_for("admin.services"))


# ─────────────────────────────────────────────────────────────
# SUBSCRIBERS
# ─────────────────────────────────────────────────────────────

@admin_bp.route("/subscribers")
@login_required
def subscribers():
    sub_list = Subscriber.get_all()
    return render_template("admin/subscribers.html", subscribers=sub_list)


@admin_bp.route("/subscribers/<int:sub_id>/delete", methods=["POST"])
@login_required
def delete_subscriber(sub_id):
    Subscriber.delete(sub_id)
    flash("Subscriber removed.", "info")
    return redirect(url_for("admin.subscribers"))


# ─────────────────────────────────────────────────────────────
# SETTINGS & PROFILE
# ─────────────────────────────────────────────────────────────

@admin_bp.route("/settings", methods=["GET", "POST"])
@login_required
def settings():
    if request.method == "POST":
        keys = [
            "site_name", "site_tagline", "contact_email",
            "contact_phone", "contact_address",
            "instagram_url", "linkedin_url", "twitter_url"
        ]
        for k in keys:
            if k in request.form:
                category = "social" if "url" in k else ("contact" if "contact" in k else "general")
                val = request.form[k].strip()
                Setting.set(k, val, category)

        flash("Settings saved successfully!", "success")
        return redirect(url_for("admin.settings"))

    settings_dict = Setting.get_all_dict()
    return render_template("admin/settings.html", settings=settings_dict)



@admin_bp.route("/profile", methods=["POST"])
@login_required
def update_profile():
    user_id = session["user_id"]
    username = request.form.get("username", "").strip()
    email = request.form.get("email", "").strip()
    current_pass = request.form.get("current_password", "")
    new_pass = request.form.get("new_password", "")

    user = User.get_by_id(user_id)
    if not user:
        flash("User not found.", "error")
        return redirect(url_for("admin.settings"))

    # If user wants to change password
    if new_pass:
        if not User.verify_password(user["password_hash"], current_pass):
            flash("Current password is incorrect.", "error")
            return redirect(url_for("admin.settings"))
        if len(new_pass) < 6:
            flash("New password must be at least 6 characters.", "error")
            return redirect(url_for("admin.settings"))
        User.update_password(user_id, new_pass)
        flash("Password updated successfully!", "success")

    # Update username and email
    if username and email:
        User.update_profile(user_id, username, email)
        session["username"] = username
        session["email"] = email
        flash("Profile information updated!", "success")

    return redirect(url_for("admin.settings"))


# ─────────────────────────────────────────────────────────────
# MEDIA UPLOAD HANDLER
# ─────────────────────────────────────────────────────────────

@admin_bp.route("/upload", methods=["POST"])
@login_required
def upload_file():
    if "file" not in request.files:
        return jsonify({"success": False, "error": "No file part"}), 400
    file = request.files["file"]
    if file.filename == "":
        return jsonify({"success": False, "error": "No selected file"}), 400
    if file and allowed_file(file.filename):
        timestamp = int(datetime.now().timestamp())
        filename = f"media_{timestamp}_{secure_filename(file.filename)}"
        filepath = os.path.join(Config.UPLOAD_FOLDER, filename)
        file.save(filepath)
        file_url = f"/uploads/{filename}"
        return jsonify({"success": True, "url": file_url, "filename": filename})
    return jsonify({"success": False, "error": "File type not allowed"}), 400

