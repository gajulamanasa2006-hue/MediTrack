CREATE DATABASE IF NOT EXISTS meditrack_db;
USE meditrack_db;

CREATE TABLE IF NOT EXISTS patients (
  id INT AUTO_INCREMENT PRIMARY KEY,
  patient_id VARCHAR(20) NOT NULL UNIQUE,
  first_name VARCHAR(80) NOT NULL,
  last_name VARCHAR(80) NOT NULL,
  age INT NOT NULL,
  gender VARCHAR(20) NOT NULL,
  dob DATE NOT NULL,
  phone VARCHAR(20) NOT NULL UNIQUE,
  email VARCHAR(120) NOT NULL UNIQUE,
  address TEXT NOT NULL,
  username VARCHAR(80) NOT NULL UNIQUE,
  password VARCHAR(255) NOT NULL,
  qr_code_path VARCHAR(255),
  is_active TINYINT(1) NOT NULL DEFAULT 1,
  created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS patient_profiles (
  profile_id INT AUTO_INCREMENT PRIMARY KEY,
  patient_id VARCHAR(20) NOT NULL,
  blood_group VARCHAR(10),
  height DECIMAL(6,2),
  weight DECIMAL(6,2),
  bmi DECIMAL(6,2),
  blood_pressure VARCHAR(30),
  pulse_rate VARCHAR(30),
  oxygen_level VARCHAR(30),
  allergies TEXT,
  diseases TEXT,
  previous_history TEXT,
  surgeries TEXT,
  medications TEXT,
  family_history TEXT,
  lifestyle VARCHAR(120),
  emergency_contact_name VARCHAR(120),
  emergency_contact_phone VARCHAR(20),
  profile_photo VARCHAR(255),
  last_updated DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  CONSTRAINT fk_patient_profile_patient FOREIGN KEY (patient_id) REFERENCES patients(patient_id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS appointments (
  id INT AUTO_INCREMENT PRIMARY KEY,
  appointment_id VARCHAR(20) NOT NULL UNIQUE,
  patient_id VARCHAR(20) NOT NULL,
  department VARCHAR(120) NOT NULL,
  doctor VARCHAR(120) NOT NULL,
  appointment_date DATE NOT NULL,
  time_slot VARCHAR(40) NOT NULL,
  reason TEXT NOT NULL,
  status VARCHAR(20) NOT NULL DEFAULT 'Confirmed',
  waiting_position INT NOT NULL DEFAULT 1,
  created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
  updated_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  CONSTRAINT fk_appointment_patient FOREIGN KEY (patient_id) REFERENCES patients(patient_id) ON DELETE CASCADE,
  INDEX idx_appointment_lookup (doctor, appointment_date, time_slot)
);

-- ---------------------------------------------------------------------
-- Milestone 2 additions: Consultations & Prescriptions
-- (Appended without altering any table defined above.)
-- ---------------------------------------------------------------------

CREATE TABLE IF NOT EXISTS consultations (
  id INT AUTO_INCREMENT PRIMARY KEY,
  consultation_id VARCHAR(20) NOT NULL UNIQUE,
  patient_id VARCHAR(20) NOT NULL,
  appointment_id VARCHAR(20),
  doctor VARCHAR(120) NOT NULL,
  symptoms TEXT NOT NULL,
  diagnosis TEXT NOT NULL,
  treatment TEXT NOT NULL,
  consultation_date DATE NOT NULL,
  notes TEXT,
  created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
  CONSTRAINT fk_consultation_patient FOREIGN KEY (patient_id) REFERENCES patients(patient_id) ON DELETE CASCADE,
  CONSTRAINT fk_consultation_appointment FOREIGN KEY (appointment_id) REFERENCES appointments(appointment_id) ON DELETE SET NULL,
  INDEX idx_consultation_lookup (patient_id, doctor)
);

CREATE TABLE IF NOT EXISTS prescriptions (
  id INT AUTO_INCREMENT PRIMARY KEY,
  prescription_id VARCHAR(20) NOT NULL UNIQUE,
  patient_id VARCHAR(20) NOT NULL,
  doctor VARCHAR(120) NOT NULL,
  consultation_id VARCHAR(20),
  prescription_date DATE NOT NULL,
  created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
  CONSTRAINT fk_prescription_patient FOREIGN KEY (patient_id) REFERENCES patients(patient_id) ON DELETE CASCADE,
  CONSTRAINT fk_prescription_consultation FOREIGN KEY (consultation_id) REFERENCES consultations(consultation_id) ON DELETE SET NULL,
  INDEX idx_prescription_lookup (patient_id, doctor)
);

CREATE TABLE IF NOT EXISTS prescription_items (
  id INT AUTO_INCREMENT PRIMARY KEY,
  prescription_id VARCHAR(20) NOT NULL,
  medicine_name VARCHAR(150) NOT NULL,
  dosage VARCHAR(80) NOT NULL,
  frequency VARCHAR(80) NOT NULL,
  duration VARCHAR(80) NOT NULL,
  instructions VARCHAR(255),
  CONSTRAINT fk_prescription_item_prescription FOREIGN KEY (prescription_id) REFERENCES prescriptions(prescription_id) ON DELETE CASCADE
);

-- ---------------------------------------------------------------------
-- Milestone 3 additions: Staff accounts, Notifications, Audit Logs, Security
-- (Appended without altering any table defined above.)
-- ---------------------------------------------------------------------

CREATE TABLE IF NOT EXISTS staff (
  id INT AUTO_INCREMENT PRIMARY KEY,
  staff_id VARCHAR(20) NOT NULL UNIQUE,
  name VARCHAR(120) NOT NULL,
  username VARCHAR(80) NOT NULL UNIQUE,
  email VARCHAR(120) NOT NULL UNIQUE,
  password VARCHAR(255) NOT NULL,
  role VARCHAR(20) NOT NULL,
  specialization VARCHAR(120),
  is_active TINYINT(1) NOT NULL DEFAULT 1,
  created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS notifications (
  id INT AUTO_INCREMENT PRIMARY KEY,
  patient_id VARCHAR(20) NOT NULL,
  notif_type VARCHAR(40) NOT NULL,
  title VARCHAR(150) NOT NULL,
  message TEXT NOT NULL,
  related_type VARCHAR(40),
  related_id VARCHAR(20),
  is_read TINYINT(1) NOT NULL DEFAULT 0,
  created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
  CONSTRAINT fk_notification_patient FOREIGN KEY (patient_id) REFERENCES patients(patient_id) ON DELETE CASCADE,
  INDEX idx_notification_lookup (patient_id, is_read)
);

CREATE TABLE IF NOT EXISTS audit_logs (
  id INT AUTO_INCREMENT PRIMARY KEY,
  actor_label VARCHAR(160) NOT NULL,
  actor_role VARCHAR(20) NOT NULL,
  action VARCHAR(80) NOT NULL,
  resource VARCHAR(80),
  resource_id VARCHAR(60),
  ip_address VARCHAR(64),
  details TEXT,
  created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
  INDEX idx_audit_lookup (action, created_at)
);

CREATE TABLE IF NOT EXISTS security_events (
  id INT AUTO_INCREMENT PRIMARY KEY,
  event_type VARCHAR(60) NOT NULL,
  severity VARCHAR(20) NOT NULL DEFAULT 'medium',
  username VARCHAR(120),
  ip_address VARCHAR(64),
  details TEXT,
  created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
  INDEX idx_security_lookup (event_type, created_at)
);
