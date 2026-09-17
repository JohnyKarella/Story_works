import unittest
import json
import os
import sys
from pathlib import Path
BASE_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(BASE_DIR))
from app import create_app
from app.config import Config
from app.models import User, Inquiry, Blog, Portfolio, Service, Setting
class BackendTestCase(unittest.TestCase):
    def setUp(self):
        self.app = create_app()
        self.app.config["TESTING"] = True
        self.client = self.app.test_client()
    def test_frontend_routes(self):
        """Verify static and dynamic frontend page routes."""
        res = self.client.get("/")
        self.assertEqual(res.status_code, 200)
        res = self.client.get("/contact.html")
        self.assertEqual(res.status_code, 200)
        res = self.client.get("/portfolio.html")
        self.assertEqual(res.status_code, 200)
        res = self.client.get("/about_us.html")
        self.assertEqual(res.status_code, 200)
        res = self.client.get("/blog_pages.html")
        self.assertEqual(res.status_code, 200)
    def test_public_apis(self):
        """Verify all public JSON APIs."""
        # 1. Blogs API
        res = self.client.get("/api/blogs")
        self.assertEqual(res.status_code, 200)
        data = res.get_json()
        self.assertTrue(data["success"])
        self.assertGreater(data["count"], 0)
        # Single Blog API
        slug = data["data"][0]["slug"]
        res = self.client.get(f"/api/blogs/{slug}")
        self.assertEqual(res.status_code, 200)
        self.assertTrue(res.get_json()["success"])
        # 2. Portfolio API
        res = self.client.get("/api/portfolio")
        self.assertEqual(res.status_code, 200)
        p_data = res.get_json()
        self.assertTrue(p_data["success"])
        self.assertGreater(p_data["count"], 0)
        # 3. Services API
        res = self.client.get("/api/services")
        self.assertEqual(res.status_code, 200)
        self.assertTrue(res.get_json()["success"])
        # 4. Settings API
        res = self.client.get("/api/settings")
        self.assertEqual(res.status_code, 200)
        self.assertTrue(res.get_json()["success"])
        self.assertIn("contact_email", res.get_json()["data"])
        # 5. Newsletter API
        res = self.client.post("/api/newsletter", json={"email": "tester123@example.com"})
        self.assertEqual(res.status_code, 200)
        self.assertTrue(res.get_json()["success"])
    def test_contact_form_submission(self):
        """Verify contact form validation and saving."""
        # Invalid submission (missing email and message)
        res = self.client.post("/api/contact", json={"fname": "John"})
        self.assertEqual(res.status_code, 400)
        self.assertFalse(res.get_json()["success"])
        # Valid submission
        res = self.client.post(
            "/api/contact",
            json={
                "fname": "Priya",
                "lname": "Sharma",
                "email": "priya@organics.in",
                "phone": "+91 99887 76655",
                "company": "Priya Organics",
                "budget": "₹75,000 – ₹2,00,000",
                "services": "Branding, Packaging",
                "message": "We need help redesigning our organic skincare line packaging and website.",
            },
        )
        self.assertEqual(res.status_code, 201)
        data = res.get_json()
        self.assertTrue(data["success"])
        self.assertIn("inquiry_id", data)
        # Verify it was saved in DB
        inquiry = Inquiry.get_by_id(data["inquiry_id"])
        self.assertIsNotNone(inquiry)
        self.assertEqual(inquiry["first_name"], "Priya")
        self.assertEqual(inquiry["company"], "Priya Organics")
    def test_admin_auth_and_dashboard(self):
        """Verify admin login protection and session workflow."""
        # Unauthenticated access should redirect to login
        res = self.client.get("/admin/dashboard")
        self.assertEqual(res.status_code, 302)
        self.assertIn("/admin/login", res.headers["Location"])
        # Bad login attempt
        res = self.client.post(
            "/admin/login",
            data={"username": "admin", "password": "wrongpassword"},
        )
        self.assertEqual(res.status_code, 200)
        # Successful login
        res = self.client.post(
            "/admin/login",
            data={
                "username": Config.DEFAULT_ADMIN_USERNAME,
                "password": Config.DEFAULT_ADMIN_PASSWORD,
            },
            follow_redirects=True,
        )
        self.assertEqual(res.status_code, 200)
        self.assertIn(b"Studio Overview", res.data)
        # Inquiries page
        res = self.client.get("/admin/inquiries")
        self.assertEqual(res.status_code, 200)
        self.assertIn(b"Client Inquiries", res.data)
        # Inquiries CSV export
        res = self.client.get("/admin/inquiries/export")
        self.assertEqual(res.status_code, 200)
        self.assertEqual(res.mimetype, "text/csv")
        self.assertIn(b"First Name", res.data)
        # Blogs admin page
        res = self.client.get("/admin/blogs")
        self.assertEqual(res.status_code, 200)
        self.assertIn(b"Blog Articles", res.data)
        # Portfolio admin page
        res = self.client.get("/admin/portfolio")
        self.assertEqual(res.status_code, 200)
        self.assertIn(b"Portfolio Case Studies", res.data)
        # Services admin page
        res = self.client.get("/admin/services")
        self.assertEqual(res.status_code, 200)
        self.assertIn(b"Agency Services", res.data)
        # Settings admin page
        res = self.client.get("/admin/settings")
        self.assertEqual(res.status_code, 200)
        self.assertIn(b"Settings & Admin Profile", res.data)
    def test_client_portal_auth_and_workflow(self):
        """Verify client registration, login, brief submission, profile updates, and role isolation."""
        # 1. Unauthenticated access should redirect to client login
        res = self.client.get("/client/dashboard")
        self.assertEqual(res.status_code, 302)
        self.assertIn("/client/login", res.headers["Location"])
        res = self.client.get("/client/requests")
        self.assertEqual(res.status_code, 302)
        res = self.client.get("/client/request-service")
        self.assertEqual(res.status_code, 302)
        res = self.client.get("/client/profile")
        self.assertEqual(res.status_code, 302)
        # Login and Register pages load 200
        self.assertEqual(self.client.get("/client/login").status_code, 200)
        self.assertEqual(self.client.get("/client/register").status_code, 200)
        # 2. Registration with self-chosen password
        import uuid
        uid = uuid.uuid4().hex[:8]
        unique_username = f"sarah_client_{uid}"
        unique_email = f"sarah_{uid}@acmebrands.com"
        client_pwd = "MySecurePassword123!"
        res = self.client.post(
            "/client/register",
            data={
                "username": unique_username,
                "email": unique_email,
                "full_name": "Sarah Jenkins",
                "company": "Acme Brands International",
                "phone": "+91 91234 56789",
                "password": client_pwd,
                "confirm_password": client_pwd,
            },
            follow_redirects=True,
        )
        self.assertEqual(res.status_code, 200)
        self.assertIn(b"Client Portal Dashboard", res.data)
        self.assertIn(b"Sarah Jenkins", res.data)
        # Verify user in database
        client_user = User.get_by_username(unique_username)
        self.assertIsNotNone(client_user)
        self.assertEqual(client_user["role"], "client")
        self.assertEqual(client_user["company"], "Acme Brands International")
        self.assertTrue(User.verify_password(client_user["password_hash"], client_pwd))
        # 3. Duplicate registration rejection (when signed out)
        self.client.get("/client/logout")
        res_dup = self.client.post(
            "/client/register",
            data={
                "username": unique_username,
                "email": unique_email,
                "full_name": "Sarah Copy",
                "password": client_pwd,
                "confirm_password": client_pwd,
            },
        )
        self.assertEqual(res_dup.status_code, 200)
        self.assertIn(b"already taken", res_dup.data.lower())
        # Log back in as Sarah
        self.client.post(
            "/client/login",
            data={"identifier": unique_username, "password": client_pwd},
            follow_redirects=True,
        )
        # 4. Submit a project brief as logged-in client
        res = self.client.post(
            "/client/request-service",
            data={
                "first_name": "Sarah",
                "last_name": "Jenkins",
                "email": unique_email,
                "phone": "+91 91234 56789",
                "company": "Acme Brands International",
                "budget": "₹2,00,000 – ₹5,00,000",
                "timeline": "1 – 2 Months",
                "services": ["Brand Strategy", "Web & Experience Design"],
                "message": "We need an end-to-end brand transformation and web presence launch.",
            },
            follow_redirects=True,
        )
        self.assertEqual(res.status_code, 200)
        self.assertIn(b"My Project Briefs", res.data)
        self.assertIn(b"Brand Strategy", res.data)
        # Verify inquiry in DB has user_id
        client_inquiries = Inquiry.get_for_client(client_user["id"], unique_email)
        self.assertGreater(len(client_inquiries), 0)
        self.assertEqual(client_inquiries[0]["user_id"], client_user["id"])
        # 5. Client Services & Profile pages
        res = self.client.get("/client/services")
        self.assertEqual(res.status_code, 200)
        self.assertIn(b"Brand Strategy", res.data)
        res = self.client.get("/client/profile")
        self.assertEqual(res.status_code, 200)
        self.assertIn(b"Sarah Jenkins", res.data)
        # 6. Update Profile
        res = self.client.post(
            "/client/profile",
            data={
                "action": "update_profile",
                "full_name": "Sarah Jenkins-Smith",
                "company": "Acme Global Co",
                "phone": "+91 99999 88888",
            },
            follow_redirects=True,
        )
        self.assertEqual(res.status_code, 200)
        updated_client = User.get_by_id(client_user["id"])
        self.assertEqual(updated_client["full_name"], "Sarah Jenkins-Smith")
        self.assertEqual(updated_client["company"], "Acme Global Co")
        # 7. Update Password
        new_pwd = "BrandNewPassword456@"
        res = self.client.post(
            "/client/profile",
            data={
                "action": "change_password",
                "current_password": client_pwd,
                "new_password": new_pwd,
                "confirm_new_password": new_pwd,
            },
            follow_redirects=True,
        )
        self.assertEqual(res.status_code, 200)
        # 8. Logout
        res = self.client.get("/client/logout", follow_redirects=True)
        self.assertEqual(res.status_code, 200)
        self.assertIn(b"Client Sign In", res.data)
        # 9. Log in with new password using email as identifier
        res = self.client.post(
            "/client/login",
            data={
                "identifier": unique_email,
                "password": new_pwd,
            },
            follow_redirects=True,
        )
        self.assertEqual(res.status_code, 200)
        self.assertIn(b"Client Portal Dashboard", res.data)
        # 10. Role isolation: client cannot access admin panel
        res = self.client.get("/admin/dashboard")
        self.assertEqual(res.status_code, 302)
        self.assertIn("/admin/login", res.headers["Location"])
        res = self.client.post(
            "/admin/login",
            data={"username": unique_username, "password": new_pwd},
        )
        self.assertEqual(res.status_code, 200)
        self.assertIn(b"Access denied", res.data)
if __name__ == "__main__":
    unittest.main()
