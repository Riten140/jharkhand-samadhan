"""
Jharkhand Samadhan — Complaint Verification Platform (v2)

Three real logins: Citizen, Officer, Admin. Citizens file a complaint with a
photo/video. An AI engine (pure Pillow, offline) cross-checks the upload against
the stated problem and verifies whether the reported issue is visible; high
confidence auto-verifies the complaint, low confidence routes it to an officer
for manual verification instead of blocking the citizen. Once an officer
accepts a case they get a resolution deadline. When they upload an "after"
photo, a real before/after image comparison (Pillow) decides whether the case
auto-closes or reopens.

Only two third-party packages are needed: Flask and Pillow. Auth is handled
with Flask's own signed session cookies (no Flask-Login) and persistence is
plain sqlite3 (no ORM) — see db.py. Data lives in jsamadhan.db next to this
file; delete it to reset to a clean seeded state.
"""

import hashlib
import json
import math
import os
import sqlite3
import uuid
from datetime import datetime, timedelta
from functools import wraps

from flask import (Flask, render_template, request, redirect, url_for,
                    flash, send_from_directory, abort, session, g)
from PIL import ExifTags, Image

import db
import ai_engine
import i18n

BASE_DIR = os.path.abspath(os.path.dirname(__file__))
UPLOAD_DIR = os.path.join(BASE_DIR, "uploads")
PROFILE_DIR = os.path.join(BASE_DIR, "static", "profile")
os.makedirs(UPLOAD_DIR, exist_ok=True)
os.makedirs(PROFILE_DIR, exist_ok=True)

ALLOWED_EXT = {"png", "jpg", "jpeg", "gif", "webp", "mp4", "mov", "avi", "webm"}
PROFILE_EXT = {"png", "jpg", "jpeg", "webp", "gif"}
VIDEO_EXT = {"mp4", "mov", "avi", "webm"}
IMAGE_LOCATION_TOLERANCE_METERS = 5000

app = Flask(__name__)
app.secret_key = "jsamadhan-dev-secret-change-me"
app.config["MAX_CONTENT_LENGTH"] = 25 * 1024 * 1024  # 25 MB uploads
app.config["PERMANENT_SESSION_LIFETIME"] = timedelta(days=30)

db.init_db()


@app.teardown_appcontext
def _close_db(exception):
    db.close_db(exception)


@app.before_request
def load_current_user():
    user_id = session.get("user_id")
    g.current_user = db.hydrate_user(db.get_user_by_id(db.get_db(), user_id)) if user_id else None
    g.lang = session.get("lang", i18n.DEFAULT_LANG)
    if g.lang not in i18n.LANGUAGE_CODES:
        g.lang = i18n.DEFAULT_LANG


@app.context_processor
def inject_current_user():
    return {
        "current_user": g.get("current_user"),
        "LANGUAGES": i18n.LANGUAGES,
        "current_lang_code": g.get("lang", i18n.DEFAULT_LANG),
    }


# Register as true Jinja *globals* (not just per-render context) so they
# also work inside imported macros without needing "with context".
app.jinja_env.globals["t"] = i18n.t
app.jinja_env.globals["tr_text"] = i18n.tr_text
app.jinja_env.globals["cat_label"] = i18n.cat_label
app.jinja_env.globals["dist_label"] = i18n.dist_label


@app.route("/set-language/<code>")
def set_language(code):
    if code in i18n.LANGUAGE_CODES:
        session["lang"] = code
    return redirect(request.referrer or url_for("landing"))


# ---------------------------------------------------------------------------
# helpers
# ---------------------------------------------------------------------------

def allowed_file(filename):
    return "." in filename and filename.rsplit(".", 1)[1].lower() in ALLOWED_EXT


def save_upload(file_storage):
    """Save an uploaded file with a unique name; return (filename, is_video)."""
    if not file_storage or file_storage.filename == "":
        return None, False
    if not allowed_file(file_storage.filename):
        raise ValueError("Unsupported file type. Please upload an image or video.")
    ext = file_storage.filename.rsplit(".", 1)[1].lower()
    filename = f"{uuid.uuid4().hex}.{ext}"
    file_storage.save(os.path.join(UPLOAD_DIR, filename))
    return filename, ext in VIDEO_EXT


def save_profile_photo(file_storage):
    """Validate + resize an uploaded profile photo to a small square PNG."""
    if not file_storage or not file_storage.filename:
        return None
    ext = file_storage.filename.rsplit(".", 1)[-1].lower() if "." in file_storage.filename else ""
    if ext not in PROFILE_EXT:
        raise ValueError("Unsupported photo type. Please upload an image (JPG, PNG, WEBP or GIF).")
    try:
        file_storage.stream.seek(0)
        with Image.open(file_storage.stream) as image:
            image.thumbnail((256, 256))
            if image.mode in ("RGBA", "LA", "P"):
                image = image.convert("RGBA")
            else:
                image = image.convert("RGB")
            filename = f"{uuid.uuid4().hex}.png"
            image.save(os.path.join(PROFILE_DIR, filename), "PNG")
    except Exception:
        raise ValueError("The photo could not be read. Please choose a valid image.") from ValueError
    finally:
        file_storage.stream.seek(0)
    return filename


def _remove_profile_file(filename):
    if not filename:
        return
    try:
        os.remove(os.path.join(PROFILE_DIR, filename))
    except OSError:
        pass


def profile_photo_url(user):
    """Uploaded profile photo, or a Gravatar derived from the user's email."""
    photo = getattr(user, "profile_photo", None)
    if photo:
        return url_for("static", filename="profile/" + photo)
    email = (getattr(user, "email", "") or "").strip().lower()
    if not email:
        return None
    digest = hashlib.md5(email.encode("utf-8")).hexdigest()
    return f"https://www.gravatar.com/avatar/{digest}?d=identicon&s=128"


app.jinja_env.globals["profile_photo_url"] = profile_photo_url


def _rational_to_float(value):
    if hasattr(value, "numerator") and hasattr(value, "denominator"):
        return float(value.numerator) / float(value.denominator)
    return float(value)


def _gps_coordinate(values, reference):
    if not values or reference not in ("N", "S", "E", "W"):
        return None
    degrees, minutes, seconds = (_rational_to_float(value) for value in values)
    coordinate = degrees + minutes / 60 + seconds / 3600
    return -coordinate if reference in ("S", "W") else coordinate


def read_image_metadata(file_storage):
    """Read EXIF capture details and GPS coordinates from an uploaded image."""
    try:
        file_storage.stream.seek(0)
        with Image.open(file_storage.stream) as image:
            exif = image.getexif()
            gps_info = exif.get_ifd(ExifTags.IFD.GPSInfo) if exif else {}
            metadata = {
                "taken_at": exif.get(36867) or exif.get(306),
                "camera_make": exif.get(271),
                "camera_model": exif.get(272),
                "gps_latitude": _gps_coordinate(gps_info.get(2), gps_info.get(1)),
                "gps_longitude": _gps_coordinate(gps_info.get(4), gps_info.get(3)),
            }
            return {key: value for key, value in metadata.items() if value is not None}
    except (OSError, ValueError, ZeroDivisionError, KeyError, TypeError) as error:
        raise ValueError("The uploaded image could not be read. Please choose a valid image.") from error
    finally:
        file_storage.stream.seek(0)


def distance_between_coordinates(latitude_a, longitude_a, latitude_b, longitude_b):
    earth_radius = 6371000
    lat_a, lat_b = math.radians(latitude_a), math.radians(latitude_b)
    delta_lat = math.radians(latitude_b - latitude_a)
    delta_lon = math.radians(longitude_b - longitude_a)
    haversine = (math.sin(delta_lat / 2) ** 2 +
                 math.cos(lat_a) * math.cos(lat_b) * math.sin(delta_lon / 2) ** 2)
    return 2 * earth_radius * math.asin(math.sqrt(haversine))


def role_required(*roles):
    def decorator(fn):
        @wraps(fn)
        def wrapper(*args, **kwargs):
            if g.current_user is None:
                flash("Please log in to continue.", "error")
                return redirect(url_for("landing"))
            if g.current_user.role not in roles:
                abort(403)
            return fn(*args, **kwargs)
        return wrapper
    return decorator


def login_required(fn):
    @wraps(fn)
    def wrapper(*args, **kwargs):
        if g.current_user is None:
            flash("Please log in to continue.", "error")
            return redirect(url_for("landing"))
        return fn(*args, **kwargs)
    return wrapper


@app.route("/uploads/<path:filename>")
@login_required
def uploaded_file(filename):
    return send_from_directory(UPLOAD_DIR, filename)


# ---------------------------------------------------------------------------
# public / auth
# ---------------------------------------------------------------------------

@app.route("/")
def landing():
    if g.current_user:
        return redirect(url_for(f"{g.current_user.role}_dashboard"))
    conn = db.get_db()
    total = conn.execute("SELECT COUNT(*) c FROM complaints").fetchone()["c"]
    resolved = conn.execute("SELECT COUNT(*) c FROM complaints WHERE status='Resolved'").fetchone()["c"]
    open_ = conn.execute("SELECT COUNT(*) c FROM complaints WHERE status NOT IN ('Resolved','Rejected')").fetchone()["c"]
    stats = {"total": total, "resolved": resolved, "open": open_}
    return render_template("landing.html", stats=stats)


@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        name = request.form.get("name", "").strip()
        email = request.form.get("email", "").strip().lower()
        phone = request.form.get("phone", "").strip()
        password = request.form.get("password", "")

        if not (name and email and phone and password):
            flash("Please fill in every field.", "error")
            return render_template("register.html")

        conn = db.get_db()
        if db.get_user_by_email(conn, email):
            flash("An account with this email already exists. Please log in instead.", "error")
            return render_template("register.html")

        user_id = db.create_user(conn, name, email, phone, password, "citizen")
        session.permanent = True
        session["user_id"] = user_id
        flash(f"Welcome, {name}! Your citizen account is ready.", "success")
        return redirect(url_for("citizen_dashboard"))

    return render_template("register.html")


@app.route("/login", methods=["GET", "POST"])
@app.route("/login/<role>", methods=["GET", "POST"])
def login(role=None):
    if request.method == "POST" and role is None:
        role = request.form.get("role", "")
    if role not in db.ROLES:
        if request.method == "POST":
            flash("Please choose a valid login type.", "error")
        return render_template("login.html", role=None)

    if request.method == "POST":
        email = request.form.get("email", "").strip().lower()
        password = request.form.get("password", "")
        conn = db.get_db()
        user = db.get_user_by_email_role(conn, email, role)

        if user and db.verify_password(user, password):
            session.permanent = True
            session["user_id"] = user["id"]
            flash(f"Welcome back, {user['name']}.", "success")
            return redirect(url_for(f"{role}_dashboard"))

        flash("Invalid email or password for this login.", "error")

    return render_template("login.html", role=role)


@app.route("/logout")
@login_required
def logout():
    session.clear()
    return redirect(url_for("landing"))


# ---------------------------------------------------------------------------
# account / profile
# ---------------------------------------------------------------------------

@app.route("/account", methods=["GET", "POST"])
@login_required
def account():
    conn = db.get_db()
    user = g.current_user

    if request.method == "POST":
        name = request.form.get("name", "").strip()
        email = request.form.get("email", "").strip().lower()
        phone = request.form.get("phone", "").strip()
        alternate_phone = request.form.get("alternate_phone", "").strip()
        home_address = request.form.get("home_address", "").strip()

        errors = []
        if not (name and email and phone):
            errors.append("Please fill in your name, email and phone number.")
        existing = db.get_user_by_email(conn, email)
        if existing and existing["id"] != user.id:
            errors.append("That email is already used by another account.")

        action = request.form.get("action", "")
        photo = request.files.get("profile_photo")
        new_photo = None
        if photo and photo.filename:
            try:
                new_photo = save_profile_photo(photo)
            except ValueError as error:
                errors.append(str(error))

        if not errors:
            db.update_user_account(conn, user.id, name, email, phone, alternate_phone, home_address)
            if action == "remove_photo":
                _remove_profile_file(user.profile_photo)
                db.clear_profile_photo(conn, user.id)
            elif new_photo:
                _remove_profile_file(user.profile_photo)
                db.set_profile_photo(conn, user.id, new_photo)

        for message in errors:
            flash(message, "error")
        if not errors:
            flash(i18n.t("photo_removed") if action == "remove_photo" else i18n.t("account_updated"), "success")

        user = db.hydrate_user(db.get_user_by_id(conn, user.id))
        g.current_user = user

    return render_template("account.html", user=user)


# ---------------------------------------------------------------------------
# citizen
# ---------------------------------------------------------------------------

@app.route("/citizen")
@role_required("citizen")
def citizen_dashboard():
    conn = db.get_db()
    complaints = db.list_by_citizen(conn, g.current_user.id)
    return render_template("citizen_dashboard.html", complaints=complaints)


@app.route("/citizen/report", methods=["GET", "POST"])
@role_required("citizen")
def report_problem():
    if request.method == "POST":
        title = request.form.get("title", "").strip()
        description = request.form.get("description", "").strip()
        category = request.form.get("category", db.CATEGORIES[0])
        district = request.form.get("district", "").strip()
        location_text = request.form.get("location_text", "").strip()
        latitude = request.form.get("latitude", "").strip()
        longitude = request.form.get("longitude", "").strip()
        location_address = request.form.get("location_address", "").strip()
        location_city = request.form.get("location_city", "").strip()
        location_state = request.form.get("location_state", "").strip()
        pincode = request.form.get("pincode", "").strip()

        if not (title and description):
            flash("Please add a title and description of the problem.", "error")
            return render_template("report_problem.html", categories=db.CATEGORIES, districts=db.DISTRICTS)

        try:
            latitude = float(latitude)
            longitude = float(longitude)
            if not (-90 <= latitude <= 90 and -180 <= longitude <= 180):
                raise ValueError
        except (TypeError, ValueError):
            flash("Please share your current location or select the problem location on the map.", "error")
            return render_template("report_problem.html", categories=db.CATEGORIES, districts=db.DISTRICTS)
        if district not in db.DISTRICTS:
            flash("Please confirm the district detected for this location or select it manually.", "error")
            return render_template("report_problem.html", categories=db.CATEGORIES, districts=db.DISTRICTS)
        if pincode and (not pincode.isdigit() or len(pincode) != 6):
            flash("Please enter a valid 6-digit pincode.", "error")
            return render_template("report_problem.html", categories=db.CATEGORIES, districts=db.DISTRICTS)

        evidence = request.files.get("camera_evidence")
        if not evidence or not evidence.filename:
            evidence = request.files.get("evidence")
        image_metadata = {}
        image_latitude = None
        image_longitude = None
        if evidence and evidence.filename:
            evidence_ext = evidence.filename.rsplit(".", 1)[-1].lower() if "." in evidence.filename else ""
            if evidence_ext not in VIDEO_EXT:
                try:
                    image_metadata = read_image_metadata(evidence)
                except ValueError as error:
                    flash(str(error), "error")
                    return render_template("report_problem.html", categories=db.CATEGORIES, districts=db.DISTRICTS)
                image_latitude = image_metadata.get("gps_latitude")
                image_longitude = image_metadata.get("gps_longitude")
                if image_latitude is not None and image_longitude is not None:
                    distance = distance_between_coordinates(latitude, longitude, image_latitude, image_longitude)
                    if distance > IMAGE_LOCATION_TOLERANCE_METERS:
                        flash("The image location does not match the problem location. Please select the correct spot on the map or verify the photo is from this location.", "error")
                        return render_template("report_problem.html", categories=db.CATEGORIES, districts=db.DISTRICTS)
        try:
            filename, is_video = save_upload(evidence)
        except ValueError as e:
            flash(str(e), "error")
            return render_template("report_problem.html", categories=db.CATEGORIES, districts=db.DISTRICTS)

        if not filename:
            flash("Please attach a photo or video of the problem — this is required for verification.", "error")
            return render_template("report_problem.html", categories=db.CATEGORIES, districts=db.DISTRICTS)

        conn = db.get_db()
        code = db.new_complaint_code(conn)
        complaint_id = db.create_complaint(
            conn, code=code, title=title, description=description, category=category,
            district=district, location_text=location_text, latitude=latitude, longitude=longitude,
            location_address=location_address, location_city=location_city,
            location_state=location_state, pincode=pincode,
            image_metadata=json.dumps(image_metadata) if image_metadata else None,
            image_taken_at=image_metadata.get("taken_at"), image_latitude=image_latitude,
            image_longitude=image_longitude, photo_filename=filename,
            is_photo_video=int(is_video), citizen_id=g.current_user.id, status="Submitted",
        )
        db.add_log(conn, complaint_id, "Submitted",
                    f"Filed by {g.current_user.name} ({g.current_user.phone}, {g.current_user.email}).")
        if not is_video and (image_latitude is None or image_longitude is None):
            db.add_log(conn, complaint_id, "Submitted",
                        "The uploaded photo carried no GPS location tag; the location selected on the map was recorded instead.")

        # --- automatic AI screening: photo vs the reported problem ---
        if not is_video:
            photo_path = os.path.join(UPLOAD_DIR, filename)
            verdict = ai_engine.verify_image_against_problem(photo_path, title, description, category)
            new_status = "AI Verified" if verdict["verified"] else "Pending Officer Review"
            db.set_status(conn, complaint_id, new_status, verdict["note"],
                          extra_fields={
                              "ai_confidence": verdict["confidence"],
                              "ai_note": verdict["note"],
                              "ai_detail": json.dumps(verdict, ensure_ascii=False),
                          })
        else:
            note = ("Video evidence was submitted. Automated image verification cannot "
                     "inspect videos, so this was routed for officer verification.")
            db.set_status(conn, complaint_id, "Pending Officer Review", note,
                          extra_fields={"ai_note": note})

        flash(f"Problem submitted as #{code}.", "success")
        return redirect(url_for("track_complaint", code=code))

    return render_template("report_problem.html", categories=db.CATEGORIES, districts=db.DISTRICTS)


@app.route("/citizen/complaint/<code>")
@login_required
def track_complaint(code):
    conn = db.get_db()
    row = db.get_complaint_row(conn, code=code)
    if row is None:
        abort(404)
    complaint = db.hydrate_complaint(conn, row, with_relations=True)
    if g.current_user.role == "citizen" and complaint.citizen_id != g.current_user.id:
        abort(403)
    return render_template("track_complaint.html", c=complaint)


# ---------------------------------------------------------------------------
# officer
# ---------------------------------------------------------------------------

@app.route("/officer")
@role_required("officer")
def officer_dashboard():
    conn = db.get_db()
    queue = db.list_queue(conn)
    my_cases = db.list_my_cases(conn, g.current_user.id)
    resolved = db.list_resolved_by(conn, g.current_user.id)
    return render_template("officer_dashboard.html", queue=queue, my_cases=my_cases, resolved=resolved)


@app.route("/officer/complaint/<code>")
@role_required("officer")
def officer_complaint(code):
    conn = db.get_db()
    row = db.get_complaint_row(conn, code=code)
    if row is None:
        abort(404)
    complaint = db.hydrate_complaint(conn, row, with_relations=True)
    return render_template("officer_complaint.html", c=complaint)


@app.route("/officer/complaint/<code>/accept", methods=["POST"])
@role_required("officer")
def officer_accept(code):
    conn = db.get_db()
    row = db.get_complaint_row(conn, code=code)
    if row is None:
        abort(404)
    deadline = datetime.utcnow() + timedelta(days=db.RESOLUTION_WINDOW_DAYS)
    note = f"Accepted by {g.current_user.name}. Resolution due by {deadline.strftime('%d %b %Y')}."
    db.set_status(conn, row["id"], "Accepted by Officer", note, extra_fields={
        "officer_id": g.current_user.id,
        "accepted_at": datetime.utcnow().isoformat(),
        "deadline": deadline.isoformat(),
    })
    flash("Case accepted. Upload a resolution photo before the deadline.", "success")
    return redirect(url_for("officer_complaint", code=code))


@app.route("/officer/complaint/<code>/reject", methods=["POST"])
@role_required("officer")
def officer_reject(code):
    conn = db.get_db()
    row = db.get_complaint_row(conn, code=code)
    if row is None:
        abort(404)
    reason = request.form.get("reason", "").strip() or "Not a verifiable public infrastructure issue."
    db.set_status(conn, row["id"], "Rejected", f"Rejected by {g.current_user.name}: {reason}",
                  extra_fields={"officer_id": g.current_user.id})
    flash("Complaint rejected.", "success")
    return redirect(url_for("officer_dashboard"))


@app.route("/officer/complaint/<code>/resolve", methods=["POST"])
@role_required("officer")
def officer_resolve(code):
    conn = db.get_db()
    row = db.get_complaint_row(conn, code=code)
    if row is None:
        abort(404)
    if row["officer_id"] != g.current_user.id:
        abort(403)

    evidence = request.files.get("resolution_evidence")
    try:
        filename, is_video = save_upload(evidence)
    except ValueError as e:
        flash(str(e), "error")
        return redirect(url_for("officer_complaint", code=code))

    if not filename:
        flash("Please attach an 'after' photo showing the resolved site.", "error")
        return redirect(url_for("officer_complaint", code=code))

    before_path = os.path.join(UPLOAD_DIR, row["photo_filename"])
    after_path = os.path.join(UPLOAD_DIR, filename)

    if bool(row["is_photo_video"]) or is_video:
        note = ("Automated image comparison isn't available because the before or after "
                 "evidence is a video. Marked resolved on officer confirmation.")
        db.set_status(conn, row["id"], "Resolved", note, extra_fields={
            "resolution_filename": filename, "resolution_note": note,
            "resolved_at": datetime.utcnow().isoformat(),
        })
    else:
        change_score, note = ai_engine.compare_before_after(before_path, after_path)
        if change_score is not None and change_score >= ai_engine.RESOLUTION_CHANGE_THRESHOLD:
            db.set_status(conn, row["id"], "Resolved", note, extra_fields={
                "resolution_filename": filename, "resolution_confidence": change_score,
                "resolution_note": note, "resolved_at": datetime.utcnow().isoformat(),
            })
        else:
            db.set_status(conn, row["id"], "Reopened", note, extra_fields={
                "resolution_filename": filename, "resolution_confidence": change_score,
                "resolution_note": note,
            })

    flash("Resolution evidence submitted and verified.", "success")
    return redirect(url_for("officer_complaint", code=code))


# ---------------------------------------------------------------------------
# admin
# ---------------------------------------------------------------------------

@app.route("/admin")
@role_required("admin")
def admin_dashboard():
    conn = db.get_db()
    complaints = db.list_all_complaints(conn)
    officers = db.list_officers(conn)
    stats = {
        "total": len(complaints),
        "open": len([c for c in complaints if c.status not in ("Resolved", "Rejected")]),
        "resolved": len([c for c in complaints if c.status == "Resolved"]),
        "overdue": len([c for c in complaints if c.is_overdue]),
        "citizens": db.count_users(conn, "citizen"),
        "officers": len(officers),
    }
    return render_template("admin_dashboard.html", complaints=complaints, officers=officers, stats=stats)


@app.route("/admin/officers/create", methods=["POST"])
@role_required("admin")
def admin_create_officer():
    name = request.form.get("name", "").strip()
    email = request.form.get("email", "").strip().lower()
    phone = request.form.get("phone", "").strip()
    password = request.form.get("password", "")

    if not (name and email and phone and password):
        flash("Please fill in every field to create an officer account.", "error")
        return redirect(url_for("admin_dashboard"))

    conn = db.get_db()
    if db.get_user_by_email(conn, email):
        flash("An account with this email already exists.", "error")
        return redirect(url_for("admin_dashboard"))

    db.create_user(conn, name, email, phone, password, "officer")
    flash(f"Officer account created for {name}.", "success")
    return redirect(url_for("admin_dashboard"))


@app.route("/admin/complaint/<code>")
@role_required("admin")
def admin_complaint(code):
    conn = db.get_db()
    row = db.get_complaint_row(conn, code=code)
    if row is None:
        abort(404)
    complaint = db.hydrate_complaint(conn, row, with_relations=True)
    officers = db.list_officers(conn)
    return render_template("admin_complaint.html", c=complaint, officers=officers)


@app.route("/admin/complaint/<code>/assign", methods=["POST"])
@role_required("admin")
def admin_assign(code):
    conn = db.get_db()
    row = db.get_complaint_row(conn, code=code)
    if row is None:
        abort(404)
    officer_id = request.form.get("officer_id")
    officer = db.get_user_by_id(conn, int(officer_id)) if officer_id else None
    if not officer or officer["role"] != "officer":
        flash("Please select a valid officer.", "error")
        return redirect(url_for("admin_complaint", code=code))

    deadline = datetime.utcnow() + timedelta(days=db.RESOLUTION_WINDOW_DAYS)
    note = f"Manually assigned to {officer['name']} by admin. Due {deadline.strftime('%d %b %Y')}."
    db.set_status(conn, row["id"], "Accepted by Officer", note, extra_fields={
        "officer_id": officer["id"],
        "accepted_at": datetime.utcnow().isoformat(),
        "deadline": deadline.isoformat(),
    })
    flash(f"Assigned to {officer['name']}.", "success")
    return redirect(url_for("admin_complaint", code=code))


# ---------------------------------------------------------------------------
# seed data (runs once, only if DB is empty)
# ---------------------------------------------------------------------------

def seed_if_empty():
    conn = sqlite3.connect(db.DB_PATH)
    conn.row_factory = sqlite3.Row
    has_user = conn.execute("SELECT 1 FROM users LIMIT 1").fetchone()
    if has_user:
        conn.close()
        return

    db.create_user(conn, "Admin", "admin@jsamadhan.gov", "9000000000", "admin123", "admin")
    db.create_user(conn, "Officer Verma", "officer1@jsamadhan.gov", "9000000001", "officer123", "officer")
    db.create_user(conn, "Officer Kujur", "officer2@jsamadhan.gov", "9000000002", "officer123", "officer")
    db.create_user(conn, "Rahul", "citizen@example.com", "9800000000", "citizen123", "citizen")
    conn.close()

    print("Seeded demo accounts:")
    print("  Admin    -> admin@jsamadhan.gov / admin123")
    print("  Officer  -> officer1@jsamadhan.gov / officer123")
    print("  Officer  -> officer2@jsamadhan.gov / officer123")
    print("  Citizen  -> citizen@example.com / citizen123")


seed_if_empty()


if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=5000)
