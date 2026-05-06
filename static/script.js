function openModal(modalId) {
    document.getElementById(modalId).classList.add("show");
}

function closeModal(modalId) {
    document.getElementById(modalId).classList.remove("show");
}

function openEditSymptomModal(id, name, severity, date, notes) {
    document.getElementById("editSymptomId").value = id;
    document.getElementById("editSymptomName").value = name;
    document.getElementById("editSymptomSeverity").value = severity;
    document.getElementById("editSymptomDate").value = date;
    document.getElementById("editSymptomNotes").value = notes;
    openModal("editSymptomModal");
}

function openEditAppointmentModal(id, doctor, doctorType, date, time, reason, notes, status) {
    document.getElementById("editAppointmentId").value = id;
    document.getElementById("editAppointmentDoctor").value = doctor;
    document.getElementById("editAppointmentDate").value = date;
    document.getElementById("editAppointmentTime").value = time;
    document.getElementById("editAppointmentReason").value = reason;
    document.getElementById("editAppointmentNotes").value = notes;
    document.getElementById("editAppointmentStatus").value = status;

    const select = document.getElementById("editDoctorTypeSelect");
    const customInput = document.getElementById("editCustomSpecialtyInput");

    const standardOptions = [
        "Primary Care",
        "Dentistry",
        "Optometry / Ophthalmology",
        "Neurology",
        "Cardiology",
        "Dermatology",
        "Gynecology",
        "Psychiatry",
        "Physical Therapy",
        "Other Specialty"
    ];

    if (standardOptions.includes(doctorType)) {
        select.value = doctorType;
        customInput.style.display = "none";
        customInput.required = false;
        customInput.value = "";
    } else {
        select.value = "Other Specialty";
        customInput.style.display = "block";
        customInput.required = true;
        customInput.value = doctorType;
    }

    openModal("editAppointmentModal");
}

function toggleEditCustomSpecialty() {
    const select = document.getElementById("editDoctorTypeSelect");
    const customInput = document.getElementById("editCustomSpecialtyInput");

    if (select.value === "Other Specialty") {
        customInput.style.display = "block";
        customInput.required = true;
    } else {
        customInput.style.display = "none";
        customInput.required = false;
        customInput.value = "";
    }
}

function showCategory(category, buttonElement) {
    const cards = document.querySelectorAll(".appointment-card");
    const buttons = document.querySelectorAll(".appt-category-btn");

    buttons.forEach((btn) => btn.classList.remove("active"));
    buttonElement.classList.add("active");

    let visibleCount = 0;

    cards.forEach((card) => {
        if (card.dataset.category === category) {
            card.style.display = "flex";
            visibleCount++;
        } else {
            card.style.display = "none";
        }
    });

    const emptyMessage = document.getElementById("appointmentEmptyMessage");
    if (emptyMessage) {
        emptyMessage.style.display = visibleCount === 0 ? "block" : "none";
    }
}

function toggleCustomSpecialty() {
    const select = document.getElementById("doctorTypeSelect");
    const customInput = document.getElementById("customSpecialtyInput");

    if (select.value === "Other Specialty") {
        customInput.style.display = "block";
        customInput.required = true;
    } else {
        customInput.style.display = "none";
        customInput.required = false;
        customInput.value = "";
    }
}

window.addEventListener("click", function (event) {
    const modals = document.querySelectorAll(".modal-overlay");
    modals.forEach((modal) => {
        if (event.target === modal) {
            modal.classList.remove("show");
        }
    });
});

window.addEventListener("DOMContentLoaded", function () {
    const firstButton = document.querySelector(".appt-category-btn.active");
    if (firstButton) {
        showCategory("Primary Care", firstButton);
    }
});

function updateMedicationTimeInputs() {
    const timesInput = document.getElementById("timesPerDayInput");
    const container = document.getElementById("medicationTimesContainer");

    let count = parseInt(timesInput.value, 10);

    if (isNaN(count) || count < 1) {
        count = 1;
    }

    if (count > 4) {
        count = 4;
    }

    timesInput.value = count;
    container.innerHTML = "";

    for (let i = 1; i <= count; i++) {
        const label = document.createElement("label");
        label.innerHTML = `
            Time ${i}
            <input type="time" name="medication_times" required>
        `;
        container.appendChild(label);
    }
}

function openEditMedicationModal(id, name, dosage, timesPerDay, times, days) {
    document.getElementById("editMedicationId").value = id;
    document.getElementById("editMedicationName").value = name;
    document.getElementById("editMedicationDosage").value = dosage;

    const timesInput = document.getElementById("editTimesPerDayInput");
    timesInput.value = timesPerDay;

    // Clear all day selections first
    document.querySelectorAll("#editMedicationModal input[name='days_of_week']")
        .forEach(cb => cb.checked = false);

    // Set selected days
    if (days) {
        const selectedDays = days.split(",");
        selectedDays.forEach(day => {
            const checkbox = document.querySelector(
                `#editMedicationModal input[value='${day}']`
            );
            if (checkbox) checkbox.checked = true;
        });
    }

    // Set time inputs
    updateEditMedicationTimeInputs();

    const timeList = times ? times.split(",") : [];
    const inputs = document.querySelectorAll("#editMedicationTimesContainer input");

    inputs.forEach((input, index) => {
        if (timeList[index]) {
            input.value = timeList[index];
        }
    });

    openModal("editMedicationModal");
}

function updateEditMedicationTimeInputs() {
    const timesInput = document.getElementById("editTimesPerDayInput");
    const container = document.getElementById("editMedicationTimesContainer");

    let count = parseInt(timesInput.value, 10);

    if (isNaN(count) || count < 1) count = 1;
    if (count > 4) count = 4;

    timesInput.value = count;
    container.innerHTML = "";

    for (let i = 1; i <= count; i++) {
        const label = document.createElement("label");
        label.innerHTML = `
            Time ${i}
            <input type="time" name="medication_times" required>
        `;
        container.appendChild(label);
    }
}