# MediTrack – Integrated Patient Care Management System

MediTrack is a responsive healthcare-themed Flask + MySQL web application focused on four integrated workflows: patient registration, patient profile management, patient database management, and appointment scheduling.

## Tech Stack
- Python Flask
- MySQL
- SQLAlchemy ORM
- HTML5, CSS3, JavaScript
- Bootstrap 5

## Included Features
- Auto-generated Patient IDs (`PAT001`, `PAT002`, ...)
- Secure registration with password hashing
- Duplicate prevention for email, phone, and username
- Registration review modal before submission
- QR code generation for each patient profile
- Editable medical profile with BMI auto-calculation
- Profile photo upload and profile completion progress tracking
- Quick medical summary + last-updated timestamp
- Searchable, filterable, paginated patient database
- Soft delete support for patient records
- Appointment booking with live department-doctor-slot flow
- Double-booking prevention and auto-blocked booked slots
- Appointment rescheduling, cancellation, status colors, and waiting position
- Responsive dashboard with quick actions and visit overview

## Project Structure
```bash
meditrack_m1/
├── app.py
├── requirements.txt
├── schema.sql
├── sample_data.sql
├── README.md
├── static/
│   ├── css/styles.css
│   ├── js/app.js
│   └── uploads/
│       ├── profiles/
│       └── qrcodes/
└── templates/
    ├── layout.html
    ├── login.html
    ├── register.html
    ├── dashboard.html
    ├── profile.html
    ├── appointments.html
    └── patients.html
```

## Setup Instructions
1. Create and activate a virtual environment.
2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
3. Create the MySQL database:
   ```sql
   CREATE DATABASE meditrack_db;
   ```
4. Import the schema:
   ```bash
   mysql -u root -p meditrack_db < schema.sql
   ```
5. (Optional) Import sample records:
   ```bash
   mysql -u root -p meditrack_db < sample_data.sql
   ```
   Sample login password for the seeded users: `Password@123`
6. Set environment variables before running:
   ```bash
   # Windows PowerShell
   $env:DATABASE_URL="mysql+pymysql://root:YOUR_PASSWORD@localhost/meditrack_db?charset=utf8mb4"
   $env:SECRET_KEY="your-secret-key"

   # macOS / Linux
   export DATABASE_URL="mysql+pymysql://root:YOUR_PASSWORD@localhost/meditrack_db?charset=utf8mb4"
   export SECRET_KEY="your-secret-key"
   ```
7. Run the app:
   ```bash
   python app.py
   ```
8. Open `http://127.0.0.1:5000`

## Notes
- The app creates tables automatically at startup if the database already exists.
- Profile photos and QR codes are stored inside `static/uploads/`.
- The patient database page is included as a demo-ready management screen. In production, you should protect it with role-based access control.
- Appointment status automatically flips from `Confirmed` / `Pending` to `Completed` after the scheduled date passes.

## Default Workflow
1. Register a patient account.
2. Sign in to the portal.
3. Complete the medical profile.
4. Book or manage appointments.
5. Use the patient records page to search and review stored information.

---

## Milestone 2 – Consultations & Prescriptions

This update adds the doctor-facing clinical workflow on top of the existing patient portal, without changing any Milestone 1 behavior.

### New Features
- **Consultations**: record symptoms, diagnosis, treatment, and notes for a patient visit, optionally linked to an appointment. Auto-generated IDs (`CON001`, `CON002`, ...).
- **Consultation history**: searchable, filterable (by patient/doctor) medical-record style log.
- **Prescriptions**: generate a prescription from a consultation (or standalone) with one or more medicines added dynamically via "Add Medicine". Auto-generated IDs (`RX001`, `RX002`, ...).
- **Prescription history**: searchable, filterable log of all prescriptions.
- **Print/Download Prescription**: a clean, A4-style printable prescription page with a Print button.
- **Patient detail page**: tabbed view (`Overview | Appointments | Consultations | Prescriptions`) reachable from Patient Records via **View**.
- **Dashboard update**: new "System overview" cards — Total Patients, Total Appointments, Today's Appointments, Total Consultations, Total Prescriptions, Upcoming Appointments — added alongside the existing personal stats cards.

### New Database Tables
- `consultations` — linked to `patients` and optionally `appointments`.
- `prescriptions` — linked to `patients` and optionally `consultations`.
- `prescription_items` — linked to `prescriptions`, one row per medicine.

No existing tables were modified; all new tables use foreign keys back to the existing `patients` and `appointments` tables.

### New Routes
| Route | Purpose |
|---|---|
| `/consultations/new` | Create a consultation |
| `/consultations` | Consultation history (search/filter) |
| `/consultations/<consultation_id>` | Consultation detail |
| `/prescriptions/new` | Create a prescription (multi-medicine) |
| `/prescriptions` | Prescription history (search/filter) |
| `/prescriptions/<prescription_id>` | Prescription detail |
| `/prescriptions/<prescription_id>/print` | Printable A4 prescription |
| `/patients/<patient_id>/detail` | Tabbed patient detail view |

### Security Notes
- All Milestone 2 routes are protected with the existing `login_required` decorator and use SQLAlchemy ORM (parameterized) queries throughout.
- As with the existing Patient Records page (see note above), Milestone 2's consultation/prescription pages are accessible to any signed-in user, since the app has a single patient-level session and no doctor-role system yet. If you add doctor accounts, protect `/consultations*`, `/prescriptions*`, and `/patients/<id>/detail` with role-based access control before production use.

---

## Milestone 3 – Notifications, Security & APIs

Adds JWT-secured REST APIs, role-based access control, audit logging, security monitoring, in-app notifications, and a public-facing hospital website — all without changing any Milestone 1/2 behavior for existing users.

### New Features

- **Public landing page** (`/`) — Home, About Us, Services, Departments, Doctors, and Contact sections, plus a 24/7 ambulance-request call-to-action. No login required.
- **Ambulance tracking demo** (`/ambulance`) — a public request form and a live-feeling, animated multi-step dispatch tracker (`Request Received → Dispatched → On The Way → Arrived`).
- **Staff accounts (Doctor / Admin)** — a new `staff` table alongside `patients`. Two accounts are auto-seeded on first run:
  - Admin: `admin` / `Admin@123`
  - Doctor: `doctor01` / `Doctor@123`
  The same login form on `/login` now accepts both patient and staff credentials.
- **Role-based access control** — `patient`, `doctor`, and `admin` roles are enforced on every route:
  - Patients: Dashboard, My Profile, Appointments, Notifications — and can view (but not browse) their **own** consultations/prescriptions.
  - Doctors/Admins: Patient Records, Consultations, Prescriptions (create + full history), API Docs.
  - Admins only: Security Center (audit logs + security events), patient soft-delete.
  - Any attempt to view another patient's record or a staff-only page is blocked, logged as a security event, and recorded in the audit trail.
- **Notifications** — in-app bell + `/notifications` page for patients:
  - *Appointment Reminder* — created the day before a confirmed/pending appointment.
  - *Prescription Alert* — created the moment a doctor saves a prescription.
  - *Follow-Up Reminder* — created 7+ days after a consultation if no later appointment has been booked.
  - *Missed Appointment* — a `Pending` appointment whose date has passed is now flipped to a new `Missed` status (instead of silently `Completed`) and the patient is notified.
- **Audit Logging** — every login, logout, registration, booking, consultation/prescription creation, patient update/deactivation, and API call is recorded with actor, role, action, resource, IP address, and timestamp. Viewable at **Security Center → Audit Logs** (admin only).
- **Security Monitoring** — failed logins are logged; 5+ failed attempts for the same username within 10 minutes raises a `BRUTE_FORCE_SUSPECTED` high-severity event. Unauthorized page/API access attempts are logged as `UNAUTHORIZED_*` events. Viewable at **Security Center → Security Events** (admin only).
- **JWT-secured REST API** under `/api/v1/` — see the in-app **API Docs** page (visible to doctor/admin) for the full list with example `curl` commands. Covers:
  - `POST /api/v1/auth/login` — get a token
  - `GET/POST /api/v1/patients`, `GET/PUT/DELETE /api/v1/patients/<id>`
  - `GET/POST /api/v1/appointments`
  - `GET/POST /api/v1/consultations`
  - `GET/POST /api/v1/prescriptions`

  Every endpoint enforces role and ownership rules identical to the web UI (e.g. a patient token can only see their own appointments/consultations/prescriptions).

### New Database Tables
- `staff` — doctor/admin accounts.
- `notifications` — per-patient in-app notifications.
- `audit_logs` — full action trail.
- `security_events` — failed logins, brute-force flags, unauthorized access attempts.

### New Config
- `JWT_SECRET` (env var, defaults to `SECRET_KEY`) and a 120-minute token expiry (`app.config["JWT_EXP_MINUTES"]`).

### Security Notes
- Web routes use session-based auth (`login_required` / `role_required`); the REST API uses stateless JWT bearer tokens (`token_required` / `api_roles_required`) — both paths funnel into the same audit/security logging.
- Passwords remain hashed with Werkzeug's `scrypt`-based hasher; JWTs are signed with HS256.
- As documented in Milestone 2, this project still uses a lightweight staff model (no self-service staff registration) — provision additional doctor/admin accounts directly in the `staff` table for now.
