from flask import Flask
from flask_cors import CORS
from app.config import Config
from app.database import init_db
def create_app(config_class=Config):
    app = Flask(
        __name__,
        template_folder="templates",
        static_folder="static",
        static_url_path="/admin-static",
    )
    app.config.from_object(config_class)
    # Enable CORS for API routes
    CORS(app, resources={r"/api/*": {"origins": "*"}})
    # Initialize Database
    with app.app_context():
        init_db(app)
    # Register Blueprints
    from app.routes.api import api_bp
    from app.routes.admin import admin_bp
    from app.routes.client import client_bp
    from app.routes.web import web_bp
    app.register_blueprint(api_bp)
    app.register_blueprint(admin_bp)
    app.register_blueprint(client_bp)
    # web_bp is registered last to avoid capturing /api, /admin, and /client paths
    app.register_blueprint(web_bp)

    # ── Exact Timeline & Datetime Filters ──
    @app.template_filter("format_dt")
    def format_dt_filter(value, fmt="%d %b %Y, %I:%M %p"):
        if not value:
            return "—"
        try:
            from datetime import datetime
            if isinstance(value, str):
                clean_str = value.replace("T", " ")[:19]
                dt = datetime.strptime(clean_str, "%Y-%m-%d %H:%M:%S")
            elif isinstance(value, datetime):
                dt = value
            else:
                return str(value)
            return dt.strftime(fmt)
        except Exception:
            return str(value)

    @app.template_filter("format_date")
    def format_date_filter(value):
        return format_dt_filter(value, "%d %b %Y")

    @app.template_filter("format_time")
    def format_time_filter(value):
        return format_dt_filter(value, "%I:%M %p")
    @app.after_request
    def add_no_cache_headers(response):
        response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
        response.headers["Pragma"] = "no-cache"
        response.headers["Expires"] = "0"
        return response
    return app
