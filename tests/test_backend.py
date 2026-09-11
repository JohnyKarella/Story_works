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


if __name__ == "__main__":
    unittest.main()
