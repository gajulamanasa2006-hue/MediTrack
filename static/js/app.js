document.addEventListener('DOMContentLoaded', () => {
  document.querySelectorAll('.toast').forEach((toastEl) => new bootstrap.Toast(toastEl).show());

  const sidebarToggle = document.getElementById('sidebarToggle');
  const sidebar = document.getElementById('sidebar');
  if (sidebarToggle && sidebar) {
    sidebarToggle.addEventListener('click', () => sidebar.classList.toggle('show'));
  }

  const heightField = document.getElementById('height');
  const weightField = document.getElementById('weight');
  const bmiField = document.getElementById('bmi');
  const calcBMI = () => {
    if (!heightField || !weightField || !bmiField) return;
    const height = parseFloat(heightField.value || '0');
    const weight = parseFloat(weightField.value || '0');
    if (height > 0 && weight > 0) {
      const bmi = (weight / Math.pow(height / 100, 2)).toFixed(2);
      bmiField.value = bmi;
    }
  };
  [heightField, weightField].forEach(el => el && el.addEventListener('input', calcBMI));

  const registerForm = document.getElementById('registrationForm');
  const summaryModalEl = document.getElementById('summaryModal');
  if (registerForm && summaryModalEl) {
    const summaryModal = new bootstrap.Modal(summaryModalEl);
    const summaryList = document.getElementById('registrationSummary');
    const summaryButton = document.getElementById('previewRegistration');

    summaryButton.addEventListener('click', () => {
      if (!registerForm.checkValidity()) {
        registerForm.classList.add('was-validated');
        return;
      }
      const formData = new FormData(registerForm);
      const fields = [
        ['Patient ID', formData.get('patient_id')],
        ['Name', `${formData.get('first_name')} ${formData.get('last_name')}`],
        ['Age / Gender', `${formData.get('age')} / ${formData.get('gender')}`],
        ['Date of Birth', formData.get('dob')],
        ['Mobile', formData.get('phone')],
        ['Email', formData.get('email')],
        ['Address', formData.get('address')],
        ['Username', formData.get('username')]
      ];
      summaryList.innerHTML = fields.map(([label, value]) => `<li class="d-flex justify-content-between gap-3"><span class="text-muted">${label}</span><strong class="text-end">${value || '-'}</strong></li>`).join('');
      summaryModal.show();
    });
  }

  const departmentField = document.getElementById('department');
  const doctorField = document.getElementById('doctor');
  const dateField = document.getElementById('appointment_date');
  const slotField = document.getElementById('time_slot');

  async function loadDoctors() {
    if (!departmentField || !doctorField) return;
    const department = departmentField.value;
    doctorField.innerHTML = '<option value="">Select doctor</option>';
    slotField && (slotField.innerHTML = '<option value="">Select time slot</option>');
    if (!department) return;
    const response = await fetch(`/api/doctors?department=${encodeURIComponent(department)}`);
    const data = await response.json();
    data.doctors.forEach((doctor) => {
      const option = document.createElement('option');
      option.value = doctor;
      option.textContent = doctor;
      doctorField.appendChild(option);
    });
  }

  async function loadSlots() {
    if (!doctorField || !dateField || !slotField) return;
    const doctor = doctorField.value;
    const date = dateField.value;
    slotField.innerHTML = '<option value="">Select time slot</option>';
    if (!doctor || !date) return;
    const response = await fetch(`/api/slots?doctor=${encodeURIComponent(doctor)}&date=${encodeURIComponent(date)}`);
    const data = await response.json();
    data.slots.forEach((slot) => {
      const option = document.createElement('option');
      option.value = slot;
      option.textContent = slot;
      slotField.appendChild(option);
    });
  }

  departmentField && departmentField.addEventListener('change', loadDoctors);
  doctorField && doctorField.addEventListener('change', loadSlots);
  dateField && dateField.addEventListener('change', loadSlots);

  // --- Milestone 2 additions -------------------------------------------

  // Consultation form: load that patient's appointments into the optional link dropdown
  const consultPatientField = document.getElementById('consult_patient_id');
  const consultAppointmentField = document.getElementById('consult_appointment_id');
  async function loadPatientAppointments(preselect) {
    if (!consultPatientField || !consultAppointmentField) return;
    const patientId = consultPatientField.value;
    consultAppointmentField.innerHTML = '<option value="">No linked appointment</option>';
    if (!patientId) return;
    const response = await fetch(`/api/patient-appointments?patient_id=${encodeURIComponent(patientId)}`);
    const data = await response.json();
    data.appointments.forEach((item) => {
      const option = document.createElement('option');
      option.value = item.id;
      option.textContent = item.label;
      if (preselect && preselect === item.id) option.selected = true;
      consultAppointmentField.appendChild(option);
    });
  }
  if (consultPatientField) {
    const preselectedAppointment = consultAppointmentField ? consultAppointmentField.dataset.preselect : '';
    if (consultPatientField.value) loadPatientAppointments(preselectedAppointment);
    consultPatientField.addEventListener('change', () => loadPatientAppointments());
  }

  // Prescription form: load that patient's consultations into the optional link dropdown
  const rxPatientField = document.getElementById('rx_patient_id');
  const rxConsultationField = document.getElementById('rx_consultation_id');
  async function loadPatientConsultations(preselect) {
    if (!rxPatientField || !rxConsultationField) return;
    const patientId = rxPatientField.value;
    rxConsultationField.innerHTML = '<option value="">No linked consultation</option>';
    if (!patientId) return;
    const response = await fetch(`/api/patient-consultations?patient_id=${encodeURIComponent(patientId)}`);
    const data = await response.json();
    data.consultations.forEach((item) => {
      const option = document.createElement('option');
      option.value = item.id;
      option.textContent = item.label;
      if (preselect && preselect === item.id) option.selected = true;
      rxConsultationField.appendChild(option);
    });
  }
  if (rxPatientField) {
    const preselectedConsultation = rxConsultationField ? rxConsultationField.dataset.preselect : '';
    if (rxPatientField.value) loadPatientConsultations(preselectedConsultation);
    rxPatientField.addEventListener('change', () => loadPatientConsultations());
  }

  // Prescription form: dynamic "Add Medicine" rows
  const medicineList = document.getElementById('medicineList');
  const addMedicineBtn = document.getElementById('addMedicineBtn');
  let medicineRowCount = medicineList ? medicineList.querySelectorAll('.medicine-row').length : 0;

  function buildMedicineRow() {
    medicineRowCount += 1;
    const wrapper = document.createElement('div');
    wrapper.className = 'medicine-row border rounded-4 p-3 mb-3 position-relative';
    wrapper.innerHTML = `
      <div class="d-flex justify-content-between align-items-center mb-2">
        <div class="fw-semibold text-primary">Medicine ${medicineRowCount}</div>
        <button type="button" class="btn btn-sm btn-outline-danger rounded-pill remove-medicine">Remove</button>
      </div>
      <div class="row g-3">
        <div class="col-md-6"><label class="form-label">Medicine Name</label><input class="form-control" name="medicine_name[]" placeholder="e.g. Paracetamol 500 mg" required></div>
        <div class="col-md-3"><label class="form-label">Dosage</label><input class="form-control" name="dosage[]" placeholder="1 tablet" required></div>
        <div class="col-md-3"><label class="form-label">Frequency</label><input class="form-control" name="frequency[]" placeholder="Twice daily" required></div>
        <div class="col-md-4"><label class="form-label">Duration</label><input class="form-control" name="duration[]" placeholder="5 days" required></div>
        <div class="col-md-8"><label class="form-label">Instructions</label><input class="form-control" name="instructions[]" placeholder="After food"></div>
      </div>`;
    wrapper.querySelector('.remove-medicine').addEventListener('click', () => {
      if (medicineList.querySelectorAll('.medicine-row').length > 1) {
        wrapper.remove();
      }
    });
    return wrapper;
  }

  if (addMedicineBtn && medicineList) {
    addMedicineBtn.addEventListener('click', () => {
      medicineList.appendChild(buildMedicineRow());
    });
    medicineList.querySelectorAll('.remove-medicine').forEach((btn) => {
      btn.addEventListener('click', () => {
        if (medicineList.querySelectorAll('.medicine-row').length > 1) {
          btn.closest('.medicine-row').remove();
        }
      });
    });
  }
});
