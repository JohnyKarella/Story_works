from functools import wraps
from flask import (
    Blueprint,
    render_template,
    request,
    redirect,
    url_for,
    flash,
    session,
    jsonify,
    current_app,
)
from app.models import User, Inquiry, Service, Setting

client_bp = Blueprint("client", __name__, url_prefix="/client")


def client_login_required(f):
    """Decorator to require authenticated client session."""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        client_id = session.get("client_id")
        if not client_id:
            flash("Please sign in to access your client portal.", "warning")
            return redirect(url_for("client.login", next=request.url))

        client = User.get_by_id(client_id)
        if not client:
            for key in ["client_id", "client_username", "client_email", "client_name", "client_role"]:
                session.pop(key, None)
            flash("Your session has expired. Please sign in again.", "warning")
            return redirect(url_for("client.login", next=request.url))

        return f(*args, **kwargs)
    return decorated_function


@client_bp.context_processor
def inject_client_context():
    """Inject current client information and studio settings into all client templates."""
    client_user = None
    if session.get("client_id"):
        client_user = User.get_by_id(session["client_id"])
    return {
        "current_client": client_user,
        "site_settings": Setting.get_all_dict(),
    }


# ─────────────────────────────────────────────────────────────
# AUTHENTICATION (Register, Login, Logout)
# ─────────────────────────────────────────────────────────────

@client_bp.route("/register", methods=["GET", "POST"], strict_slashes=False)
def register():
    if session.get("client_id"):
        if User.get_by_id(session["client_id"]):
            return redirect(url_for("client.dashboard"))
        for key in ["client_id", "client_username", "client_email", "client_name", "client_role"]:
            session.pop(key, None)

    if request.method == "POST":
        username = request.form.get("username", "").strip()
        email = request.form.get("email", "").strip().lower()
        full_name = request.form.get("full_name", "").strip()
        company = request.form.get("company", "").strip()
        phone = request.form.get("phone", "").strip()
        password = request.form.get("password", "")
        confirm_password = request.form.get("confirm_password", "")

        # Validation
        if not username or not email or not full_name or not password:
            flash("Please fill in all required fields (Username, Email, Full Name, Password).", "error")
            return render_template("client/register.html", form_data=request.form)

        if len(password) < 6:
            flash("Password must be at least 6 characters long.", "error")
            return render_template("client/register.html", form_data=request.form)

        if password != confirm_password:
            flash("Passwords do not match. Please verify your password.", "error")
            return render_template("client/register.html", form_data=request.form)

        # Check existing username
        if User.get_by_username(username):
            flash("That username is already taken. Please choose another.", "error")
            return render_template("client/register.html", form_data=request.form)

        # Check existing email
        if User.get_by_email(email):
            flash("An account with this email address already exists. Please sign in.", "error")
            return render_template("client/register.html", form_data=request.form)

        try:
            new_id = User.create(
                username=username,
                email=email,
                password=password,
                role="client",
                full_name=full_name,
                company=company,
                phone=phone,
            )

            # Auto-sign in the newly registered client
            session["client_id"] = new_id
            session["client_username"] = username
            session["client_email"] = email
            session["client_name"] = full_name
            session["client_role"] = "client"
            User.record_login(new_id)

            flash(f"Welcome to Storyworks, {full_name}! Your client portal is ready.", "success")
            return redirect(url_for("client.dashboard"))

        except Exception as e:
            flash(f"Registration failed: {str(e)}", "error")
            return render_template("client/register.html", form_data=request.form)

    return render_template("client/register.html", form_data={})


@client_bp.route("/login", methods=["GET", "POST"], strict_slashes=False)
def login():
    if session.get("client_id"):
        if User.get_by_id(session["client_id"]):
            return redirect(url_for("client.dashboard"))
        for key in ["client_id", "client_username", "client_email", "client_name", "client_role"]:
            session.pop(key, None)

    if request.method == "POST":
        identifier = request.form.get("identifier", "").strip()
        password = request.form.get("password", "")
        remember = bool(request.form.get("remember"))

        if not identifier or not password:
            flash("Please enter both username/email and your password.", "error")
            return render_template("client/login.html")

        # Identifier can be either username or email
        user = User.get_by_username(identifier)
        if not user:
            user = User.get_by_email(identifier)

        if user and User.verify_password(user["password_hash"], password):
            session.permanent = remember
            session["client_id"] = user["id"]
            session["client_username"] = user["username"]
            session["client_email"] = user["email"]
            session["client_name"] = user.get("full_name") or user["username"]
            session["client_role"] = user.get("role", "client")
            User.record_login(user["id"])

            flash(f"Welcome back, {session['client_name']}!", "success")
            next_page = request.args.get("next")
            return redirect(next_page or url_for("client.dashboard"))
        else:
            flash("Invalid username/email or password. Please try again.", "error")

    return render_template("client/login.html")


@client_bp.route("/logout")
def logout():
    session.pop("client_id", None)
    session.pop("client_username", None)
    session.pop("client_email", None)
    session.pop("client_name", None)
    session.pop("client_role", None)
    flash("You have been signed out of the Client Portal.", "info")
    return redirect(url_for("client.login"))


# ─────────────────────────────────────────────────────────────
# CLIENT DASHBOARD & MAIN VIEWS
# ─────────────────────────────────────────────────────────────

@client_bp.route("", strict_slashes=False)
@client_bp.route("/", strict_slashes=False)
@client_bp.route("/dashboard", strict_slashes=False)
@client_login_required
def dashboard():
    client_id = session.get("client_id")
    client = User.get_by_id(client_id) if client_id else None
    if not client:
        for key in ["client_id", "client_username", "client_email", "client_name", "client_role"]:
            session.pop(key, None)
        flash("Please sign in to access your client portal.", "warning")
        return redirect(url_for("client.login"))

    stats = Inquiry.get_client_stats(client["id"], client.get("email"))
    all_inquiries = Inquiry.get_for_client(client["id"], client.get("email")) or []
    recent_inquiries = all_inquiries[:5]
    services = Service.get_all() or []

    return render_template(
        "client/dashboard.html",
        client=client,
        stats=stats,
        recent_inquiries=recent_inquiries,
        services=services,
    )


# ─────────────────────────────────────────────────────────────
# CLIENT PROJECT BRIEFS & INQUIRIES
# ─────────────────────────────────────────────────────────────

@client_bp.route("/requests", strict_slashes=False)
@client_login_required
def requests():
    client_id = session.get("client_id")
    client = User.get_by_id(client_id) if client_id else None
    if not client:
        for key in ["client_id", "client_username", "client_email", "client_name", "client_role"]:
            session.pop(key, None)
        flash("Please sign in to access your client portal.", "warning")
        return redirect(url_for("client.login"))

    status_filter = request.args.get("status", "all").strip().lower()
    inquiries = Inquiry.get_for_client(client["id"], client.get("email")) or []

    if status_filter and status_filter != "all":
        if status_filter in ("in_progress", "contacted"):
            inquiries = [i for i in inquiries if i.get("status") in ("in_progress", "contacted")]
        elif status_filter in ("closed", "completed"):
            inquiries = [i for i in inquiries if i.get("status") in ("closed", "completed")]
        else:
            inquiries = [i for i in inquiries if i.get("status") == status_filter]

    stats = Inquiry.get_client_stats(client["id"], client.get("email"))

    return render_template(
        "client/requests.html",
        client=client,
        inquiries=inquiries,
        stats=stats,
        active_status=status_filter,
    )


@client_bp.route("/request-service", methods=["GET", "POST"], strict_slashes=False)
@client_login_required
def request_service():
    client_id = session.get("client_id")
    client = User.get_by_id(client_id) if client_id else None
    if not client:
        for key in ["client_id", "client_username", "client_email", "client_name", "client_role"]:
            session.pop(key, None)
        flash("Please sign in to access your client portal.", "warning")
        return redirect(url_for("client.login"))

    services = Service.get_all() or []
    preselected = request.args.get("service", "").strip()

    if request.method == "POST":
        first_name = request.form.get("first_name", "").strip() or client.get("full_name", "")
        last_name = request.form.get("last_name", "").strip()
        email = request.form.get("email", "").strip() or client.get("email", "")
        phone = request.form.get("phone", "").strip() or client.get("phone", "")
        company = request.form.get("company", "").strip() or client.get("company", "")
        budget = request.form.get("budget", "").strip()
        timeline = request.form.get("timeline", "").strip()
        selected_services = request.form.getlist("services")
        message = request.form.get("message", "").strip()

        if not message:
            flash("Please provide details regarding your project or brief requirements.", "error")
            return render_template(
                "client/request_form.html",
                client=client,
                services=services,
                preselected=preselected,
                form_data=request.form,
            )

        # Append timeline info to message if provided
        formatted_message = message
        if timeline:
            formatted_message = f"[Target Timeline: {timeline}]\n\n{message}"

        inquiry_data = {
            "user_id": client["id"],
            "first_name": first_name or client.get("username", "Client"),
            "last_name": last_name,
            "email": email,
            "phone": phone,
            "company": company,
            "budget": budget,
            "timeline": timeline,
            "services": ", ".join(selected_services) if selected_services else "General Creative Strategy",
            "message": formatted_message,
            "ip_address": request.remote_addr or "",
        }

        Inquiry.create(inquiry_data)
        flash("Your project brief has been submitted successfully! Our creative team will review it and get in touch with you.", "success")
        return redirect(url_for("client.requests"))

    return render_template(
        "client/request_form.html",
        client=client,
        services=services,
        preselected=preselected,
        form_data={},
    )


# ─────────────────────────────────────────────────────────────
# CLIENT AGENCY SERVICES CATALOGUE
# ─────────────────────────────────────────────────────────────

@client_bp.route("/services", strict_slashes=False)
@client_login_required
def services():
    client_id = session.get("client_id")
    client = User.get_by_id(client_id) if client_id else None
    if not client:
        for key in ["client_id", "client_username", "client_email", "client_name", "client_role"]:
            session.pop(key, None)
        flash("Please sign in to access your client portal.", "warning")
        return redirect(url_for("client.login"))

    services_list = Service.get_all() or []
    return render_template(
        "client/services.html",
        client=client,
        services=services_list,
    )


# ─────────────────────────────────────────────────────────────
# CLIENT PROFILE & PASSWORD SETTINGS
# ─────────────────────────────────────────────────────────────

@client_bp.route("/profile", methods=["GET", "POST"], strict_slashes=False)
@client_login_required
def profile():
    client_id = session.get("client_id")
    client = User.get_by_id(client_id) if client_id else None
    if not client:
        for key in ["client_id", "client_username", "client_email", "client_name", "client_role"]:
            session.pop(key, None)
        flash("Please sign in to access your client portal.", "warning")
        return redirect(url_for("client.login"))

    stats = Inquiry.get_client_stats(client["id"], client.get("email"))

    if request.method == "POST":
        action = request.form.get("action")

        if action == "update_profile":
            full_name = request.form.get("full_name", "").strip()
            company = request.form.get("company", "").strip()
            phone = request.form.get("phone", "").strip()

            if not full_name:
                flash("Full name cannot be empty.", "error")
            else:
                User.update_client_profile(client["id"], full_name, company, phone)
                session["client_name"] = full_name
                flash("Your profile information has been updated.", "success")
                return redirect(url_for("client.profile"))

        elif action == "change_password":
            current_password = request.form.get("current_password", "")
            new_password = request.form.get("new_password", "")
            confirm_new_password = request.form.get("confirm_new_password", "")

            if not User.verify_password(client["password_hash"], current_password):
                flash("Current password is incorrect.", "error")
            elif len(new_password) < 6:
                flash("New password must be at least 6 characters.", "error")
            elif new_password != confirm_new_password:
                flash("New passwords do not match. Please verify.", "error")
            else:
                User.update_password(client["id"], new_password)
                flash("Your password has been changed successfully! Please use your new password next time you sign in.", "success")
                return redirect(url_for("client.profile"))

    return render_template(
        "client/profile.html",
        client=client,
        stats=stats,
    )

