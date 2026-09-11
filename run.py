import os
from app import create_app
from app.config import Config
app = create_app()
if __name__ == "__main__":
    port = int(os.getenv("PORT", 5000))
    host = os.getenv("HOST", "0.0.0.0" if os.getenv("PORT") else "127.0.0.1")
    debug = os.getenv("DEBUG", "False" if os.getenv("PORT") else "True").lower() in ("true", "1", "yes")
    print("\n" + "=" * 60)
    print("  * STORYWORKS STUDIO BACKEND & ADMIN PANEL *")
    print("=" * 60)
    print(f"  - Website:     http://{host}:{port}/")
    print(f"  - Contact:     http://{host}:{port}/contact.html")
    print(f"  - Admin Panel: http://{host}:{port}/admin")
    print(f"  - Admin Login: {Config.DEFAULT_ADMIN_USERNAME} / {Config.DEFAULT_ADMIN_PASSWORD}")
    print(f"  - REST API:    http://{host}:{port}/api/contact")
    print("=" * 60 + "\n")
    app.run(host=host, port=port, debug=debug)
