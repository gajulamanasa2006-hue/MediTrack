# MediTrack – Integrated Patient Care Management System

## 🏥 Project Overview

**MediTrack** is a comprehensive web-based **Integrated Patient Care Management System** developed to digitize and streamline healthcare workflows.

The system provides a centralized platform for managing patients, appointments, consultations, prescriptions, notifications, security, analytics, reporting, and administrative operations.

MediTrack was developed incrementally through **four milestones**, where each milestone extends the functionality of the previous milestone.

The project follows the complete healthcare workflow:

```text
Patient Registration
        ↓
Patient Profile Management
        ↓
Appointment Scheduling
        ↓
Consultation
        ↓
Prescription
        ↓
Notifications
        ↓
Security & Audit Logging
        ↓
Analytics & Reports
        ↓
Testing & Optimization
        ↓
Deployment
```

---

# 📌 Introduction

Healthcare organizations manage a large amount of patient information every day. Traditional paper-based systems can lead to problems such as duplicate records, difficulty in accessing patient information, appointment conflicts, inefficient record management, and lack of centralized healthcare data.

MediTrack addresses these challenges by providing a centralized web-based healthcare management platform.

The system enables:

* Patient registration and profile management
* Patient record management
* Appointment scheduling
* Consultation management
* Prescription generation
* Patient notifications
* Role-based access control
* Security monitoring
* Audit logging
* Secure REST APIs
* Analytics dashboards
* CSV and PDF reports
* Testing and performance optimization

The main objective of MediTrack is to improve the efficiency, accessibility, organization, and security of patient care management.

---

# 🎯 Project Objectives

The major objectives of MediTrack are:

* To digitize patient registration and record management.
* To provide efficient appointment scheduling.
* To manage patient consultations and medical history.
* To generate and maintain digital prescriptions.
* To provide important notifications to patients.
* To implement secure authentication and authorization.
* To provide role-based access for patients, doctors, and administrators.
* To maintain audit logs and security events.
* To provide JWT-secured REST APIs.
* To analyze healthcare data using dashboards and reports.
* To test and optimize the complete healthcare workflow.
* To prepare the system for deployment and real-world usage.

---

# 🏗️ System Architecture

MediTrack follows a layered architecture.

```text
┌─────────────────────────────────────────────┐
│                   USERS                     │
│                                             │
│     Patient      Doctor       Admin         │
└──────────────────────┬──────────────────────┘
                       │
                       ▼
┌─────────────────────────────────────────────┐
│             PRESENTATION LAYER              │
│                                             │
│       HTML5 | CSS3 | JavaScript             │
│              Bootstrap 5                    │
└──────────────────────┬──────────────────────┘
                       │
                       ▼
┌─────────────────────────────────────────────┐
│             APPLICATION LAYER               │
│                                             │
│              Python Flask                   │
│                                             │
│ • Authentication                            │
│ • Role-Based Access Control                 │
│ • Patient Management                        │
│ • Appointment Management                    │
│ • Consultation Management                   │
│ • Prescription Management                   │
│ • Notification Management                   │
│ • Security Monitoring                       │
│ • Audit Logging                             │
│ • Analytics                                 │
│ • Reporting                                 │
│ • REST APIs                                 │
└──────────────────────┬──────────────────────┘
                       │
                       ▼
┌─────────────────────────────────────────────┐
│              DATA ACCESS LAYER              │
│                                             │
│               SQLAlchemy ORM                │
└──────────────────────┬──────────────────────┘
                       │
                       ▼
┌─────────────────────────────────────────────┐
│                DATABASE LAYER               │
│                                             │
│                  MySQL                      │
│                                             │
│ Patients | Staff | Appointments             │
│ Consultations | Prescriptions               │
│ Notifications | Audit Logs                  │
│ Security Events                             │
└─────────────────────────────────────────────┘
```

---

# 🔄 Complete Milestone Architecture

```text
                    MEDITRACK
                        │
                        ▼
        ┌───────────────────────────┐
        │       MILESTONE 1         │
        │  Patient + Appointment    │
        └─────────────┬─────────────┘
                      │
                      ▼
        ┌───────────────────────────┐
        │       MILESTONE 2         │
        │ Consultation + Prescription│
        └─────────────┬─────────────┘
                      │
                      ▼
        ┌───────────────────────────┐
        │       MILESTONE 3         │
        │ Security + APIs +          │
        │ Notifications              │
        └─────────────┬─────────────┘
                      │
                      ▼
        ┌───────────────────────────┐
        │       MILESTONE 4         │
        │ Analytics + Testing +      │
        │ Optimization + Deployment  │
        └─────────────┬─────────────┘
                      │
                      ▼
              ┌───────────────┐
              │ FINAL SYSTEM  │
              └───────────────┘
```

---

# 🚀 Milestone 1 – Patient & Appointment Management

## Patient Registration

The system allows new patients to create an account.

Features include:

* Auto-generated Patient IDs
* Secure registration
* Password hashing
* Duplicate prevention
* Username validation
* Email validation
* Phone number validation
* Registration review before submission

Example Patient IDs:

```text
PAT001
PAT002
PAT003
```

---

## Patient Profile Management

Patients can maintain and update their medical information.

Features include:

* Personal information
* Medical information
* Editable patient profile
* BMI calculation
* Profile photo upload
* Profile completion tracking
* Medical summary
* Last updated information
* QR code generation

---

## Patient Database Management

The system provides centralized management of patient records.

Features include:

* Search patient records
* Filter patient records
* Pagination
* View patient details
* Soft delete patient records
* Patient information management

---

## Appointment Management

Patients can book and manage appointments.

Features include:

* Department selection
* Doctor selection
* Available slot selection
* Appointment booking
* Double-booking prevention
* Automatic blocking of booked slots
* Appointment rescheduling
* Appointment cancellation
* Appointment status tracking
* Waiting position information

Appointment workflow:

```text
Select Department
        ↓
Select Doctor
        ↓
Check Available Slots
        ↓
Select Appointment Time
        ↓
Check Double Booking
        ↓
Appointment Confirmed
```

---

# 🩺 Milestone 2 – Consultations & Prescriptions

Milestone 2 extends the healthcare workflow by introducing consultation and prescription management.

## Consultation Management

Doctors and authorized staff can record patient consultations.

Information includes:

* Patient information
* Symptoms
* Diagnosis
* Treatment
* Doctor notes
* Consultation date
* Linked appointment

Example consultation IDs:

```text
CON001
CON002
CON003
```

Features include:

* Create consultation
* View consultation history
* Search consultations
* Filter by patient
* Filter by doctor
* View consultation details

---

## Prescription Management

The system allows doctors to create digital prescriptions.

Features include:

* Auto-generated prescription IDs
* Multiple medicines
* Medicine name
* Dosage
* Frequency
* Duration
* Instructions
* Prescription history
* Printable prescription

Example Prescription IDs:

```text
RX001
RX002
RX003
```

Workflow:

```text
Consultation
      ↓
Diagnosis
      ↓
Treatment Decision
      ↓
Add Medicines
      ↓
Generate Prescription
      ↓
Patient Record Updated
```

---

## Patient Medical History

The patient detail page provides a centralized view of medical information.

```text
Patient Details
│
├── Overview
│
├── Appointments
│
├── Consultations
│
└── Prescriptions
```

---

# 🔐 Milestone 3 – Notifications, Security & APIs

Milestone 3 focuses on securing the healthcare system and connecting the application through REST APIs.

## User Roles

MediTrack supports three major user roles:

```text
Patient
Doctor
Admin
```

### Patient

Patients can:

* Access their dashboard
* Manage their profile
* Book appointments
* View notifications
* View their own consultations
* View their own prescriptions

### Doctor

Doctors can:

* View patient records
* Manage consultations
* Create prescriptions
* View consultation history
* Access authorized APIs

### Admin

Administrators can:

* Manage patient records
* Monitor audit logs
* Monitor security events
* Access security center
* Manage administrative healthcare information

---

## Role-Based Access Control

The system implements Role-Based Access Control (RBAC).

```text
User Login
     ↓
Authentication
     ↓
Identify User Role
     ↓
Check Permissions
     ↓
Allow / Deny Access
```

Unauthorized access attempts are blocked and recorded.

---

## Notifications

Patients receive in-app notifications for important healthcare events.

Notification types include:

* Appointment Reminder
* Prescription Alert
* Follow-Up Reminder
* Missed Appointment Alert

Example:

```text
Appointment Booked
       ↓
Appointment Date Approaches
       ↓
Reminder Generated
       ↓
Patient Notification
```

---

## Audit Logging

The system records important actions performed by users.

Audit information includes:

* User
* Role
* Action
* Resource
* IP Address
* Timestamp

Actions include:

* Login
* Logout
* Registration
* Appointment booking
* Consultation creation
* Prescription creation
* Patient update
* API access

---

## Security Monitoring

The system monitors suspicious and unauthorized activities.

Security features include:

* Failed login monitoring
* Unauthorized access detection
* Brute-force attempt detection
* Security event logging

Example:

```text
Failed Login Attempts
        ↓
Repeated Attempts Detected
        ↓
Threshold Reached
        ↓
BRUTE_FORCE_SUSPECTED
        ↓
Security Event Logged
```

---

## JWT-Secured REST APIs

The system provides secure REST APIs under:

```text
/api/v1/
```

Authentication workflow:

```text
User Login
     ↓
Verify Credentials
     ↓
Generate JWT Token
     ↓
Send Token to Client
     ↓
Protected API Request
     ↓
Validate JWT
     ↓
Allow / Reject Request
```

Main API functionality includes:

```text
POST   /api/v1/auth/login

GET    /api/v1/patients
POST   /api/v1/patients
GET    /api/v1/patients/<id>
PUT    /api/v1/patients/<id>
DELETE /api/v1/patients/<id>

GET    /api/v1/appointments
POST   /api/v1/appointments

GET    /api/v1/consultations
POST   /api/v1/consultations

GET    /api/v1/prescriptions
POST   /api/v1/prescriptions
```

---

# 📊 Milestone 4 – Analytics, Testing & Finalization

Milestone 4 focuses on making the complete MediTrack system ready for final use.

The four major areas are:

```text
Analytics
    +
Testing
    +
Optimization
    +
Documentation & Deployment
```

---

# 📈 Analytics Dashboard

Analytics converts raw healthcare data into useful information.

The administrative dashboard provides information about:

* Total patients
* Total appointments
* Today's appointments
* Completed appointments
* Cancelled appointments
* Pending appointments
* Consultation statistics
* Prescription statistics
* Doctor workload
* Patient demographics
* Patient registration trends
* Visit trends
* Doctor availability

---

## Appointment Analytics

The system analyzes appointment information.

Metrics include:

```text
Total Appointments
Completed Appointments
Cancelled Appointments
Pending Appointments
Missed Appointments
```

Example:

```text
Total Appointments: 500
Completed: 420
Cancelled: 50
Pending: 30
```

---

## Patient Analytics

Patient information can be analyzed based on demographics.

Analytics includes:

* Total patients
* New patient registrations
* Age groups
* Gender distribution

Example:

```text
0–18 Years     → 150
19–40 Years    → 450
41–60 Years    → 400
60+ Years      → 250
```

---

## Visit Trends

The system analyzes patient visits over time.

Example:

```text
Monday      → 80
Tuesday     → 95
Wednesday   → 70
Thursday    → 110
Friday      → 90
```

This helps administrators understand:

* Peak hospital days
* Patient flow
* Appointment demand
* Healthcare resource requirements

---

## Doctor Analytics

The system provides operational information about doctors.

Metrics include:

* Number of consultations
* Patient workload
* Appointment activity
* Doctor availability

Example:

```text
Doctor              Consultations

Dr. Ravi                  120
Dr. Priya                 140
Dr. Kumar                  95
```

---

# 📄 Reporting

MediTrack provides administrative reports that can be exported and shared.

Supported report formats include:

```text
CSV
PDF
```

---

## CSV Reports

CSV reports can be used with spreadsheet software.

Example:

```text
Patient ID,Patient,Doctor,Date,Status
PAT001,Rahul,Dr Ravi,20-08-2026,Completed
PAT002,Arun,Dr Priya,20-08-2026,Pending
```

Reports can include:

* Patient reports
* Appointment reports
* Consultation reports
* Prescription reports
* Doctor activity reports

---

## PDF Reports

PDF reports provide formatted healthcare and operational summaries.

Example:

```text
MEDITRACK

MONTHLY APPOINTMENT REPORT

Total Appointments: 500

Completed: 420
Cancelled: 50
Pending: 30
```

---

# 🧪 Testing

Milestone 4 validates whether all MediTrack modules work correctly.

Testing includes:

```text
Functional Testing
        ↓
Integration Testing
        ↓
Security Testing
        ↓
Performance Testing
        ↓
User Acceptance Testing
```

---

## Integration Testing

The complete healthcare workflow is tested.

```text
Registration
     ↓
Appointment
     ↓
Doctor Login
     ↓
Consultation
     ↓
Prescription
     ↓
Notification
     ↓
Audit Log
     ↓
Analytics
```

Each module must successfully communicate with the next module.

---

## Security Testing

Security testing verifies authentication and authorization.

Tests include:

```text
Correct Password
        ↓
Login Success
```

```text
Wrong Password
        ↓
Login Failure
```

```text
Invalid JWT
        ↓
Request Rejected
```

```text
Expired JWT
        ↓
Request Rejected
```

Unauthorized patient record access:

```text
Patient
   ↓
Try Accessing Another Patient Record
   ↓
Authorization Check
   ↓
ACCESS DENIED
   ↓
Security Event Logged
```

---

## Appointment Conflict Testing

The system tests appointment double-booking prevention.

Example:

```text
Doctor: Dr. Ravi
Time: 10:00 AM

Patient A → Appointment Booked

Patient B → Same Doctor + Same Time

Result:
Slot Already Booked
```

---

## Performance Testing

Performance testing checks whether the system remains responsive with large amounts of data.

Testing includes:

* Multiple users
* Large patient records
* Large appointment records
* Database query performance

The system is evaluated for handling approximately:

```text
10,000 Patient Records
```

without significant performance degradation.

---

# ⚡ Database Optimization

Database optimization improves system performance.

Optimization techniques include:

* Avoiding unnecessary queries
* Retrieving only required data
* Using appropriate database indexes
* Optimizing frequently used queries
* Efficient pagination
* Efficient search operations

Architecture:

```text
User Request
      ↓
Optimized Query
      ↓
SQLAlchemy ORM
      ↓
MySQL Database
      ↓
Required Data
      ↓
User Interface
```

---

# 📅 Appointment Scheduling Optimization

Appointment scheduling is optimized for efficient availability checking.

Workflow:

```text
Patient Requests Appointment
           ↓
Check Doctor Availability
           ↓
      Is Slot Available?
         ↙       ↘
       YES        NO
        ↓          ↓
      Book      Reject
Appointment      Request
```

The system ensures efficient scheduling even as appointment records increase.

---

# 📝 Documentation

The MediTrack project includes complete technical documentation.

Documentation covers:

* Project overview
* System architecture
* Technology stack
* Database structure
* Application modules
* API documentation
* Authentication
* Authorization
* Installation instructions
* Configuration
* Testing procedures
* Deployment guide

---

# 🔌 API Documentation

Each API is documented with:

* Endpoint
* HTTP method
* Purpose
* Request format
* Response format
* Authentication requirements
* Error responses

Example:

```text
Endpoint:
POST /api/v1/patients

Purpose:
Create a patient record.

Request:
Name
Age
Gender
Phone

Response:
Patient Created Successfully
```

---

# 🚀 Deployment Guide

Deployment makes MediTrack available outside the local development environment.

Deployment workflow:

```text
Development
      ↓
Build
      ↓
Testing
      ↓
Optimization
      ↓
Configuration
      ↓
Deployment
      ↓
Server
      ↓
Users
```

Deployment documentation includes:

* System requirements
* Dependency installation
* Database configuration
* Environment variables
* Application configuration
* Application startup
* Production deployment guidelines

---

# 👥 User Acceptance Testing

User Acceptance Testing (UAT) checks whether the system is useful and easy to use.

Users evaluate:

* Ease of registration
* Appointment booking process
* Patient record accessibility
* Dashboard usefulness
* Overall system usability

The project aims for:

```text
Target User Satisfaction: 85% or Higher
```

among healthcare staff and patients.

---

# 🗄️ Database Architecture

The main database tables include:

```text
patients
│
├── appointments
│
├── consultations
│
├── prescriptions
│       │
│       └── prescription_items
│
└── notifications
```

Administrative and security tables:

```text
staff
audit_logs
security_events
```

---

# 💻 Technology Stack

## Backend

```text
Python
Flask
```

## Database

```text
MySQL
SQLAlchemy ORM
```

## Frontend

```text
HTML5
CSS3
JavaScript
Bootstrap 5
```

## Security

```text
Password Hashing
Session Authentication
Role-Based Access Control
JWT Authentication
HS256 JWT Signing
Audit Logging
Security Monitoring
```

## Reporting

```text
CSV Export
PDF Export
```

---

# 📁 Project Structure

```text
meditrack/
│
├── app.py
├── requirements.txt
├── schema.sql
├── sample_data.sql
├── README.md
│
├── static/
│   ├── css/
│   │   └── styles.css
│   │
│   ├── js/
│   │   └── app.js
│   │
│   ├── uploads/
│   │   ├── profiles/
│   │   └── qrcodes/
│   │
│   └── reports/
│
├── templates/
│   ├── layout.html
│   ├── home.html
│   ├── login.html
│   ├── register.html
│   ├── dashboard.html
│   ├── profile.html
│   ├── patients.html
│   ├── appointments.html
│   ├── consultations.html
│   ├── prescriptions.html
│   ├── notifications.html
│   ├── analytics.html
│   ├── reports.html
│   ├── security_center.html
│   └── api_docs.html
│
└── tests/
    ├── test_auth.py
    ├── test_appointments.py
    ├── test_consultations.py
    ├── test_security.py
    └── test_integration.py
```

---

# ⚙️ Installation

## 1. Clone the Repository

```bash
git clone YOUR_REPOSITORY_URL
```

## 2. Navigate to the Project

```bash
cd meditrack
```

## 3. Create a Virtual Environment

```bash
python -m venv venv
```

## 4. Activate the Virtual Environment

### Windows

```bash
venv\Scripts\activate
```

### Linux/macOS

```bash
source venv/bin/activate
```

## 5. Install Dependencies

```bash
pip install -r requirements.txt
```

---

# 🗃️ Database Setup

Create the MySQL database:

```sql
CREATE DATABASE meditrack_db;
```

Import the database schema:

```bash
mysql -u root -p meditrack_db < schema.sql
```

Optional sample data:

```bash
mysql -u root -p meditrack_db < sample_data.sql
```

---

# 🔧 Environment Configuration

### Windows PowerShell

```powershell
$env:DATABASE_URL="mysql+pymysql://root:YOUR_PASSWORD@localhost/meditrack_db?charset=utf8mb4"

$env:SECRET_KEY="your-secret-key"

$env:JWT_SECRET="your-jwt-secret"
```

### Linux/macOS

```bash
export DATABASE_URL="mysql+pymysql://root:YOUR_PASSWORD@localhost/meditrack_db?charset=utf8mb4"

export SECRET_KEY="your-secret-key"

export JWT_SECRET="your-jwt-secret"
```

---

# ▶️ Running the Application

Run the application:

```bash
python app.py
```

Open the application:

```text
http://127.0.0.1:5000
```

---

# 🔐 Default Workflow

```text
Register
   ↓
Login
   ↓
Complete Profile
   ↓
Book Appointment
   ↓
Doctor Consultation
   ↓
Prescription
   ↓
Patient Notification
   ↓
Audit Logging
   ↓
Analytics & Reporting
```

---

# 📊 Complete Feature List

## Milestone 1

* Patient Registration
* Patient Profile Management
* QR Code Generation
* BMI Calculation
* Patient Database
* Search and Filtering
* Appointment Scheduling
* Appointment Rescheduling
* Appointment Cancellation
* Double-Booking Prevention

## Milestone 2

* Consultation Management
* Consultation History
* Prescription Management
* Multiple Medicines
* Prescription History
* Printable Prescriptions
* Patient Medical History

## Milestone 3

* Patient, Doctor and Admin Roles
* Role-Based Access Control
* In-App Notifications
* Audit Logging
* Security Monitoring
* Failed Login Detection
* Brute-Force Detection
* JWT Authentication
* REST APIs

## Milestone 4

* Analytics Dashboard
* Appointment Analytics
* Patient Analytics
* Visit Trends
* Doctor Analytics
* CSV Reports
* PDF Reports
* Integration Testing
* Security Testing
* Performance Testing
* Database Optimization
* Appointment Optimization
* User Acceptance Testing
* Documentation
* Deployment Guide

---

# 🧠 Simple Milestone Summary

```text
Milestone 1 → MANAGE
Manage patients and appointments.

Milestone 2 → TREAT
Record consultations and treatment.

Milestone 3 → PROTECT & CONNECT
Secure the system and connect it through APIs.

Milestone 4 → ANALYZE & FINALIZE
Analyze data, test the system, optimize performance,
document the project, and prepare for deployment.
```

---

# 🔮 Future Enhancements

Future versions of MediTrack can include:

* AI-based disease prediction
* Medicine reminder system
* Telemedicine and video consultation
* Email notifications
* SMS notifications
* Mobile application
* Online payment integration
* Advanced data visualization
* Machine learning-based patient analytics
* Cloud deployment
* Multi-hospital support
* Real-time ambulance tracking
* Integration with external healthcare systems



# 🏁 Conclusion

MediTrack is a complete Integrated Patient Care Management System designed to digitize and improve healthcare management workflows.

The project was developed progressively across four milestones. Starting with patient and appointment management, it was extended with consultations and prescriptions, followed by security, notifications, audit logging, and REST APIs. The final milestone adds analytics, reporting, testing, optimization, documentation, and deployment preparation.

The final system provides a centralized, secure, scalable, and organized platform for managing important patient care processes.

```text
MANAGE
   ↓
TREAT
   ↓
PROTECT & CONNECT
   ↓
ANALYZE & FINALIZE
   ↓
MEDITRACK – FINAL INTEGRATED SYSTEM
```

---

