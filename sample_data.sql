USE meditrack_db;

INSERT INTO patients (patient_id, first_name, last_name, age, gender, dob, phone, email, address, username, password, qr_code_path, is_active)
VALUES
('PAT001', 'Ava', 'Johnson', 29, 'Female', '1997-02-14', '5551230001', 'ava.johnson@example.com', '21 Riverstone Avenue', 'avaj', 'scrypt:32768:8:1$E8uWDmL2AlbvrKIO$2f1f8fdcbeef52c44949c31607eee7ca028c4fd8d227ad379452bbd7badb57145ae9f2fec4863a7d6cf14bf0806c7ec2195fb86ddd255d1a560e197fcb57e404', NULL, 1),
('PAT002', 'Liam', 'Turner', 41, 'Male', '1985-08-09', '5551230002', 'liam.turner@example.com', '44 Sunrise Park', 'liamt', 'scrypt:32768:8:1$E8uWDmL2AlbvrKIO$2f1f8fdcbeef52c44949c31607eee7ca028c4fd8d227ad379452bbd7badb57145ae9f2fec4863a7d6cf14bf0806c7ec2195fb86ddd255d1a560e197fcb57e404', NULL, 1);

INSERT INTO patient_profiles (patient_id, blood_group, height, weight, bmi, blood_pressure, pulse_rate, oxygen_level, allergies, diseases, previous_history, surgeries, medications, family_history, lifestyle, emergency_contact_name, emergency_contact_phone, profile_photo)
VALUES
('PAT001', 'O+', 165.00, 59.00, 21.67, '118/76', '72 bpm', '98', 'Penicillin', 'None', 'Seasonal migraines', 'None', 'Vitamin D', 'Maternal hypertension', 'Non-smoker / Social alcohol', 'Mia Johnson', '5557001010', NULL),
('PAT002', 'A+', 178.00, 82.00, 25.88, '126/82', '78 bpm', '97', 'Dust', 'Mild asthma', 'Sports-related knee pain', 'Appendectomy', 'Inhaler', 'Paternal diabetes', 'Non-smoker / No alcohol', 'Sophia Turner', '5557002020', NULL);

INSERT INTO appointments (appointment_id, patient_id, department, doctor, appointment_date, time_slot, reason, status, waiting_position)
VALUES
('APT001', 'PAT001', 'Cardiology', 'Dr. Amelia Carter', DATE_ADD(CURDATE(), INTERVAL 3 DAY), '09:00 AM - 09:30 AM', 'Routine heart health review', 'Confirmed', 1),
('APT002', 'PAT002', 'General Medicine', 'Dr. Ethan Brooks', DATE_ADD(CURDATE(), INTERVAL 5 DAY), '10:00 AM - 10:30 AM', 'Follow-up consultation', 'Pending', 2);

-- ---------------------------------------------------------------------
-- Milestone 2 additions: sample consultations & prescriptions
-- ---------------------------------------------------------------------

INSERT INTO consultations (consultation_id, patient_id, appointment_id, doctor, symptoms, diagnosis, treatment, consultation_date, notes)
VALUES
('CON001', 'PAT002', 'APT002', 'Dr. Ethan Brooks', 'Cough, mild fever, congestion', 'Seasonal viral infection', 'Rest, fluids, symptomatic care', CURDATE(), 'Advised follow-up if symptoms persist beyond 5 days.');

INSERT INTO prescriptions (prescription_id, patient_id, doctor, consultation_id, prescription_date)
VALUES
('RX001', 'PAT002', 'Dr. Ethan Brooks', 'CON001', CURDATE());

INSERT INTO prescription_items (prescription_id, medicine_name, dosage, frequency, duration, instructions)
VALUES
('RX001', 'Paracetamol 500 mg', '1 tablet', 'Twice daily', '5 days', 'After food'),
('RX001', 'Cetirizine 10 mg', '1 tablet', 'Once daily', '3 days', 'At night');

-- ---------------------------------------------------------------------
-- Milestone 3 additions: default staff accounts
-- (Matches the idempotent auto-seed in app.py; safe to import once.)
-- Default credentials: admin/Admin@123, doctor01/Doctor@123
-- ---------------------------------------------------------------------

INSERT INTO staff (staff_id, name, username, email, password, role, specialization)
VALUES
('ADM001', 'System Administrator', 'admin', 'admin@meditrack.local',
 'scrypt:32768:8:1$Jd0M8iivw9yHKytR$0a0caaad5b3ed410a5c8b5f27982a927508ad7e260bbb9b3c1c183f72678713a46e2701ec9b341a3c92070c44eb450a093b8b2d81cc08a8d10c911ce51ad8e5c',
 'admin', NULL),
('DOC001', 'Dr. Amelia Carter', 'doctor01', 'amelia.carter@meditrack.local',
 'scrypt:32768:8:1$Ge3cotpbsxfo4bFz$e2a643f36a8eb51025a3d98f85c967121edcbdf02c8432dca228d1dfd2a9b9f117583a0a9e12dfd972569112aa763b8454f3c09d0d9ed2f0a6df78ab6165e47d',
 'doctor', 'Cardiology');
-- These hashes correctly correspond to Admin@123 / Doctor@123. app.py's
-- startup seeding also creates these same two accounts automatically if the
-- staff table is empty, so importing this file manually is optional.
