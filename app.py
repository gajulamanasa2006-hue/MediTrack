import os
import uuid
from datetime import date, datetime, timedelta
from functools import wraps
from sqlalchemy.engine import URL


import jwt
import qrcode
from flask import (
    Flask,
    flash,
    g,
    jsonify,
    redirect,
    render_template,
    render_template_string,
    request,
    session,
    url_for,
)
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import or_
from werkzeug.security import check_password_hash, generate_password_hash
from werkzeug.utils import secure_filename

BASE_DIR = os.path.abspath(os.path.dirname(__file__))

app = Flask(__name__)
app.config["SECRET_KEY"] = os.getenv("SECRET_KEY", "meditrack-dev-secret")
app.config["SQLALCHEMY_DATABASE_URI"] = URL.create(
    drivername="mysql+pymysql",
    username="root",
    password="Manasa@1026",
    host="localhost",
    database="meditrack_db",
)
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
app.config["UPLOAD_FOLDER"] = os.path.join(BASE_DIR, "static", "uploads")
app.config["MAX_CONTENT_LENGTH"] = 2 * 1024 * 1024

# --- Milestone 3 addition: JWT configuration (additive) --------------------
app.config["JWT_SECRET"] = os.getenv("JWT_SECRET", app.config["SECRET_KEY"])
app.config["JWT_ALGORITHM"] = "HS256"
app.config["JWT_EXP_MINUTES"] = 120
# --- End Milestone 3 addition ------------------------------------------

os.makedirs(os.path.join(app.config["UPLOAD_FOLDER"], "profiles"), exist_ok=True)
os.makedirs(os.path.join(app.config["UPLOAD_FOLDER"], "qrcodes"), exist_ok=True)

db = SQLAlchemy(app)

DEPARTMENTS = {
    "General Medicine": ["Dr. Ethan Brooks", "Dr. Maya Reid"],
    "Cardiology": ["Dr. Amelia Carter", "Dr. Noah Patel"],
    "Neurology": ["Dr. Chloe Bennett", "Dr. Lucas Hayes"],
    "Orthopedics": ["Dr. Olivia Stone", "Dr. Mason Clarke"],
    "Dermatology": ["Dr. Ava Collins", "Dr. Logan Murphy"],
}

TIME_SLOTS = [
    "09:00 AM - 09:30 AM",
    "09:30 AM - 10:00 AM",
    "10:00 AM - 10:30 AM",
    "10:30 AM - 11:00 AM",
    "11:00 AM - 11:30 AM",
    "11:30 AM - 12:00 PM",
    "02:00 PM - 02:30 PM",
    "02:30 PM - 03:00 PM",
    "03:00 PM - 03:30 PM",
    "03:30 PM - 04:00 PM",
]

PROFILE_FIELDS = {
    "blood_group": "Blood Group",
    "height": "Height",
    "weight": "Weight",
    "bmi": "BMI",
    "blood_pressure": "Blood Pressure",
    "pulse_rate": "Pulse Rate",
    "oxygen_level": "Oxygen Saturation",
    "allergies": "Allergies",
    "diseases": "Existing Diseases",
    "previous_history": "Previous Medical History",
    "surgeries": "Previous Surgeries",
    "medications": "Current Medications",
    "family_history": "Family Medical History",
    "lifestyle": "Lifestyle",
    "emergency_contact_name": "Emergency Contact Name",
    "emergency_contact_phone": "Emergency Contact Number",
}


class Patient(db.Model):
    __tablename__ = "patients"

    id = db.Column(db.Integer, primary_key=True)
    patient_id = db.Column(db.String(20), unique=True, nullable=False)
    first_name = db.Column(db.String(80), nullable=False)
    last_name = db.Column(db.String(80), nullable=False)
    age = db.Column(db.Integer, nullable=False)
    gender = db.Column(db.String(20), nullable=False)
    dob = db.Column(db.Date, nullable=False)
    phone = db.Column(db.String(20), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    address = db.Column(db.Text, nullable=False)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password = db.Column(db.String(255), nullable=False)
    qr_code_path = db.Column(db.String(255))
    is_active = db.Column(db.Boolean, default=True, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)

    profile = db.relationship(
        "PatientProfile",
        back_populates="patient",
        uselist=False,
        cascade="all, delete-orphan",
    )
    appointments = db.relationship(
        "Appointment", back_populates="patient", cascade="all, delete-orphan"
    )

    @property
    def full_name(self):
        return f"{self.first_name} {self.last_name}"


class PatientProfile(db.Model):
    __tablename__ = "patient_profiles"

    profile_id = db.Column(db.Integer, primary_key=True)
    patient_id = db.Column(
        db.String(20), db.ForeignKey("patients.patient_id"), unique=True, nullable=False
    )
    blood_group = db.Column(db.String(10))
    height = db.Column(db.Numeric(6, 2))
    weight = db.Column(db.Numeric(6, 2))
    bmi = db.Column(db.Numeric(6, 2))
    blood_pressure = db.Column(db.String(30))
    pulse_rate = db.Column(db.String(30))
    oxygen_level = db.Column(db.String(30))
    allergies = db.Column(db.Text)
    diseases = db.Column(db.Text)
    previous_history = db.Column(db.Text)
    surgeries = db.Column(db.Text)
    medications = db.Column(db.Text)
    family_history = db.Column(db.Text)
    lifestyle = db.Column(db.String(120))
    emergency_contact_name = db.Column(db.String(120))
    emergency_contact_phone = db.Column(db.String(20))
    profile_photo = db.Column(db.String(255))
    last_updated = db.Column(
        db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False
    )

    patient = db.relationship("Patient", back_populates="profile")


class Appointment(db.Model):
    __tablename__ = "appointments"

    id = db.Column(db.Integer, primary_key=True)
    appointment_id = db.Column(db.String(20), unique=True, nullable=False)
    patient_id = db.Column(
        db.String(20), db.ForeignKey("patients.patient_id"), nullable=False
    )
    department = db.Column(db.String(120), nullable=False)
    doctor = db.Column(db.String(120), nullable=False)
    appointment_date = db.Column(db.Date, nullable=False)
    time_slot = db.Column(db.String(40), nullable=False)
    reason = db.Column(db.Text, nullable=False)
    status = db.Column(db.String(20), default="Confirmed", nullable=False)
    waiting_position = db.Column(db.Integer, default=1, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    updated_at = db.Column(
        db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False
    )

    patient = db.relationship("Patient", back_populates="appointments")


# ---------------------------------------------------------------------------
# Milestone 2 additions: Consultations & Prescriptions
# (Appended without altering any existing models/routes above.)
# ---------------------------------------------------------------------------

class Consultation(db.Model):
    __tablename__ = "consultations"

    id = db.Column(db.Integer, primary_key=True)
    consultation_id = db.Column(db.String(20), unique=True, nullable=False)
    patient_id = db.Column(
        db.String(20), db.ForeignKey("patients.patient_id"), nullable=False
    )
    appointment_id = db.Column(
        db.String(20), db.ForeignKey("appointments.appointment_id"), nullable=True
    )
    doctor = db.Column(db.String(120), nullable=False)
    symptoms = db.Column(db.Text, nullable=False)
    diagnosis = db.Column(db.Text, nullable=False)
    treatment = db.Column(db.Text, nullable=False)
    consultation_date = db.Column(db.Date, nullable=False)
    notes = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)

    patient = db.relationship("Patient", backref=db.backref("consultations", cascade="all, delete-orphan"))
    appointment = db.relationship("Appointment", backref=db.backref("consultations"))
    prescriptions = db.relationship(
        "Prescription", back_populates="consultation", cascade="all, delete-orphan"
    )


class Prescription(db.Model):
    __tablename__ = "prescriptions"

    id = db.Column(db.Integer, primary_key=True)
    prescription_id = db.Column(db.String(20), unique=True, nullable=False)
    patient_id = db.Column(
        db.String(20), db.ForeignKey("patients.patient_id"), nullable=False
    )
    doctor = db.Column(db.String(120), nullable=False)
    consultation_id = db.Column(
        db.String(20), db.ForeignKey("consultations.consultation_id"), nullable=True
    )
    prescription_date = db.Column(db.Date, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)

    patient = db.relationship("Patient", backref=db.backref("prescriptions", cascade="all, delete-orphan"))
    consultation = db.relationship("Consultation", back_populates="prescriptions")
    items = db.relationship(
        "PrescriptionItem", back_populates="prescription", cascade="all, delete-orphan",
        order_by="PrescriptionItem.id",
    )


class PrescriptionItem(db.Model):
    __tablename__ = "prescription_items"

    id = db.Column(db.Integer, primary_key=True)
    prescription_id = db.Column(
        db.String(20), db.ForeignKey("prescriptions.prescription_id"), nullable=False
    )
    medicine_name = db.Column(db.String(150), nullable=False)
    dosage = db.Column(db.String(80), nullable=False)
    frequency = db.Column(db.String(80), nullable=False)
    duration = db.Column(db.String(80), nullable=False)
    instructions = db.Column(db.String(255))

    prescription = db.relationship("Prescription", back_populates="items")


# ---------------------------------------------------------------------------
# Milestone 3 additions: Staff accounts, Notifications, Audit Logs, Security
# (Appended without altering any existing models above.)
# ---------------------------------------------------------------------------

class Staff(db.Model):
    __tablename__ = "staff"

    id = db.Column(db.Integer, primary_key=True)
    staff_id = db.Column(db.String(20), unique=True, nullable=False)
    name = db.Column(db.String(120), nullable=False)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.String(255), nullable=False)
    role = db.Column(db.String(20), nullable=False)  # 'doctor' or 'admin'
    specialization = db.Column(db.String(120))
    is_active = db.Column(db.Boolean, default=True, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)


class Notification(db.Model):
    __tablename__ = "notifications"

    id = db.Column(db.Integer, primary_key=True)
    patient_id = db.Column(
        db.String(20), db.ForeignKey("patients.patient_id"), nullable=False
    )
    notif_type = db.Column(db.String(40), nullable=False)
    title = db.Column(db.String(150), nullable=False)
    message = db.Column(db.Text, nullable=False)
    related_type = db.Column(db.String(40))
    related_id = db.Column(db.String(20))
    is_read = db.Column(db.Boolean, default=False, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)

    patient = db.relationship("Patient", backref=db.backref("notifications", cascade="all, delete-orphan"))


class AuditLog(db.Model):
    __tablename__ = "audit_logs"

    id = db.Column(db.Integer, primary_key=True)
    actor_label = db.Column(db.String(160), nullable=False)
    actor_role = db.Column(db.String(20), nullable=False)
    action = db.Column(db.String(80), nullable=False)
    resource = db.Column(db.String(80))
    resource_id = db.Column(db.String(60))
    ip_address = db.Column(db.String(64))
    details = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)


class SecurityEvent(db.Model):
    __tablename__ = "security_events"

    id = db.Column(db.Integer, primary_key=True)
    event_type = db.Column(db.String(60), nullable=False)
    severity = db.Column(db.String(20), nullable=False, default="medium")
    username = db.Column(db.String(120))
    ip_address = db.Column(db.String(64))
    details = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)


# --- End Milestone 3 model additions --------------------------------------


with app.app_context():
    db.create_all()

    # One-time, idempotent seeding of default clinical staff accounts so the
    # doctor/admin workflow is usable immediately after setup. Safe to run
    # every startup: it only inserts rows when the staff table is empty.
    if Staff.query.count() == 0:
        db.session.add_all(
            [
                Staff(
                    staff_id="ADM001",
                    name="System Administrator",
                    username="admin",
                    email="admin@meditrack.local",
                    password=generate_password_hash("Admin@123"),
                    role="admin",
                    specialization=None,
                ),
                Staff(
                    staff_id="DOC001",
                    name="Dr. Amelia Carter",
                    username="doctor01",
                    email="amelia.carter@meditrack.local",
                    password=generate_password_hash("Doctor@123"),
                    role="doctor",
                    specialization="Cardiology",
                ),
            ]
        )
        db.session.commit()


def login_required(view_func):
    @wraps(view_func)
    def wrapped(*args, **kwargs):
        # Milestone 3: a session may belong to either a patient or a staff (doctor/admin) account.
        if not (session.get("patient_key") or session.get("staff_key")):
            flash("Please sign in to continue.", "warning")
            return redirect(url_for("login"))
        return view_func(*args, **kwargs)

    return wrapped


def current_patient():
    return Patient.query.filter_by(id=session.get("patient_key")).first()


def current_staff():
    return Staff.query.filter_by(id=session.get("staff_key")).first()


def next_code(model, prefix):
    latest = model.query.order_by(model.id.desc()).first()
    if not latest:
        return f"{prefix}001"
    source = latest.patient_id if prefix == "PAT" else latest.appointment_id
    current_num = int(source.replace(prefix, ""))
    return f"{prefix}{current_num + 1:03d}"


def profile_completion(profile):
    if not profile:
        return 0
    completed = 0
    total = len(PROFILE_FIELDS) + 1
    for field in PROFILE_FIELDS:
        value = getattr(profile, field)
        if value not in (None, ""):
            completed += 1
    if profile.profile_photo:
        completed += 1
    return round((completed / total) * 100)


def missing_profile_fields(profile):
    if not profile:
        return list(PROFILE_FIELDS.values()) + ["Profile Photo"]
    missing = [label for field, label in PROFILE_FIELDS.items() if getattr(profile, field) in (None, "")]
    if not profile.profile_photo:
        missing.append("Profile Photo")
    return missing


def save_profile_photo(file_storage):
    if not file_storage or not file_storage.filename:
        return None
    extension = os.path.splitext(secure_filename(file_storage.filename))[1].lower()
    filename = f"profile_{uuid.uuid4().hex}{extension}"
    relative_path = os.path.join("uploads", "profiles", filename)
    absolute_path = os.path.join(app.static_folder, relative_path)
    file_storage.save(absolute_path)
    return relative_path.replace("\\", "/")


def generate_qr_code(patient):
    target_url = url_for("patient_lookup", patient_id=patient.patient_id, _external=True)
    qr = qrcode.QRCode(box_size=8, border=2)
    qr.add_data(target_url)
    qr.make(fit=True)
    image = qr.make_image(fill_color="#0d6efd", back_color="white")
    relative_path = os.path.join("uploads", "qrcodes", f"{patient.patient_id}.png")
    absolute_path = os.path.join(app.static_folder, relative_path)
    image.save(absolute_path)
    patient.qr_code_path = relative_path.replace("\\", "/")


def recalculate_bmi(height, weight):
    try:
        height_value = float(height)
        weight_value = float(weight)
        if height_value > 0 and weight_value > 0:
            return round(weight_value / ((height_value / 100) ** 2), 2)
    except (TypeError, ValueError):
        return None
    return None


def update_completed_appointments():
    today = date.today()
    changed = False
    appointments = Appointment.query.filter(
        Appointment.status.in_(["Confirmed", "Pending"]),
        Appointment.appointment_date < today,
    ).all()
    for appointment in appointments:
        # Milestone 3: an appointment that was never confirmed and whose date
        # has passed is treated as "missed" rather than silently completed,
        # and the patient is notified.
        if appointment.status == "Pending":
            appointment.status = "Missed"
            create_notification(
                appointment.patient_id,
                "missed_appointment",
                "Missed appointment",
                f"You missed your appointment with {appointment.doctor} on "
                f"{appointment.appointment_date.strftime('%d %b %Y')}. Please reschedule.",
                related_type="appointment",
                related_id=appointment.appointment_id,
            )
        else:
            appointment.status = "Completed"
        changed = True
    if changed:
        db.session.commit()


def available_slots(doctor_name, target_date, exclude_appointment_id=None):
    query = Appointment.query.filter(
        Appointment.doctor == doctor_name,
        Appointment.appointment_date == target_date,
        Appointment.status != "Cancelled",
    )
    if exclude_appointment_id:
        query = query.filter(Appointment.id != exclude_appointment_id)
    booked_slots = {item.time_slot for item in query.all()}
    return [slot for slot in TIME_SLOTS if slot not in booked_slots]


def waiting_position(doctor_name, target_date, exclude_appointment_id=None):
    query = Appointment.query.filter(
        Appointment.doctor == doctor_name,
        Appointment.appointment_date == target_date,
        Appointment.status != "Cancelled",
    )
    if exclude_appointment_id:
        query = query.filter(Appointment.id != exclude_appointment_id)
    return query.count() + 1


# --- Milestone 2 helpers -----------------------------------------------

ALL_DOCTORS = sorted({doctor for doctors in DEPARTMENTS.values() for doctor in doctors})


def generate_prefixed_id(model, id_column, prefix):
    """Generic CONxxx / RXxxx style ID generator (mirrors next_code, but reusable for any model)."""
    latest = model.query.order_by(model.id.desc()).first()
    if not latest:
        return f"{prefix}001"
    source = getattr(latest, id_column)
    current_num = int(source.replace(prefix, ""))
    return f"{prefix}{current_num + 1:03d}"


def get_patient_or_none(patient_id):
    if not patient_id:
        return None
    return Patient.query.filter_by(patient_id=patient_id).first()


# --- End Milestone 2 helpers ---------------------------------------------


# ---------------------------------------------------------------------------
# Milestone 3 helpers: Audit Logging, Security Monitoring, RBAC, JWT, Notifications
# (Appended without altering any existing helper above.)
# ---------------------------------------------------------------------------

def _current_actor():
    """Return (label, role) for whoever is making the current request, across
    session-based (web) and JWT-based (API) auth."""
    if session.get("patient_id"):
        return f"{session.get('patient_name')} ({session.get('patient_id')})", "patient"
    if session.get("staff_id"):
        return f"{session.get('staff_name')} ({session.get('staff_id')})", session.get("role", "staff")
    jwt_subject = getattr(g, "jwt_subject", None)
    jwt_role = getattr(g, "jwt_role", None)
    if jwt_subject:
        return f"API:{jwt_subject}", jwt_role or "unknown"
    return "Anonymous", "anonymous"


def log_audit(action, resource=None, resource_id=None, details=None):
    """Record a tamper-evident trail of who did what, when. Called from both
    the session-based web routes and the JWT-protected REST API."""
    actor_label, actor_role = _current_actor()
    entry = AuditLog(
        actor_label=actor_label,
        actor_role=actor_role,
        action=action,
        resource=resource,
        resource_id=str(resource_id) if resource_id is not None else None,
        ip_address=request.remote_addr,
        details=details,
    )
    db.session.add(entry)
    db.session.commit()


def log_security_event(event_type, severity, username, details=None):
    entry = SecurityEvent(
        event_type=event_type,
        severity=severity,
        username=username,
        ip_address=request.remote_addr,
        details=details,
    )
    db.session.add(entry)
    db.session.commit()


def track_failed_login(username):
    """Log a failed login attempt and escalate to a brute-force security
    event if the same username fails repeatedly within a short window."""
    log_security_event("FAILED_LOGIN", "medium", username, "Invalid credentials provided.")
    window_start = datetime.utcnow() - timedelta(minutes=10)
    recent_failures = SecurityEvent.query.filter(
        SecurityEvent.event_type == "FAILED_LOGIN",
        SecurityEvent.username == username,
        SecurityEvent.created_at >= window_start,
    ).count()
    if recent_failures >= 5:
        log_security_event(
            "BRUTE_FORCE_SUSPECTED",
            "high",
            username,
            f"{recent_failures} failed login attempts for this username within 10 minutes.",
        )


def role_required(*roles):
    """Web-route (session-based) RBAC gate. Unlike login_required, this also
    enforces WHICH role may view the page and logs a security event + audit
    trail entry whenever someone is blocked."""
    def decorator(view_func):
        @wraps(view_func)
        def wrapped(*args, **kwargs):
            if not (session.get("patient_key") or session.get("staff_key")):
                flash("Please sign in to continue.", "warning")
                return redirect(url_for("login"))
            if session.get("role") not in roles:
                identity = session.get("patient_id") or session.get("staff_id")
                log_security_event(
                    "UNAUTHORIZED_PAGE_ACCESS",
                    "high",
                    identity,
                    f"role={session.get('role')} attempted to access {request.path}",
                )
                log_audit("UNAUTHORIZED_ACCESS_ATTEMPT", "Page", request.path, f"Blocked role={session.get('role')}")
                flash("You do not have permission to access that page.", "error")
                return redirect(url_for("dashboard"))
            return view_func(*args, **kwargs)
        return wrapped
    return decorator


# --- JWT authentication for the REST API -----------------------------------

def generate_jwt(subject, role, subject_type):
    payload = {
        "sub": subject,
        "role": role,
        "type": subject_type,
        "iat": datetime.utcnow(),
        "exp": datetime.utcnow() + timedelta(minutes=app.config["JWT_EXP_MINUTES"]),
    }
    return jwt.encode(payload, app.config["JWT_SECRET"], algorithm=app.config["JWT_ALGORITHM"])


def token_required(view_func):
    @wraps(view_func)
    def wrapped(*args, **kwargs):
        auth_header = request.headers.get("Authorization", "")
        token = auth_header.split(" ", 1)[1].strip() if auth_header.startswith("Bearer ") else None
        if not token:
            log_security_event("MISSING_TOKEN", "medium", None, f"{request.method} {request.path}")
            return jsonify({"error": "Authorization token is required."}), 401
        try:
            payload = jwt.decode(token, app.config["JWT_SECRET"], algorithms=[app.config["JWT_ALGORITHM"]])
        except jwt.ExpiredSignatureError:
            return jsonify({"error": "Token has expired. Please log in again."}), 401
        except jwt.InvalidTokenError:
            log_security_event("INVALID_TOKEN", "high", None, f"{request.method} {request.path}")
            return jsonify({"error": "Invalid token."}), 401
        g.jwt_subject = payload.get("sub")
        g.jwt_role = payload.get("role")
        g.jwt_type = payload.get("type")
        return view_func(*args, **kwargs)
    return wrapped


def api_roles_required(*roles):
    def decorator(view_func):
        @wraps(view_func)
        def wrapped(*args, **kwargs):
            if g.get("jwt_role") not in roles:
                log_security_event(
                    "UNAUTHORIZED_API_ACCESS",
                    "high",
                    g.get("jwt_subject"),
                    f"role={g.get('jwt_role')} attempted {request.method} {request.path}",
                )
                log_audit("UNAUTHORIZED_ACCESS_ATTEMPT", "API", request.path, f"Blocked role={g.get('jwt_role')}")
                return jsonify({"error": "You do not have permission to perform this action."}), 403
            return view_func(*args, **kwargs)
        return wrapped
    return decorator


# --- Notification engine ----------------------------------------------------

NOTIFICATION_LABELS = {
    "appointment_reminder": "Appointment Reminder",
    "prescription_alert": "Prescription Alert",
    "follow_up_reminder": "Follow-Up Reminder",
    "missed_appointment": "Missed Appointment",
}


def create_notification(patient_id, notif_type, title, message, related_type=None, related_id=None):
    """Create a notification unless an identical one (same patient/type/related
    record) already exists, so reminders are never duplicated."""
    existing = Notification.query.filter_by(
        patient_id=patient_id, notif_type=notif_type, related_id=related_id
    ).first()
    if existing:
        return existing
    note = Notification(
        patient_id=patient_id,
        notif_type=notif_type,
        title=title,
        message=message,
        related_type=related_type,
        related_id=related_id,
    )
    db.session.add(note)
    db.session.commit()
    return note


def generate_notifications_for_patient(patient):
    """Appointment-reminder and follow-up-reminder checks for one patient.
    (Prescription alerts are created immediately at prescription-creation
    time; missed-appointment alerts are created inside update_completed_appointments().)"""
    tomorrow = date.today() + timedelta(days=1)
    upcoming_tomorrow = Appointment.query.filter(
        Appointment.patient_id == patient.patient_id,
        Appointment.appointment_date == tomorrow,
        Appointment.status.in_(["Confirmed", "Pending"]),
    ).all()
    for appt in upcoming_tomorrow:
        create_notification(
            patient.patient_id,
            "appointment_reminder",
            "Appointment tomorrow",
            f"Your appointment with {appt.doctor} ({appt.department}) is tomorrow at {appt.time_slot}.",
            related_type="appointment",
            related_id=appt.appointment_id,
        )

    follow_up_cutoff = date.today() - timedelta(days=7)
    stale_consultations = Consultation.query.filter(
        Consultation.patient_id == patient.patient_id,
        Consultation.consultation_date <= follow_up_cutoff,
    ).all()
    for consult in stale_consultations:
        has_later_appointment = Appointment.query.filter(
            Appointment.patient_id == patient.patient_id,
            Appointment.appointment_date > consult.consultation_date,
        ).first()
        if not has_later_appointment:
            create_notification(
                patient.patient_id,
                "follow_up_reminder",
                "Follow-up may be due",
                f"It's been a week since your consultation {consult.consultation_id} ({consult.diagnosis}). "
                f"Consider booking a follow-up appointment with {consult.doctor}.",
                related_type="consultation",
                related_id=consult.consultation_id,
            )


def ensure_notifications_current():
    """Runs the notification engine for the signed-in patient at most once
    per minute per session, so it stays cheap on every page load."""
    patient_id = session.get("patient_id")
    if not patient_id:
        return
    last_check = session.get("notif_last_check")
    now_ts = datetime.utcnow().timestamp()
    if last_check and now_ts - last_check < 60:
        return
    session["notif_last_check"] = now_ts
    patient = get_patient_or_none(patient_id)
    if patient:
        generate_notifications_for_patient(patient)


@app.context_processor
def inject_milestone3_context():
    """Makes role/notification info available in every template (including
    layout.html's sidebar, topbar, and notification bell) without having to
    thread it through every render_template() call."""
    role = session.get("role")
    unread_count = 0
    recent_notes = []
    if role == "patient" and session.get("patient_id"):
        ensure_notifications_current()
        unread_count = Notification.query.filter_by(
            patient_id=session.get("patient_id"), is_read=False
        ).count()
        recent_notes = (
            Notification.query.filter_by(patient_id=session.get("patient_id"))
            .order_by(Notification.created_at.desc())
            .limit(6)
            .all()
        )
    return dict(
        current_role=role,
        current_display_name=session.get("patient_name") or session.get("staff_name"),
        unread_notification_count=unread_count,
        recent_notifications=recent_notes,
        notification_labels=NOTIFICATION_LABELS,
    )


# --- End Milestone 3 helpers -----------------------------------------------


@app.route("/")
def index():
    if session.get("patient_key") or session.get("staff_key"):
        return redirect(url_for("dashboard"))
    return render_template(
        "landing.html",
        title="MediTrack — Integrated Patient Care Management System",
        departments=DEPARTMENTS,
    )


@app.route("/contact", methods=["POST"])
def contact_submit():
    name = request.form.get("name", "").strip()
    email = request.form.get("email", "").strip()
    message = request.form.get("message", "").strip()
    if not name or not email or not message:
        flash("Please fill in your name, email, and message.", "error")
        return redirect(url_for("index") + "#contact")
    log_audit(
        "CONTACT_MESSAGE_RECEIVED",
        "ContactMessage",
        None,
        f"From {name} <{email}>: {message[:200]}",
    )
    flash("Thanks for reaching out — our care team will get back to you shortly.", "success")
    return redirect(url_for("index") + "#contact")


@app.route("/ambulance", methods=["GET", "POST"])
def ambulance_request():
    if request.method == "POST":
        name = request.form.get("name", "").strip()
        phone = request.form.get("phone", "").strip()
        location = request.form.get("location", "").strip()
        emergency_type = request.form.get("emergency_type", "").strip()
        if not name or not phone or not location:
            flash("Please provide your name, phone number, and pickup location.", "error")
            return redirect(url_for("ambulance_request"))
        request_id = f"AMB-{uuid.uuid4().hex[:6].upper()}"
        log_audit(
            "AMBULANCE_REQUESTED",
            "Ambulance",
            request_id,
            f"{name} ({phone}) at {location}; type={emergency_type or 'Not specified'}",
        )
        return redirect(url_for("ambulance_track", request_id=request_id, name=name, location=location))
    return render_template("ambulance_request.html", title="Request an Ambulance")


@app.route("/ambulance/track/<request_id>")
def ambulance_track(request_id):
    return render_template(
        "ambulance_track.html",
        title="Ambulance Tracking",
        request_id=request_id,
        name=request.args.get("name", "Guest"),
        location=request.args.get("location", "Your location"),
    )


@app.route("/login", methods=["GET", "POST"])
def login():
    if session.get("patient_key") or session.get("staff_key"):
        return redirect(url_for("dashboard"))

    if request.method == "POST":
        login_value = request.form.get("login", "").strip()
        password = request.form.get("password", "")

        # Milestone 3: a single sign-in form now serves both patient accounts
        # and staff (doctor/admin) accounts.
        patient = Patient.query.filter(
            or_(Patient.username == login_value, Patient.email == login_value)
        ).first()
        staff = None
        if not patient:
            staff = Staff.query.filter(
                or_(Staff.username == login_value, Staff.email == login_value)
            ).first()
        account = patient or staff

        if not account or not check_password_hash(account.password, password):
            track_failed_login(login_value)
            flash("Invalid credentials. Please try again.", "error")
        elif isinstance(account, Patient) and not account.is_active:
            flash("This patient record is inactive.", "warning")
        elif isinstance(account, Staff) and not account.is_active:
            flash("This staff account is inactive.", "warning")
        else:
            if isinstance(account, Patient):
                session["patient_key"] = account.id
                session["patient_id"] = account.patient_id
                session["patient_name"] = account.full_name
                session["role"] = "patient"
                log_audit("LOGIN_SUCCESS", "Auth", account.patient_id)
            else:
                session["staff_key"] = account.id
                session["staff_id"] = account.staff_id
                session["staff_name"] = account.name
                session["role"] = account.role
                log_audit("LOGIN_SUCCESS", "Auth", account.staff_id)
            flash("Welcome back to MediTrack.", "success")
            return redirect(url_for("dashboard"))
    return render_template("login.html", title="Sign In")


@app.route("/logout")
def logout():
    if session.get("patient_key") or session.get("staff_key"):
        log_audit("LOGOUT", "Auth", session.get("patient_id") or session.get("staff_id"))
    session.clear()
    flash("You have been logged out successfully.", "info")
    return redirect(url_for("login"))


@app.route("/register", methods=["GET", "POST"])
def register():
    generated_patient_id = next_code(Patient, "PAT")
    if request.method == "POST":
        form = request.form
        required_fields = [
            "first_name",
            "last_name",
            "age",
            "gender",
            "dob",
            "phone",
            "email",
            "address",
            "username",
            "password",
            "confirm_password",
        ]
        if any(not form.get(field, "").strip() for field in required_fields):
            flash("Please complete all required registration fields.", "error")
            return render_template(
                "register.html", title="Register", next_patient_id=generated_patient_id
            )

        if form.get("password") != form.get("confirm_password"):
            flash("Password and confirm password do not match.", "error")
            return render_template(
                "register.html", title="Register", next_patient_id=generated_patient_id
            )

        duplicate = Patient.query.filter(
            or_(Patient.email == form.get("email"), Patient.phone == form.get("phone"), Patient.username == form.get("username"))
        ).first()
        if duplicate:
            flash("A patient with the same email, phone, or username already exists.", "error")
            return render_template(
                "register.html", title="Register", next_patient_id=generated_patient_id
            )

        patient = Patient(
            patient_id=form.get("patient_id") or generated_patient_id,
            first_name=form.get("first_name").strip(),
            last_name=form.get("last_name").strip(),
            age=int(form.get("age")),
            gender=form.get("gender").strip(),
            dob=datetime.strptime(form.get("dob"), "%Y-%m-%d").date(),
            phone=form.get("phone").strip(),
            email=form.get("email").strip().lower(),
            address=form.get("address").strip(),
            username=form.get("username").strip(),
            password=generate_password_hash(form.get("password")),
        )
        db.session.add(patient)
        db.session.flush()
        generate_qr_code(patient)
        db.session.add(PatientProfile(patient_id=patient.patient_id))
        db.session.commit()
        flash("Registration complete. Please sign in with your new account.", "success")
        log_audit("PATIENT_REGISTERED", "Patient", patient.patient_id)
        return redirect(url_for("login"))

    return render_template(
        "register.html", title="Register", next_patient_id=generated_patient_id
    )


@app.route("/dashboard")
@login_required
def dashboard():
    update_completed_appointments()

    # Milestone 3: staff (doctor/admin) accounts get a system-facing
    # dashboard instead of the patient's personal one.
    if session.get("role") in ("doctor", "admin"):
        staff = current_staff()
        overview_stats = {
            "total_patients": Patient.query.count(),
            "total_appointments": Appointment.query.count(),
            "todays_appointments": Appointment.query.filter(
                Appointment.appointment_date == date.today()
            ).count(),
            "total_consultations": Consultation.query.count(),
            "total_prescriptions": Prescription.query.count(),
            "upcoming_appointments": Appointment.query.filter(
                Appointment.appointment_date >= date.today(),
                Appointment.status.in_(["Confirmed", "Pending"]),
            ).count(),
        }
        recent_patients = Patient.query.order_by(Patient.created_at.desc()).limit(5).all()
        recent_security_events = (
            SecurityEvent.query.order_by(SecurityEvent.created_at.desc()).limit(5).all()
            if session.get("role") == "admin"
            else []
        )
        recent_audit_logs = (
            AuditLog.query.order_by(AuditLog.created_at.desc()).limit(6).all()
        )
        return render_template(
            "staff_dashboard.html",
            title="Dashboard",
            page_title="Clinical dashboard",
            staff=staff,
            overview_stats=overview_stats,
            recent_patients=recent_patients,
            recent_security_events=recent_security_events,
            recent_audit_logs=recent_audit_logs,
        )

    patient = current_patient()
    profile = patient.profile
    completion = profile_completion(profile)
    stats = {
        "total_appointments": Appointment.query.filter_by(patient_id=patient.patient_id).count(),
        "upcoming_appointments": Appointment.query.filter(
            Appointment.patient_id == patient.patient_id,
            Appointment.appointment_date >= date.today(),
            Appointment.status.in_(["Confirmed", "Pending"]),
        ).count(),
        "completed_appointments": Appointment.query.filter_by(
            patient_id=patient.patient_id, status="Completed"
        ).count(),
    }
    next_appointment = (
        Appointment.query.filter(
            Appointment.patient_id == patient.patient_id,
            Appointment.appointment_date >= date.today(),
            Appointment.status != "Cancelled",
        )
        .order_by(Appointment.appointment_date.asc(), Appointment.time_slot.asc())
        .first()
    )
    recent_patients = (
        Patient.query.order_by(Patient.created_at.desc()).limit(5).all()
    )

    # --- Milestone 2 addition: system-wide overview stats (additive only) ---
    milestone2_stats = {
        "total_patients": Patient.query.count(),
        "total_appointments": Appointment.query.count(),
        "todays_appointments": Appointment.query.filter(
            Appointment.appointment_date == date.today()
        ).count(),
        "total_consultations": Consultation.query.count(),
        "total_prescriptions": Prescription.query.count(),
        "upcoming_appointments": Appointment.query.filter(
            Appointment.appointment_date >= date.today(),
            Appointment.status.in_(["Confirmed", "Pending"]),
        ).count(),
    }
    # --- End Milestone 2 addition ---

    return render_template(
        "dashboard.html",
        title="Dashboard",
        page_title="Care dashboard",
        patient=patient,
        stats=stats,
        next_appointment=next_appointment,
        completion=completion,
        recent_patients=recent_patients,
        milestone2_stats=milestone2_stats,
    )


@app.route("/profile", methods=["GET", "POST"])
@login_required
def profile():
    if session.get("role") in ("doctor", "admin"):
        flash("Staff accounts don't have a patient medical profile.", "info")
        return redirect(url_for("dashboard"))
    patient = current_patient()
    if not patient.qr_code_path:
        generate_qr_code(patient)
        db.session.commit()
    profile_obj = patient.profile or PatientProfile(patient_id=patient.patient_id)
    if request.method == "POST":
        if not patient.profile:
            db.session.add(profile_obj)
        for field in PROFILE_FIELDS:
            setattr(profile_obj, field, request.form.get(field, "").strip() or None)
        auto_bmi = recalculate_bmi(request.form.get("height"), request.form.get("weight"))
        if auto_bmi:
            profile_obj.bmi = auto_bmi
        photo = request.files.get("profile_photo")
        photo_path = save_profile_photo(photo)
        if photo_path:
            profile_obj.profile_photo = photo_path
        profile_obj.last_updated = datetime.utcnow()
        db.session.commit()
        flash("Medical profile updated successfully.", "success")
        log_audit("PROFILE_UPDATED", "Patient", patient.patient_id)
        return redirect(url_for("profile"))

    completion = profile_completion(profile_obj)
    missing_fields = missing_profile_fields(profile_obj)
    last_updated = (
        profile_obj.last_updated.strftime("%d %b %Y, %I:%M %p")
        if profile_obj and profile_obj.last_updated
        else "Not updated yet"
    )
    photo_url = (
        url_for("static", filename=profile_obj.profile_photo)
        if profile_obj.profile_photo
        else "https://via.placeholder.com/96x96.png?text=MD"
    )
    return render_template(
        "profile.html",
        title="My Profile",
        page_title="Patient profile",
        patient=patient,
        profile=profile_obj,
        completion=completion,
        missing_fields=missing_fields,
        last_updated=last_updated,
        photo_url=photo_url,
    )


@app.route("/appointments", methods=["GET", "POST"])
@login_required
def appointments():
    if session.get("role") in ("doctor", "admin"):
        flash("Appointment booking is a patient-portal feature.", "info")
        return redirect(url_for("dashboard"))
    update_completed_appointments()
    patient = current_patient()
    next_appointment_id = next_code(Appointment, "APT")

    if request.method == "POST":
        department = request.form.get("department", "").strip()
        doctor = request.form.get("doctor", "").strip()
        appointment_date_raw = request.form.get("appointment_date", "")
        time_slot = request.form.get("time_slot", "").strip()
        reason = request.form.get("reason", "").strip()

        if not all([department, doctor, appointment_date_raw, time_slot, reason]):
            flash("Please complete all appointment fields.", "error")
            return redirect(url_for("appointments"))

        appointment_date = datetime.strptime(appointment_date_raw, "%Y-%m-%d").date()
        if appointment_date < date.today():
            flash("Appointments can only be booked for today or a future date.", "error")
            return redirect(url_for("appointments"))

        if doctor not in DEPARTMENTS.get(department, []):
            flash("Selected doctor does not belong to the chosen department.", "error")
            return redirect(url_for("appointments"))

        if time_slot not in available_slots(doctor, appointment_date):
            flash("That time slot is no longer available. Please choose another one.", "error")
            return redirect(url_for("appointments"))

        appointment = Appointment(
            appointment_id=next_appointment_id,
            patient_id=patient.patient_id,
            department=department,
            doctor=doctor,
            appointment_date=appointment_date,
            time_slot=time_slot,
            reason=reason,
            status="Confirmed",
            waiting_position=waiting_position(doctor, appointment_date),
        )
        db.session.add(appointment)
        db.session.commit()
        flash(f"Appointment {appointment.appointment_id} booked successfully.", "success")
        log_audit("APPOINTMENT_BOOKED", "Appointment", appointment.appointment_id)
        return redirect(url_for("appointments"))

    upcoming = (
        Appointment.query.filter(
            Appointment.patient_id == patient.patient_id,
            Appointment.appointment_date >= date.today(),
        )
        .order_by(Appointment.appointment_date.asc(), Appointment.time_slot.asc())
        .all()
    )
    history = (
        Appointment.query.filter_by(patient_id=patient.patient_id)
        .order_by(Appointment.appointment_date.desc(), Appointment.time_slot.desc())
        .all()
    )
    return render_template(
        "appointments.html",
        title="Appointments",
        page_title="Appointment scheduling",
        departments=list(DEPARTMENTS.keys()),
        next_appointment_id=next_appointment_id,
        upcoming=upcoming,
        history=history,
        today=date.today(),
        min_date=date.today().isoformat(),
        slot_options=TIME_SLOTS,
    )


@app.route("/appointments/<int:appointment_id>/cancel", methods=["POST"])
@login_required
def cancel_appointment(appointment_id):
    appointment = Appointment.query.get_or_404(appointment_id)
    patient = current_patient()
    if not patient or appointment.patient_id != patient.patient_id:
        log_security_event(
            "UNAUTHORIZED_RECORD_ACCESS",
            "high",
            session.get("patient_id") or session.get("staff_id"),
            f"Attempted to cancel appointment {appointment_id} belonging to another patient.",
        )
        flash("Unauthorized appointment action.", "error")
        return redirect(url_for("appointments"))
    if appointment.appointment_date <= date.today() or appointment.status == "Completed":
        flash("Only future appointments can be cancelled.", "warning")
        return redirect(url_for("appointments"))
    appointment.status = "Cancelled"
    db.session.commit()
    flash(f"Appointment {appointment.appointment_id} was cancelled.", "info")
    log_audit("APPOINTMENT_CANCELLED", "Appointment", appointment.appointment_id)
    return redirect(url_for("appointments"))


@app.route("/appointments/<int:appointment_id>/reschedule", methods=["POST"])
@login_required
def reschedule_appointment(appointment_id):
    appointment = Appointment.query.get_or_404(appointment_id)
    patient = current_patient()
    if not patient or appointment.patient_id != patient.patient_id:
        log_security_event(
            "UNAUTHORIZED_RECORD_ACCESS",
            "high",
            session.get("patient_id") or session.get("staff_id"),
            f"Attempted to reschedule appointment {appointment_id} belonging to another patient.",
        )
        flash("Unauthorized appointment action.", "error")
        return redirect(url_for("appointments"))
    if appointment.appointment_date <= date.today() or appointment.status == "Completed":
        flash("Only future appointments can be rescheduled.", "warning")
        return redirect(url_for("appointments"))

    new_date = datetime.strptime(request.form.get("appointment_date"), "%Y-%m-%d").date()
    new_slot = request.form.get("time_slot", "").strip()

    if new_date < date.today():
        flash("Please select a valid future date.", "error")
        return redirect(url_for("appointments"))

    if new_slot not in available_slots(appointment.doctor, new_date, exclude_appointment_id=appointment.id):
        flash("Selected slot is already booked for this doctor.", "error")
        return redirect(url_for("appointments"))

    appointment.appointment_date = new_date
    appointment.time_slot = new_slot
    appointment.waiting_position = waiting_position(
        appointment.doctor, new_date, exclude_appointment_id=appointment.id
    )
    appointment.status = "Confirmed"
    db.session.commit()
    flash(f"Appointment {appointment.appointment_id} was rescheduled.", "success")
    log_audit("APPOINTMENT_RESCHEDULED", "Appointment", appointment.appointment_id)
    return redirect(url_for("appointments"))


@app.route("/patients")
@role_required("doctor", "admin")
def patients_db():
    page = request.args.get("page", 1, type=int)
    search = request.args.get("search", "").strip()
    blood_group = request.args.get("blood_group", "").strip()
    min_age = request.args.get("min_age", type=int)
    max_age = request.args.get("max_age", type=int)

    query = Patient.query.outerjoin(PatientProfile).order_by(Patient.created_at.desc())
    if search:
        term = f"%{search}%"
        query = query.filter(
            or_(
                Patient.patient_id.ilike(term),
                Patient.first_name.ilike(term),
                Patient.last_name.ilike(term),
                Patient.phone.ilike(term),
                Patient.email.ilike(term),
            )
        )
    if blood_group:
        query = query.filter(PatientProfile.blood_group == blood_group)
    if min_age is not None:
        query = query.filter(Patient.age >= min_age)
    if max_age is not None:
        query = query.filter(Patient.age <= max_age)

    patients = query.paginate(page=page, per_page=8, error_out=False)
    totals = {
        "registered": Patient.query.count(),
        "active": Patient.query.filter_by(is_active=True).count(),
        "recent": Patient.query.filter(
            Patient.created_at >= datetime.utcnow() - timedelta(days=7)
        ).count(),
    }
    blood_groups = ["A+", "A-", "B+", "B-", "AB+", "AB-", "O+", "O-"]
    return render_template(
        "patients.html",
        title="Patient Records",
        page_title="Patient database",
        patients=patients,
        totals=totals,
        blood_groups=blood_groups,
    )


@app.route("/patients/<int:patient_id>/deactivate", methods=["POST"])
@role_required("admin")
def deactivate_patient(patient_id):
    patient = Patient.query.get_or_404(patient_id)
    if patient.id == session.get("patient_key"):
        flash("You cannot deactivate the currently signed-in patient.", "warning")
        return redirect(url_for("patients_db"))
    patient.is_active = False
    db.session.commit()
    flash(f"{patient.full_name} was marked inactive.", "info")
    log_audit("PATIENT_DEACTIVATED", "Patient", patient.patient_id)
    return redirect(url_for("patients_db"))


@app.route("/api/doctors")
@login_required
def api_doctors():
    department = request.args.get("department", "")
    return jsonify({"doctors": DEPARTMENTS.get(department, [])})


@app.route("/api/slots")
@login_required
def api_slots():
    doctor = request.args.get("doctor", "")
    date_string = request.args.get("date", "")
    if not doctor or not date_string:
        return jsonify({"slots": []})
    appointment_date = datetime.strptime(date_string, "%Y-%m-%d").date()
    return jsonify({"slots": available_slots(doctor, appointment_date)})


@app.route("/patient/<patient_id>")
def patient_lookup(patient_id):
    patient = Patient.query.filter_by(patient_id=patient_id).first_or_404()
    profile = patient.profile
    template = """
    <!doctype html>
    <html lang='en'>
    <head>
      <meta charset='utf-8'>
      <meta name='viewport' content='width=device-width, initial-scale=1'>
      <title>{{ patient.patient_id }} | MediTrack</title>
      <link href='https://cdn.jsdelivr.net/npm/bootstrap@5.3.3/dist/css/bootstrap.min.css' rel='stylesheet'>
    </head>
    <body class='bg-light'>
      <div class='container py-5'>
        <div class='card border-0 shadow-sm mx-auto' style='max-width: 720px;'>
          <div class='card-body p-4 p-lg-5'>
            <span class='badge text-bg-primary mb-3'>MediTrack Patient Card</span>
            <h2 class='fw-bold mb-1'>{{ patient.full_name }}</h2>
            <p class='text-muted'>{{ patient.patient_id }} • {{ patient.email }}</p>
            <div class='row g-3 mt-2'>
              <div class='col-md-6'><div class='border rounded-4 p-3 h-100'><div class='small text-muted'>Blood Group</div><div class='fw-semibold'>{{ profile.blood_group if profile and profile.blood_group else 'Not available' }}</div></div></div>
              <div class='col-md-6'><div class='border rounded-4 p-3 h-100'><div class='small text-muted'>Emergency Contact</div><div class='fw-semibold'>{{ profile.emergency_contact_name if profile and profile.emergency_contact_name else 'Not available' }}</div><div class='text-muted small'>{{ profile.emergency_contact_phone if profile and profile.emergency_contact_phone else '' }}</div></div></div>
            </div>
          </div>
        </div>
      </div>
    </body>
    </html>
    """
    return render_template_string(template, patient=patient, profile=profile)


# ---------------------------------------------------------------------------
# Milestone 2 routes: Consultations, Prescriptions, Patient Detail
# (Appended without modifying any existing route above.)
# ---------------------------------------------------------------------------

@app.route("/consultations/new", methods=["GET", "POST"])
@role_required("doctor", "admin")
def new_consultation():
    next_consultation_id = generate_prefixed_id(Consultation, "consultation_id", "CON")
    prefill_patient_id = request.values.get("patient_id", "").strip()
    prefill_appointment_id = request.values.get("appointment_id", "").strip()

    active_patients = Patient.query.filter_by(is_active=True).order_by(Patient.first_name).all()

    if request.method == "POST":
        form = request.form
        patient_id = form.get("patient_id", "").strip()
        doctor = form.get("doctor", "").strip()
        symptoms = form.get("symptoms", "").strip()
        diagnosis = form.get("diagnosis", "").strip()
        treatment = form.get("treatment", "").strip()
        consultation_date_raw = form.get("consultation_date", "").strip()
        notes = form.get("notes", "").strip()
        appointment_id = form.get("appointment_id", "").strip() or None

        patient = get_patient_or_none(patient_id)

        if not patient or not doctor or not symptoms or not diagnosis or not treatment or not consultation_date_raw:
            flash("Please complete all required consultation fields.", "error")
            return render_template(
                "consultation_form.html",
                title="New Consultation",
                page_title="Consultation module",
                next_consultation_id=next_consultation_id,
                active_patients=active_patients,
                doctors=ALL_DOCTORS,
                prefill_patient_id=patient_id,
                prefill_appointment_id=appointment_id or "",
                today=date.today().isoformat(),
            )

        consultation_date = datetime.strptime(consultation_date_raw, "%Y-%m-%d").date()

        if appointment_id:
            appointment_check = Appointment.query.filter_by(
                appointment_id=appointment_id, patient_id=patient.patient_id
            ).first()
            if not appointment_check:
                appointment_id = None

        consultation = Consultation(
            consultation_id=next_consultation_id,
            patient_id=patient.patient_id,
            appointment_id=appointment_id,
            doctor=doctor,
            symptoms=symptoms,
            diagnosis=diagnosis,
            treatment=treatment,
            consultation_date=consultation_date,
            notes=notes or None,
        )
        db.session.add(consultation)
        db.session.commit()
        flash(f"Consultation {consultation.consultation_id} saved successfully.", "success")
        log_audit("CONSULTATION_CREATED", "Consultation", consultation.consultation_id, f"Patient={patient.patient_id}")
        return redirect(url_for("consultation_detail", consultation_id=consultation.consultation_id))

    return render_template(
        "consultation_form.html",
        title="New Consultation",
        page_title="Consultation module",
        next_consultation_id=next_consultation_id,
        active_patients=active_patients,
        doctors=ALL_DOCTORS,
        prefill_patient_id=prefill_patient_id,
        prefill_appointment_id=prefill_appointment_id,
        today=date.today().isoformat(),
    )


@app.route("/consultations")
@role_required("doctor", "admin")
def consultation_history():
    search = request.args.get("search", "").strip()
    patient_filter = request.args.get("patient_id", "").strip()
    doctor_filter = request.args.get("doctor", "").strip()

    query = Consultation.query.join(Patient, Consultation.patient_id == Patient.patient_id)
    if search:
        term = f"%{search}%"
        query = query.filter(
            or_(
                Consultation.consultation_id.ilike(term),
                Patient.first_name.ilike(term),
                Patient.last_name.ilike(term),
                Consultation.diagnosis.ilike(term),
            )
        )
    if patient_filter:
        query = query.filter(Consultation.patient_id == patient_filter)
    if doctor_filter:
        query = query.filter(Consultation.doctor == doctor_filter)

    consultations = query.order_by(Consultation.created_at.desc()).all()
    all_patients = Patient.query.order_by(Patient.first_name).all()

    return render_template(
        "consultation_history.html",
        title="Consultation History",
        page_title="Consultation history",
        consultations=consultations,
        all_patients=all_patients,
        doctors=ALL_DOCTORS,
    )


@app.route("/consultations/<consultation_id>")
@login_required
def consultation_detail(consultation_id):
    consultation = Consultation.query.filter_by(consultation_id=consultation_id).first_or_404()

    # Milestone 3: clinical staff may view any consultation; a patient may
    # only view their own. Anything else is an unauthorized-access attempt.
    if session.get("role") == "patient" and consultation.patient_id != session.get("patient_id"):
        log_security_event(
            "UNAUTHORIZED_RECORD_ACCESS",
            "high",
            session.get("patient_id"),
            f"Patient attempted to view consultation {consultation_id} belonging to another patient.",
        )
        log_audit("UNAUTHORIZED_ACCESS_ATTEMPT", "Consultation", consultation_id)
        flash("You do not have permission to view that record.", "error")
        return redirect(url_for("dashboard"))

    return render_template(
        "consultation_detail.html",
        title=consultation.consultation_id,
        page_title="Consultation details",
        consultation=consultation,
    )


@app.route("/prescriptions/new", methods=["GET", "POST"])
@role_required("doctor", "admin")
def new_prescription():
    next_prescription_id = generate_prefixed_id(Prescription, "prescription_id", "RX")
    prefill_patient_id = request.values.get("patient_id", "").strip()
    prefill_consultation_id = request.values.get("consultation_id", "").strip()

    active_patients = Patient.query.filter_by(is_active=True).order_by(Patient.first_name).all()

    if request.method == "POST":
        form = request.form
        patient_id = form.get("patient_id", "").strip()
        doctor = form.get("doctor", "").strip()
        consultation_id = form.get("consultation_id", "").strip() or None
        prescription_date_raw = form.get("prescription_date", "").strip()

        medicine_names = form.getlist("medicine_name[]")
        dosages = form.getlist("dosage[]")
        frequencies = form.getlist("frequency[]")
        durations = form.getlist("duration[]")
        instructions_list = form.getlist("instructions[]")

        patient = get_patient_or_none(patient_id)
        valid_medicines = [
            (name.strip(), dosage.strip(), frequency.strip(), duration.strip(), instructions.strip())
            for name, dosage, frequency, duration, instructions in zip(
                medicine_names, dosages, frequencies, durations, instructions_list
            )
            if name.strip()
        ]

        if not patient or not doctor or not prescription_date_raw or not valid_medicines:
            flash("Please complete the prescription details and add at least one medicine.", "error")
            return render_template(
                "prescription_form.html",
                title="New Prescription",
                page_title="Prescription module",
                next_prescription_id=next_prescription_id,
                active_patients=active_patients,
                doctors=ALL_DOCTORS,
                prefill_patient_id=patient_id,
                prefill_consultation_id=consultation_id or "",
                today=date.today().isoformat(),
            )

        if consultation_id:
            consultation_check = Consultation.query.filter_by(
                consultation_id=consultation_id, patient_id=patient.patient_id
            ).first()
            if not consultation_check:
                consultation_id = None

        prescription_date = datetime.strptime(prescription_date_raw, "%Y-%m-%d").date()

        prescription = Prescription(
            prescription_id=next_prescription_id,
            patient_id=patient.patient_id,
            doctor=doctor,
            consultation_id=consultation_id,
            prescription_date=prescription_date,
        )
        db.session.add(prescription)
        db.session.flush()

        for name, dosage, frequency, duration, instructions in valid_medicines:
            db.session.add(
                PrescriptionItem(
                    prescription_id=prescription.prescription_id,
                    medicine_name=name,
                    dosage=dosage,
                    frequency=frequency,
                    duration=duration,
                    instructions=instructions or None,
                )
            )
        db.session.commit()
        flash(f"Prescription {prescription.prescription_id} saved successfully.", "success")
        log_audit("PRESCRIPTION_CREATED", "Prescription", prescription.prescription_id, f"Patient={patient.patient_id}")
        medicine_summary = ", ".join(name for name, *_ in valid_medicines[:3])
        if len(valid_medicines) > 3:
            medicine_summary += f", +{len(valid_medicines) - 3} more"
        create_notification(
            patient.patient_id,
            "prescription_alert",
            "Your prescription is ready",
            f"Prescription {prescription.prescription_id} from {doctor} is ready: {medicine_summary}.",
            related_type="prescription",
            related_id=prescription.prescription_id,
        )
        return redirect(url_for("prescription_detail", prescription_id=prescription.prescription_id))

    return render_template(
        "prescription_form.html",
        title="New Prescription",
        page_title="Prescription module",
        next_prescription_id=next_prescription_id,
        active_patients=active_patients,
        doctors=ALL_DOCTORS,
        prefill_patient_id=prefill_patient_id,
        prefill_consultation_id=prefill_consultation_id,
        today=date.today().isoformat(),
    )


@app.route("/prescriptions")
@role_required("doctor", "admin")
def prescription_history():
    search = request.args.get("search", "").strip()
    patient_filter = request.args.get("patient_id", "").strip()
    doctor_filter = request.args.get("doctor", "").strip()

    query = Prescription.query.join(Patient, Prescription.patient_id == Patient.patient_id)
    if search:
        term = f"%{search}%"
        query = query.filter(
            or_(
                Prescription.prescription_id.ilike(term),
                Patient.first_name.ilike(term),
                Patient.last_name.ilike(term),
            )
        )
    if patient_filter:
        query = query.filter(Prescription.patient_id == patient_filter)
    if doctor_filter:
        query = query.filter(Prescription.doctor == doctor_filter)

    prescriptions = query.order_by(Prescription.created_at.desc()).all()
    all_patients = Patient.query.order_by(Patient.first_name).all()

    return render_template(
        "prescription_history.html",
        title="Prescription History",
        page_title="Prescription history",
        prescriptions=prescriptions,
        all_patients=all_patients,
        doctors=ALL_DOCTORS,
    )


@app.route("/prescriptions/<prescription_id>")
@login_required
def prescription_detail(prescription_id):
    prescription = Prescription.query.filter_by(prescription_id=prescription_id).first_or_404()

    if session.get("role") == "patient" and prescription.patient_id != session.get("patient_id"):
        log_security_event(
            "UNAUTHORIZED_RECORD_ACCESS",
            "high",
            session.get("patient_id"),
            f"Patient attempted to view prescription {prescription_id} belonging to another patient.",
        )
        log_audit("UNAUTHORIZED_ACCESS_ATTEMPT", "Prescription", prescription_id)
        flash("You do not have permission to view that record.", "error")
        return redirect(url_for("dashboard"))

    return render_template(
        "prescription_detail.html",
        title=prescription.prescription_id,
        page_title="Prescription details",
        prescription=prescription,
    )


@app.route("/prescriptions/<prescription_id>/print")
@login_required
def prescription_print(prescription_id):
    prescription = Prescription.query.filter_by(prescription_id=prescription_id).first_or_404()

    if session.get("role") == "patient" and prescription.patient_id != session.get("patient_id"):
        log_security_event(
            "UNAUTHORIZED_RECORD_ACCESS",
            "high",
            session.get("patient_id"),
            f"Patient attempted to print prescription {prescription_id} belonging to another patient.",
        )
        log_audit("UNAUTHORIZED_ACCESS_ATTEMPT", "Prescription", prescription_id)
        flash("You do not have permission to view that record.", "error")
        return redirect(url_for("dashboard"))

    return render_template("prescription_print.html", prescription=prescription)


@app.route("/patients/<patient_id>/detail")
@role_required("doctor", "admin")
def patient_detail(patient_id):
    patient = Patient.query.filter_by(patient_id=patient_id).first_or_404()
    tab = request.args.get("tab", "overview")
    appointments_list = (
        Appointment.query.filter_by(patient_id=patient.patient_id)
        .order_by(Appointment.appointment_date.desc())
        .all()
    )
    consultations_list = (
        Consultation.query.filter_by(patient_id=patient.patient_id)
        .order_by(Consultation.consultation_date.desc())
        .all()
    )
    prescriptions_list = (
        Prescription.query.filter_by(patient_id=patient.patient_id)
        .order_by(Prescription.prescription_date.desc())
        .all()
    )
    return render_template(
        "patient_detail.html",
        title=patient.full_name,
        page_title="Patient detail",
        patient=patient,
        profile=patient.profile,
        appointments_list=appointments_list,
        consultations_list=consultations_list,
        prescriptions_list=prescriptions_list,
        active_tab=tab,
        completion=profile_completion(patient.profile),
    )


@app.route("/api/patient-appointments")
@login_required
def api_patient_appointments():
    patient_id = request.args.get("patient_id", "")
    appointments_list = (
        Appointment.query.filter_by(patient_id=patient_id)
        .order_by(Appointment.appointment_date.desc())
        .all()
    )
    return jsonify(
        {
            "appointments": [
                {
                    "id": item.appointment_id,
                    "label": f"{item.appointment_id} — {item.appointment_date.strftime('%d %b %Y')} · {item.doctor}",
                }
                for item in appointments_list
            ]
        }
    )


@app.route("/api/patient-consultations")
@login_required
def api_patient_consultations():
    patient_id = request.args.get("patient_id", "")
    consultations_list = (
        Consultation.query.filter_by(patient_id=patient_id)
        .order_by(Consultation.consultation_date.desc())
        .all()
    )
    return jsonify(
        {
            "consultations": [
                {
                    "id": item.consultation_id,
                    "label": f"{item.consultation_id} — {item.consultation_date.strftime('%d %b %Y')} · {item.diagnosis[:40]}",
                }
                for item in consultations_list
            ]
        }
    )


# --- End Milestone 2 routes -----------------------------------------------


# ---------------------------------------------------------------------------
# Milestone 3 routes: Notifications, Security Center, REST API
# (Appended without modifying any existing route above.)
# ---------------------------------------------------------------------------

@app.route("/my-consultations")
@login_required
def my_consultations():
    """Patient-facing, read-only view of the signed-in patient's own
    consultation history. Full cross-patient browsing stays doctor/admin-only
    at /consultations; this route only ever shows the caller's own records."""
    if session.get("role") != "patient":
        flash("This page is for patient accounts. Staff can use Consultations from the sidebar.", "info")
        return redirect(url_for("dashboard"))
    items = (
        Consultation.query.filter_by(patient_id=session.get("patient_id"))
        .order_by(Consultation.consultation_date.desc())
        .all()
    )
    return render_template(
        "my_consultations.html",
        title="My Consultations",
        page_title="My consultations",
        consultations=items,
    )


@app.route("/my-prescriptions")
@login_required
def my_prescriptions():
    """Patient-facing, read-only view of the signed-in patient's own
    prescription history (mirrors my_consultations above)."""
    if session.get("role") != "patient":
        flash("This page is for patient accounts. Staff can use Prescriptions from the sidebar.", "info")
        return redirect(url_for("dashboard"))
    items = (
        Prescription.query.filter_by(patient_id=session.get("patient_id"))
        .order_by(Prescription.prescription_date.desc())
        .all()
    )
    return render_template(
        "my_prescriptions.html",
        title="My Prescriptions",
        page_title="My prescriptions",
        prescriptions=items,
    )


@app.route("/notifications")
@login_required
def notifications_page():
    if session.get("role") != "patient":
        flash("Notifications are a patient-portal feature.", "info")
        return redirect(url_for("dashboard"))
    ensure_notifications_current()
    all_notes = (
        Notification.query.filter_by(patient_id=session.get("patient_id"))
        .order_by(Notification.created_at.desc())
        .all()
    )
    return render_template(
        "notifications.html",
        title="Notifications",
        page_title="Notifications",
        all_notifications=all_notes,
    )


@app.route("/notifications/<int:notification_id>/read", methods=["POST"])
@login_required
def mark_notification_read(notification_id):
    note = Notification.query.get_or_404(notification_id)
    if note.patient_id != session.get("patient_id"):
        flash("Unauthorized.", "error")
        return redirect(url_for("notifications_page"))
    note.is_read = True
    db.session.commit()
    return redirect(request.referrer or url_for("notifications_page"))


@app.route("/notifications/mark-all-read", methods=["POST"])
@login_required
def mark_all_notifications_read():
    if session.get("role") == "patient":
        Notification.query.filter_by(
            patient_id=session.get("patient_id"), is_read=False
        ).update({"is_read": True})
        db.session.commit()
    return redirect(request.referrer or url_for("notifications_page"))


@app.route("/security")
@role_required("admin")
def security_center():
    tab = request.args.get("tab", "audit")
    search = request.args.get("search", "").strip()

    audit_query = AuditLog.query
    if search:
        term = f"%{search}%"
        audit_query = audit_query.filter(
            or_(
                AuditLog.actor_label.ilike(term),
                AuditLog.action.ilike(term),
                AuditLog.resource.ilike(term),
            )
        )
    audit_logs = audit_query.order_by(AuditLog.created_at.desc()).limit(300).all()

    security_events = (
        SecurityEvent.query.order_by(SecurityEvent.created_at.desc()).limit(300).all()
    )

    summary = {
        "total_audit_events": AuditLog.query.count(),
        "total_security_events": SecurityEvent.query.count(),
        "high_severity_events": SecurityEvent.query.filter_by(severity="high").count(),
        "failed_logins_24h": SecurityEvent.query.filter(
            SecurityEvent.event_type == "FAILED_LOGIN",
            SecurityEvent.created_at >= datetime.utcnow() - timedelta(hours=24),
        ).count(),
    }

    return render_template(
        "security_center.html",
        title="Security Center",
        page_title="Security & audit center",
        active_tab=tab,
        audit_logs=audit_logs,
        security_events=security_events,
        summary=summary,
        search=search,
    )


@app.route("/api/docs")
@login_required
def api_docs():
    endpoints = [
        {
            "method": "POST",
            "path": "/api/v1/auth/login",
            "auth": "None",
            "description": "Exchange a username/email + password for a JWT access token.",
            "body": '{"login": "doctor01", "password": "Doctor@123"}',
        },
        {
            "method": "GET",
            "path": "/api/v1/patients",
            "auth": "JWT — doctor, admin",
            "description": "List all patients.",
            "body": None,
        },
        {
            "method": "POST",
            "path": "/api/v1/patients",
            "auth": "JWT — admin",
            "description": "Register a new patient.",
            "body": '{"first_name": "...", "last_name": "...", "age": 30, "gender": "Male", "dob": "1995-01-01", "phone": "...", "email": "...", "address": "...", "username": "...", "password": "..."}',
        },
        {
            "method": "GET",
            "path": "/api/v1/patients/<patient_id>",
            "auth": "JWT — doctor, admin, or the patient themself",
            "description": "Retrieve one patient record.",
            "body": None,
        },
        {
            "method": "PUT",
            "path": "/api/v1/patients/<patient_id>",
            "auth": "JWT — admin",
            "description": "Update a patient's core details.",
            "body": '{"phone": "...", "address": "...", "is_active": true}',
        },
        {
            "method": "DELETE",
            "path": "/api/v1/patients/<patient_id>",
            "auth": "JWT — admin",
            "description": "Soft-delete (deactivate) a patient.",
            "body": None,
        },
        {
            "method": "GET",
            "path": "/api/v1/appointments",
            "auth": "JWT — any role (patients see only their own)",
            "description": "List appointments.",
            "body": None,
        },
        {
            "method": "POST",
            "path": "/api/v1/appointments",
            "auth": "JWT — any role",
            "description": "Book an appointment.",
            "body": '{"patient_id": "PAT001", "department": "Cardiology", "doctor": "Dr. Amelia Carter", "appointment_date": "2026-09-10", "time_slot": "09:00 AM - 09:30 AM", "reason": "..."}',
        },
        {
            "method": "GET",
            "path": "/api/v1/consultations",
            "auth": "JWT — any role (patients see only their own)",
            "description": "List consultations.",
            "body": None,
        },
        {
            "method": "POST",
            "path": "/api/v1/consultations",
            "auth": "JWT — doctor, admin",
            "description": "Create a consultation record.",
            "body": '{"patient_id": "PAT001", "doctor": "...", "symptoms": "...", "diagnosis": "...", "treatment": "...", "consultation_date": "2026-08-29"}',
        },
        {
            "method": "GET",
            "path": "/api/v1/prescriptions",
            "auth": "JWT — any role (patients see only their own)",
            "description": "List prescriptions.",
            "body": None,
        },
        {
            "method": "POST",
            "path": "/api/v1/prescriptions",
            "auth": "JWT — doctor, admin",
            "description": "Create a prescription with one or more medicines.",
            "body": '{"patient_id": "PAT001", "doctor": "...", "prescription_date": "2026-08-29", "medicines": [{"medicine_name": "...", "dosage": "...", "frequency": "...", "duration": "...", "instructions": "..."}]}',
        },
    ]
    return render_template(
        "api_docs.html",
        title="API Docs",
        page_title="REST API documentation",
        endpoints=endpoints,
    )


# --- REST API (JWT-protected) -----------------------------------------------

def serialize_patient(patient, include_contact=True):
    data = {
        "patient_id": patient.patient_id,
        "full_name": patient.full_name,
        "age": patient.age,
        "gender": patient.gender,
        "is_active": patient.is_active,
        "created_at": patient.created_at.isoformat() if patient.created_at else None,
    }
    if include_contact:
        data.update({"phone": patient.phone, "email": patient.email, "address": patient.address})
    return data


def serialize_appointment(appt):
    return {
        "appointment_id": appt.appointment_id,
        "patient_id": appt.patient_id,
        "department": appt.department,
        "doctor": appt.doctor,
        "appointment_date": appt.appointment_date.isoformat(),
        "time_slot": appt.time_slot,
        "reason": appt.reason,
        "status": appt.status,
        "waiting_position": appt.waiting_position,
    }


def serialize_consultation(item):
    return {
        "consultation_id": item.consultation_id,
        "patient_id": item.patient_id,
        "appointment_id": item.appointment_id,
        "doctor": item.doctor,
        "symptoms": item.symptoms,
        "diagnosis": item.diagnosis,
        "treatment": item.treatment,
        "consultation_date": item.consultation_date.isoformat(),
        "notes": item.notes,
    }


def serialize_prescription(item):
    return {
        "prescription_id": item.prescription_id,
        "patient_id": item.patient_id,
        "doctor": item.doctor,
        "consultation_id": item.consultation_id,
        "prescription_date": item.prescription_date.isoformat(),
        "medicines": [
            {
                "medicine_name": med.medicine_name,
                "dosage": med.dosage,
                "frequency": med.frequency,
                "duration": med.duration,
                "instructions": med.instructions,
            }
            for med in item.items
        ],
    }


@app.route("/api/v1/auth/login", methods=["POST"])
def api_login():
    payload = request.get_json(silent=True) or {}
    login_value = str(payload.get("login", "")).strip()
    password = str(payload.get("password", ""))

    patient = Patient.query.filter(
        or_(Patient.username == login_value, Patient.email == login_value)
    ).first()
    staff = None if patient else Staff.query.filter(
        or_(Staff.username == login_value, Staff.email == login_value)
    ).first()
    account = patient or staff

    if not account or not check_password_hash(account.password, password):
        track_failed_login(login_value)
        return jsonify({"error": "Invalid credentials."}), 401
    if not account.is_active:
        return jsonify({"error": "This account is inactive."}), 403

    if isinstance(account, Patient):
        token = generate_jwt(account.patient_id, "patient", "patient")
        log_audit("API_LOGIN_SUCCESS", "Auth", account.patient_id)
        subject, role = account.patient_id, "patient"
    else:
        token = generate_jwt(account.staff_id, account.role, "staff")
        log_audit("API_LOGIN_SUCCESS", "Auth", account.staff_id)
        subject, role = account.staff_id, account.role

    return jsonify(
        {
            "token": token,
            "subject": subject,
            "role": role,
            "expires_in_minutes": app.config["JWT_EXP_MINUTES"],
        }
    )


@app.route("/api/v1/patients", methods=["GET", "POST"])
@token_required
def api_patients_collection():
    if request.method == "GET":
        if g.jwt_role not in ("doctor", "admin"):
            log_security_event("UNAUTHORIZED_API_ACCESS", "high", g.jwt_subject, f"role={g.jwt_role} tried GET /api/v1/patients")
            return jsonify({"error": "You do not have permission to perform this action."}), 403
        patients = Patient.query.order_by(Patient.created_at.desc()).all()
        log_audit("API_LIST_PATIENTS", "Patient")
        return jsonify({"patients": [serialize_patient(p) for p in patients]})

    # POST — create a new patient (admin only)
    if g.jwt_role != "admin":
        log_security_event("UNAUTHORIZED_API_ACCESS", "high", g.jwt_subject, f"role={g.jwt_role} tried POST /api/v1/patients")
        return jsonify({"error": "You do not have permission to perform this action."}), 403

    payload = request.get_json(silent=True) or {}
    required = ["first_name", "last_name", "age", "gender", "dob", "phone", "email", "address", "username", "password"]
    missing = [field for field in required if not str(payload.get(field, "")).strip()]
    if missing:
        return jsonify({"error": f"Missing required fields: {', '.join(missing)}"}), 400

    duplicate = Patient.query.filter(
        or_(
            Patient.email == payload["email"],
            Patient.phone == payload["phone"],
            Patient.username == payload["username"],
        )
    ).first()
    if duplicate:
        return jsonify({"error": "A patient with the same email, phone, or username already exists."}), 409

    try:
        dob = datetime.strptime(payload["dob"], "%Y-%m-%d").date()
        age = int(payload["age"])
    except (ValueError, TypeError):
        return jsonify({"error": "Invalid 'dob' (YYYY-MM-DD) or 'age'."}), 400

    patient = Patient(
        patient_id=next_code(Patient, "PAT"),
        first_name=payload["first_name"].strip(),
        last_name=payload["last_name"].strip(),
        age=age,
        gender=payload["gender"].strip(),
        dob=dob,
        phone=payload["phone"].strip(),
        email=payload["email"].strip().lower(),
        address=payload["address"].strip(),
        username=payload["username"].strip(),
        password=generate_password_hash(payload["password"]),
    )
    db.session.add(patient)
    db.session.commit()
    generate_qr_code(patient)
    db.session.commit()
    log_audit("API_PATIENT_CREATED", "Patient", patient.patient_id)
    return jsonify({"patient": serialize_patient(patient)}), 201


@app.route("/api/v1/patients/<patient_id>", methods=["GET", "PUT", "DELETE"])
@token_required
def api_patient_item(patient_id):
    patient = Patient.query.filter_by(patient_id=patient_id).first()
    if not patient:
        return jsonify({"error": "Patient not found."}), 404

    is_self = g.jwt_type == "patient" and g.jwt_subject == patient_id
    is_staff = g.jwt_role in ("doctor", "admin")

    if request.method == "GET":
        if not (is_self or is_staff):
            log_security_event("UNAUTHORIZED_API_ACCESS", "high", g.jwt_subject, f"tried GET /api/v1/patients/{patient_id}")
            return jsonify({"error": "You do not have permission to view this record."}), 403
        log_audit("API_VIEW_PATIENT", "Patient", patient_id)
        return jsonify({"patient": serialize_patient(patient)})

    if g.jwt_role != "admin":
        log_security_event("UNAUTHORIZED_API_ACCESS", "high", g.jwt_subject, f"role={g.jwt_role} tried {request.method} /api/v1/patients/{patient_id}")
        return jsonify({"error": "You do not have permission to perform this action."}), 403

    if request.method == "DELETE":
        patient.is_active = False
        db.session.commit()
        log_audit("API_PATIENT_DEACTIVATED", "Patient", patient_id)
        return jsonify({"patient": serialize_patient(patient)})

    # PUT — update
    payload = request.get_json(silent=True) or {}
    for field in ("phone", "address"):
        if field in payload and str(payload[field]).strip():
            setattr(patient, field, str(payload[field]).strip())
    if "is_active" in payload:
        patient.is_active = bool(payload["is_active"])
    db.session.commit()
    log_audit("API_PATIENT_UPDATED", "Patient", patient_id)
    return jsonify({"patient": serialize_patient(patient)})


@app.route("/api/v1/appointments", methods=["GET", "POST"])
@token_required
def api_appointments_collection():
    if request.method == "GET":
        query = Appointment.query
        if g.jwt_type == "patient":
            query = query.filter_by(patient_id=g.jwt_subject)
        appts = query.order_by(Appointment.appointment_date.desc()).limit(200).all()
        log_audit("API_LIST_APPOINTMENTS", "Appointment")
        return jsonify({"appointments": [serialize_appointment(a) for a in appts]})

    payload = request.get_json(silent=True) or {}
    patient_id = payload.get("patient_id") if g.jwt_role in ("doctor", "admin") else g.jwt_subject
    patient = get_patient_or_none(patient_id)
    required = ["department", "doctor", "appointment_date", "time_slot", "reason"]
    missing = [field for field in required if not str(payload.get(field, "")).strip()]
    if not patient or missing:
        return jsonify({"error": "Missing/invalid fields.", "missing": missing, "patient_found": bool(patient)}), 400

    try:
        appt_date = datetime.strptime(payload["appointment_date"], "%Y-%m-%d").date()
    except ValueError:
        return jsonify({"error": "Invalid 'appointment_date' (YYYY-MM-DD)."}), 400

    if payload["time_slot"] not in available_slots(payload["doctor"], appt_date):
        return jsonify({"error": "That time slot is no longer available."}), 409

    appointment = Appointment(
        appointment_id=next_code(Appointment, "APT"),
        patient_id=patient.patient_id,
        department=payload["department"],
        doctor=payload["doctor"],
        appointment_date=appt_date,
        time_slot=payload["time_slot"],
        reason=payload["reason"],
        status="Confirmed",
        waiting_position=waiting_position(payload["doctor"], appt_date),
    )
    db.session.add(appointment)
    db.session.commit()
    log_audit("API_APPOINTMENT_BOOKED", "Appointment", appointment.appointment_id)
    return jsonify({"appointment": serialize_appointment(appointment)}), 201


@app.route("/api/v1/consultations", methods=["GET", "POST"])
@token_required
def api_consultations_collection():
    if request.method == "GET":
        query = Consultation.query
        if g.jwt_type == "patient":
            query = query.filter_by(patient_id=g.jwt_subject)
        items = query.order_by(Consultation.created_at.desc()).limit(200).all()
        log_audit("API_LIST_CONSULTATIONS", "Consultation")
        return jsonify({"consultations": [serialize_consultation(c) for c in items]})

    if g.jwt_role not in ("doctor", "admin"):
        log_security_event("UNAUTHORIZED_API_ACCESS", "high", g.jwt_subject, f"role={g.jwt_role} tried POST /api/v1/consultations")
        return jsonify({"error": "You do not have permission to perform this action."}), 403

    payload = request.get_json(silent=True) or {}
    patient = get_patient_or_none(payload.get("patient_id"))
    required = ["doctor", "symptoms", "diagnosis", "treatment", "consultation_date"]
    missing = [field for field in required if not str(payload.get(field, "")).strip()]
    if not patient or missing:
        return jsonify({"error": "Missing/invalid fields.", "missing": missing, "patient_found": bool(patient)}), 400

    try:
        consult_date = datetime.strptime(payload["consultation_date"], "%Y-%m-%d").date()
    except ValueError:
        return jsonify({"error": "Invalid 'consultation_date' (YYYY-MM-DD)."}), 400

    consultation = Consultation(
        consultation_id=generate_prefixed_id(Consultation, "consultation_id", "CON"),
        patient_id=patient.patient_id,
        appointment_id=payload.get("appointment_id"),
        doctor=payload["doctor"],
        symptoms=payload["symptoms"],
        diagnosis=payload["diagnosis"],
        treatment=payload["treatment"],
        consultation_date=consult_date,
        notes=payload.get("notes"),
    )
    db.session.add(consultation)
    db.session.commit()
    log_audit("API_CONSULTATION_CREATED", "Consultation", consultation.consultation_id)
    return jsonify({"consultation": serialize_consultation(consultation)}), 201


@app.route("/api/v1/prescriptions", methods=["GET", "POST"])
@token_required
def api_prescriptions_collection():
    if request.method == "GET":
        query = Prescription.query
        if g.jwt_type == "patient":
            query = query.filter_by(patient_id=g.jwt_subject)
        items = query.order_by(Prescription.created_at.desc()).limit(200).all()
        log_audit("API_LIST_PRESCRIPTIONS", "Prescription")
        return jsonify({"prescriptions": [serialize_prescription(p) for p in items]})

    if g.jwt_role not in ("doctor", "admin"):
        log_security_event("UNAUTHORIZED_API_ACCESS", "high", g.jwt_subject, f"role={g.jwt_role} tried POST /api/v1/prescriptions")
        return jsonify({"error": "You do not have permission to perform this action."}), 403

    payload = request.get_json(silent=True) or {}
    patient = get_patient_or_none(payload.get("patient_id"))
    medicines = payload.get("medicines") or []
    if not patient or not payload.get("doctor") or not payload.get("prescription_date") or not medicines:
        return jsonify({"error": "patient_id, doctor, prescription_date, and at least one medicine are required."}), 400

    try:
        rx_date = datetime.strptime(payload["prescription_date"], "%Y-%m-%d").date()
    except ValueError:
        return jsonify({"error": "Invalid 'prescription_date' (YYYY-MM-DD)."}), 400

    prescription = Prescription(
        prescription_id=generate_prefixed_id(Prescription, "prescription_id", "RX"),
        patient_id=patient.patient_id,
        doctor=payload["doctor"],
        consultation_id=payload.get("consultation_id"),
        prescription_date=rx_date,
    )
    db.session.add(prescription)
    db.session.flush()

    for med in medicines:
        if not str(med.get("medicine_name", "")).strip():
            continue
        db.session.add(
            PrescriptionItem(
                prescription_id=prescription.prescription_id,
                medicine_name=med.get("medicine_name", "").strip(),
                dosage=med.get("dosage", "").strip(),
                frequency=med.get("frequency", "").strip(),
                duration=med.get("duration", "").strip(),
                instructions=med.get("instructions"),
            )
        )
    db.session.commit()
    log_audit("API_PRESCRIPTION_CREATED", "Prescription", prescription.prescription_id)
    create_notification(
        patient.patient_id,
        "prescription_alert",
        "Your prescription is ready",
        f"Prescription {prescription.prescription_id} from {payload['doctor']} is ready.",
        related_type="prescription",
        related_id=prescription.prescription_id,
    )
    return jsonify({"prescription": serialize_prescription(prescription)}), 201


# --- End Milestone 3 routes -------------------------------------------------


if __name__ == "__main__":
    app.run(debug=True)
