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
    from app.routes.web import web_bp
    app.register_blueprint(api_bp)
    app.register_blueprint(admin_bp)
    # web_bp is registered last to avoid capturing /api and /admin paths
    app.register_blueprint(web_bp)
    @app.after_request
    def add_no_cache_headers(response):
        response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
        response.headers["Pragma"] = "no-cache"
        response.headers["Expires"] = "0"
        return response
    return app
