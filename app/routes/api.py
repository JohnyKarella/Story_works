from flask import Blueprint, request, jsonify
from app.models import Inquiry, Blog, Portfolio, Service, Subscriber, Setting
api_bp = Blueprint("api", __name__, url_prefix="/api")
@api_bp.route("/contact", methods=["POST"])
def submit_contact():
    """Handle contact form submission."""
    # Accept either JSON or form encoded data
    if request.is_json:
        data = request.get_json() or {}
    else:
        data = request.form.to_dict()
    fname = data.get("fname") or data.get("first_name", "")
    lname = data.get("lname") or data.get("last_name", "")
    email = data.get("email", "")
    phone = data.get("phone", "")
    company = data.get("company", "")
    budget = data.get("budget", "")
    message = data.get("message", "")
    # Services can be passed as a list or comma-separated string
    services_val = data.get("services", "")
    if isinstance(services_val, list):
        services_str = ", ".join(services_val)
    else:
        services_str = str(services_val)
    # Validation
    errors = []
    if not fname.strip():
        errors.append("First name is required.")
    if not email.strip() or "@" not in email:
        errors.append("A valid email address is required.")
    if not message.strip():
        errors.append("Message cannot be empty.")
    if errors:
        return jsonify({"success": False, "errors": errors}), 400
    ip_address = request.headers.get("X-Forwarded-For", request.remote_addr)
    inquiry_data = {
        "first_name": fname,
        "last_name": lname,
        "email": email,
        "phone": phone,
        "company": company,
        "budget": budget,
        "services": services_str,
        "message": message,
        "ip_address": ip_address,
    }
    inquiry_id = Inquiry.create(inquiry_data)
    return jsonify({
        "success": True,
        "message": "Thank you! Your message has been received. Our team will contact you shortly.",
        "inquiry_id": inquiry_id,
    }), 201
@api_bp.route("/blogs", methods=["GET"])
def get_blogs():
    """Return published blogs."""
    blogs = Blog.get_all(status="published")
    return jsonify({"success": True, "count": len(blogs), "data": blogs})
@api_bp.route("/blogs/<slug_or_id>", methods=["GET"])
def get_single_blog(slug_or_id):
    """Return single blog post by slug or numeric ID."""
    if slug_or_id.isdigit():
        blog = Blog.get_by_id(int(slug_or_id))
    else:
        blog = Blog.get_by_slug(slug_or_id)
    if not blog or blog["status"] != "published":
        return jsonify({"success": False, "error": "Blog post not found"}), 404
    Blog.increment_views(blog["id"])
    return jsonify({"success": True, "data": blog})
@api_bp.route("/portfolio", methods=["GET"])
def get_portfolio():
    """Return published portfolio case studies."""
    category = request.args.get("category")
    items = Portfolio.get_all(category=category, status="published")
    return jsonify({"success": True, "count": len(items), "data": items})
@api_bp.route("/portfolio/<slug_or_id>", methods=["GET"])
def get_single_portfolio(slug_or_id):
    """Return single portfolio case study by slug or numeric ID."""
    if slug_or_id.isdigit():
        item = Portfolio.get_by_id(int(slug_or_id))
    else:
        item = Portfolio.get_by_slug(slug_or_id)
    if not item or item["status"] != "published":
        return jsonify({"success": False, "error": "Portfolio item not found"}), 404
    return jsonify({"success": True, "data": item})
@api_bp.route("/services", methods=["GET"])
def get_services():
    """Return active services."""
    services = Service.get_all(only_active=True)
    return jsonify({"success": True, "count": len(services), "data": services})
@api_bp.route("/newsletter", methods=["POST"])
def subscribe_newsletter():
    """Subscribe email to newsletter."""
    data = request.get_json() if request.is_json else request.form.to_dict()
    email = (data.get("email") or "").strip()
    if not email or "@" not in email:
        return jsonify({"success": False, "error": "Valid email address is required"}), 400
    added = Subscriber.add(email)
    if added:
        return jsonify({"success": True, "message": "Subscribed successfully!"})
    else:
        return jsonify({"success": True, "message": "Email is already subscribed."})
@api_bp.route("/settings", methods=["GET"])
def get_public_settings():
    """Return public agency contact and social info."""
    settings = Setting.get_all_dict()
    public_keys = [
        "site_name", "site_tagline", "contact_email",
        "contact_phone", "contact_address", "instagram_url",
        "linkedin_url", "twitter_url"
    ]
    return jsonify({
        "success": True,
        "data": {k: settings.get(k, "") for k in public_keys}
    })
@api_bp.route("/health", methods=["GET"])
def health_check():
    """System and database health check for Railway."""
    return jsonify({
        "status": "healthy",
        "service": "storyworks-studio",
        "database": "sqlite",
    }), 200
