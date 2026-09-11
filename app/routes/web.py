import os
from pathlib import Path
from flask import Blueprint, send_from_directory, abort, current_app, redirect, jsonify
from app.config import Config

web_bp = Blueprint("web", __name__)


@web_bp.route("/health")
def health():
    return jsonify({"status": "healthy", "service": "storyworks-studio"}), 200


@web_bp.route("/admin.html")
def admin_redirect():
    return redirect("/admin")


@web_bp.route("/favicon.ico")
def favicon_ico():
    return send_from_directory(
        os.path.join(current_app.root_path, "static", "admin"),
        "favicon.ico",
        mimetype="image/vnd.microsoft.icon",
    )


@web_bp.route("/favicon.png")
def favicon_png():
    return send_from_directory(
        os.path.join(current_app.root_path, "static", "admin"),
        "favicon.png",
        mimetype="image/png",
    )


@web_bp.route("/favicon.svg")
def favicon_svg():
    return send_from_directory(
        os.path.join(current_app.root_path, "static", "admin"),
        "favicon.svg",
        mimetype="image/svg+xml",
    )


@web_bp.route("/")
def home():
    return send_from_directory(Config.BASE_DIR, "index.html")


@web_bp.route("/about")
@web_bp.route("/about_us.html")
def about():
    return send_from_directory(Config.BASE_DIR, "about_us.html")


@web_bp.route("/contact")
@web_bp.route("/contact.html")
def contact():
    return send_from_directory(Config.BASE_DIR, "contact.html")


@web_bp.route("/services")
@web_bp.route("/services.html")
def services():
    return send_from_directory(Config.BASE_DIR, "services.html")


@web_bp.route("/portfolio")
@web_bp.route("/portfolio.html")
def portfolio():
    return send_from_directory(Config.BASE_DIR, "portfolio.html")


@web_bp.route("/blog")
@web_bp.route("/blog_pages.html")
def blog_list():
    return send_from_directory(Config.BASE_DIR, "blog_pages.html")


@web_bp.route("/terms")
@web_bp.route("/terms.html")
def terms():
    return send_from_directory(Config.BASE_DIR, "terms.html")


@web_bp.route("/uploads/<path:filename>")
def uploaded_file(filename):
    """Serve uploaded media files."""
    return send_from_directory(Config.UPLOAD_FOLDER, filename)


def _resolve_file_case_insensitive(base_dir, rel_path):
    """Case-insensitive filesystem lookup helper for Linux containers."""
    parts = Path(rel_path).parts
    curr = Path(base_dir)
    for part in parts:
        if not curr.is_dir():
            return None
        low = part.lower()
        matched = None
        try:
            for entry in os.scandir(curr):
                if entry.name.lower() == low:
                    matched = Path(entry.path)
                    break
        except OSError:
            return None
        if not matched:
            return None
        curr = matched
    return str(curr) if curr.is_file() else None


@web_bp.route("/<path:path>")
def static_pages_and_files(path):
    """Serve any other static HTML or root asset file."""
    # Prevent directory traversal
    safe_path = os.path.normpath(path).lstrip("/\\")
    if ".." in safe_path:
        abort(403)

    full_path = os.path.join(Config.BASE_DIR, safe_path)
    if os.path.isfile(full_path):
        directory = os.path.dirname(full_path)
        filename = os.path.basename(full_path)
        return send_from_directory(directory, filename)

    # Check if adding .html finds a matching file
    if os.path.isfile(full_path + ".html"):
        directory = os.path.dirname(full_path)
        return send_from_directory(directory, os.path.basename(full_path) + ".html")

    # Case-insensitive resolution for Linux containers (Railway)
    resolved = _resolve_file_case_insensitive(Config.BASE_DIR, safe_path)
    if resolved and os.path.isfile(resolved):
        return send_from_directory(os.path.dirname(resolved), os.path.basename(resolved))

    resolved_html = _resolve_file_case_insensitive(Config.BASE_DIR, safe_path + ".html")
    if resolved_html and os.path.isfile(resolved_html):
        return send_from_directory(os.path.dirname(resolved_html), os.path.basename(resolved_html))

    abort(404)

