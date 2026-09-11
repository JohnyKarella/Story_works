# Storyworks Studio — Python Backend & Admin Panel
Complete Python Flask backend and luxury dark-themed Admin Panel for **Storyworks Studio**.
---
## Quick Start
### 1. Requirements
Ensure Python 3.10+ is installed (tested and running on Python 3.14). Dependencies can be verified or installed via:
```powershell
python -m pip install -r requirements.txt
```
### 2. Start the Server
Run the application using:
```powershell
python run.py
```
The terminal will display the active endpoints:
- **Storyworks Website**: `http://127.0.0.1:5000/`
- **Contact Page**: `http://127.0.0.1:5000/contact.html`
- **Admin Panel**: `http://127.0.0.1:5000/admin`
- **Default Admin Credentials**:
  - **Username**: `admin`
  - **Password**: `admin123`
---
## Admin Panel Features
Visit `http://127.0.0.1:5000/admin` and sign in.
### 1. Studio Dashboard (`/admin/dashboard`)
- Real-time metrics: Total Inquiries, New/Pending Leads, Blog Articles, Portfolio Case Studies, and Newsletter Subscribers.
- Recent Leads table with quick "View Details" trigger.
- Quick shortcuts to add articles, case studies, or export leads.
### 2. Contact Inquiries & Leads Management (`/admin/inquiries`)
- Every message submitted through `contact.html` is captured automatically.
- Captures: First Name, Last Name, Email, Phone, Company, Budget, Selected Services (multi-pill), Message, Client IP, and Submission Date.
- Filter leads by status: `All`, `New`, `Contacted`, `In Progress`, `Closed`.
- Search leads by client name, email, or company.
- Change inquiry status from the dropdown or detail modal.
- Add and persist internal studio notes.
- **One-click Export to CSV** via the `Export CSV` button.
### 3. Blog Management (`/admin/blogs`)
- Full CRUD (Create, Read, Update, Delete) for blog articles.
- Rich article editor with cover image file upload or image path selection.
- Draft vs. Published status toggling.
- View counter tracking.
- Pre-seeded with existing articles from `blog.html` through `blog6.html`.
### 4. Portfolio Case Studies (`/admin/portfolio`)
- Full CRUD for client case studies.
- Manage client name, category, badge, client testimonial quotes, project year, live URL, and cover images.
- "Featured" flag to highlight top projects on the homepage.
- Pre-seeded with the 9 existing agency projects (`Shaanvi`, `Mantras`, `PickleJar`, `Bship`, `Fishland`, `Bhruhadrupi`, `SBL-Foods`, `SBL-Farms`, `Achuthan`).
### 5. Services Management (`/admin/services`)
- Add, edit, reorder, and activate/deactivate studio service offerings.
### 6. Newsletter Subscribers (`/admin/subscribers`)
- View and manage email signups.
### 7. Site Settings & Security (`/admin/settings`)
- Update company name, tagline, email, phone number, physical address, and social links (Instagram, LinkedIn, X) directly from the admin panel without touching HTML code.
- Update admin email, username, and change admin password.
---
## Public REST APIs
All API endpoints support CORS:
| Endpoint | Method | Description |
|---|---|---|
| `/api/contact` | `POST` | Submits a contact inquiry (JSON or form data). Validates required fields, stores to DB. |
| `/api/blogs` | `GET` | Returns list of published blog articles. |
| `/api/blogs/<slug_or_id>` | `GET` | Returns single article and increments its view count. |
| `/api/portfolio` | `GET` | Returns list of published case studies (supports `?category=...`). |
| `/api/portfolio/<slug_or_id>` | `GET` | Returns single case study details. |
| `/api/services` | `GET` | Returns list of active agency services. |
| `/api/newsletter` | `POST` | Subscribes an email to the newsletter. |
| `/api/settings` | `GET` | Returns public studio contact details and social links. |
---
## Database & Seeding
- **Default Engine**: SQLite (`storyworks.db`). Self-contained, zero-configuration.
- **Optional MySQL**: Update `DATABASE_TYPE=mysql` in `.env` with host/port/credentials.
- **Re-seed Data**:
  ```powershell
  python database/seed_data.py
  ```
---
## Automated Tests
Run the test suite at any time:
```powershell
python -W ignore -m unittest discover tests
```
All tests verify public APIs, contact form submissions, authentication guards, and admin workflows.
