/**
 * Prediction Form — Client-side validation and UX
 */
document.addEventListener('DOMContentLoaded', function() {
    const form = document.getElementById('predictionForm');
    const submitBtn = document.getElementById('predictBtn');

    if (!form || !submitBtn) return;

    form.addEventListener('submit', function(e) {
        // Validate required fields
        const attendance = parseFloat(form.querySelector('[name="attendance"]').value);
        const studyHours = parseFloat(form.querySelector('[name="study_hours"]').value);
        const previousMarks = parseFloat(form.querySelector('[name="previous_marks"]').value);
        const internalMarks = parseFloat(form.querySelector('[name="internal_marks"]').value);
        const assignments = parseFloat(form.querySelector('[name="assignments"]').value);

        let errors = [];

        if (isNaN(attendance) || attendance < 0 || attendance > 100) {
            errors.push('Attendance must be between 0 and 100');
        }
        if (isNaN(studyHours) || studyHours < 0 || studyHours > 24) {
            errors.push('Daily study hours must be between 0 and 24');
        }
        if (isNaN(previousMarks) || previousMarks < 0 || previousMarks > 100) {
            errors.push('Previous marks must be between 0 and 100');
        }
        if (isNaN(internalMarks) || internalMarks < 0 || internalMarks > 30) {
            errors.push('Internal marks must be between 0 and 30');
        }
        if (isNaN(assignments) || assignments < 0 || assignments > 20) {
            errors.push('Assignments must be between 0 and 20');
        }

        if (errors.length > 0) {
            e.preventDefault();
            alert('Please fix the following:\n\n' + errors.join('\n'));
            return;
        }

        // Show loading state
        submitBtn.disabled = true;
        submitBtn.innerHTML = '<i class="fas fa-spinner fa-spin"></i> Analyzing...';
    });

    // Input hover/focus animations
    const inputs = form.querySelectorAll('.form-input');
    inputs.forEach(input => {
        input.addEventListener('focus', function() {
            this.closest('.form-group')?.classList.add('focused');
        });
        input.addEventListener('blur', function() {
            this.closest('.form-group')?.classList.remove('focused');
        });
    });
});
