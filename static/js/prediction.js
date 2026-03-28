/**
 * Prediction Dashboard V2 — Real-time preview, suggestions, floating labels, Chart.js, Spline toggle
 */
document.addEventListener('DOMContentLoaded', function() {
    const form = document.getElementById('predictionForm');
    const submitBtn = document.getElementById('predictBtn');
    
    if (!form) return;

    // ═══ Floating Label Logic ═══
    initFloatingLabels();

    // ═══ Real-time Prediction & Suggestions ═══
    initRealTimePreview();

    // ═══ Form Submit with Loading ═══
    if (submitBtn) initFormSubmit(form, submitBtn);

    // ═══ Charts ═══
    initTrendChart();
    initLiveGauge(null);

    // ═══ Input Focus Animations ═══
    initInputAnimations();
});

// ─── Floating Labels ────────────────────────────────────────────
function initFloatingLabels() {
    const inputs = document.querySelectorAll('.float-label-group input:not([type="hidden"]), .float-label-group select');
    
    inputs.forEach(input => {
        updateFloatLabel(input);
        
        input.addEventListener('input', () => updateFloatLabel(input));
        input.addEventListener('change', () => updateFloatLabel(input));
        input.addEventListener('focus', () => {
            const label = input.closest('.float-label-group')?.querySelector('.float-label');
            if (label) label.classList.add('has-value');
        });
        input.addEventListener('blur', () => updateFloatLabel(input));
    });
}

function updateFloatLabel(input) {
    const label = input.closest('.float-label-group')?.querySelector('.float-label');
    if (!label) return;
    
    if ((input.value && input.value.trim() !== '') || input.tagName === 'SELECT') {
        label.classList.add('has-value');
    } else {
        label.classList.remove('has-value');
    }
}

// ─── Real-time Prediction Preview ───────────────────────────────
function initRealTimePreview() {
    const fields = ['attendanceInput', 'studyHoursInput', 'previousMarksInput', 'genderInput', 
                     'extraInput', 'internetInput', 'parentEdInput'];
    
    fields.forEach(id => {
        const el = document.getElementById(id);
        if (el) {
            el.addEventListener('input', updateLivePreview);
            el.addEventListener('change', updateLivePreview);
        }
    });
}

function updateLivePreview() {
    const attendance = parseFloat(document.getElementById('attendanceInput')?.value) || 0;
    const studyHours = parseFloat(document.getElementById('studyHoursInput')?.value) || 0;
    const previousMarks = parseFloat(document.getElementById('previousMarksInput')?.value) || 0;
    
    let estimate = 0;
    let hasInput = false;
    
    if (attendance > 0 || studyHours > 0 || previousMarks > 0) {
        hasInput = true;
        estimate = (attendance * 0.3) + (Math.min(studyHours, 50) * 0.4) + (previousMarks * 0.3);
        estimate = Math.max(0, Math.min(100, Math.round(estimate * 10) / 10));
    }
    
    const scoreEl = document.getElementById('liveScore');
    const labelEl = document.getElementById('liveLabel');
    const badgeEl = document.getElementById('liveRiskBadge');
    
    if (!scoreEl || !labelEl || !badgeEl) return;

    if (hasInput) {
        scoreEl.textContent = estimate + '%';
        
        let label, badgeClass, badgeText;
        if (estimate >= 75) {
            label = 'Good';
            badgeClass = 'badge-success';
            badgeText = 'On Track';
        } else if (estimate >= 50) {
            label = 'Average';
            badgeClass = 'badge-warning';
            badgeText = 'Moderate Risk';
        } else {
            label = 'Needs Work';
            badgeClass = 'badge-danger';
            badgeText = 'At Risk';
        }
        
        labelEl.textContent = label;
        badgeEl.innerHTML = '<span class="badge ' + badgeClass + '">' + badgeText + '</span>';
        
        initLiveGauge(estimate);
    } else {
        scoreEl.textContent = '—';
        labelEl.textContent = 'Enter values';
        badgeEl.innerHTML = '<span class="badge badge-neutral">Awaiting Input</span>';
        initLiveGauge(null);
    }
    
    updateSuggestions(attendance, studyHours, previousMarks);
}

// ─── Smart Suggestions ──────────────────────────────────────────
function updateSuggestions(attendance, studyHours, previousMarks) {
    const container = document.getElementById('suggestionsContainer');
    if (!container) return;
    
    const suggestions = [];
    
    if (attendance > 0 && attendance < 60) {
        suggestions.push({
            type: 'danger',
            icon: 'fas fa-exclamation-circle',
            text: '⚠️ Critical: Your attendance (' + attendance + '%) is very low. Aim for at least 75% to avoid failing.'
        });
    } else if (attendance > 0 && attendance < 75) {
        suggestions.push({
            type: 'warning',
            icon: 'fas fa-exclamation-triangle',
            text: 'Your attendance (' + attendance + '%) is below recommended. Try to maintain at least 80% for better results.'
        });
    } else if (attendance >= 90) {
        suggestions.push({
            type: 'success',
            icon: 'fas fa-check-circle',
            text: 'Great attendance rate! ' + attendance + '% puts you in the top performer category.'
        });
    }
    
    if (studyHours > 0 && studyHours < 10) {
        suggestions.push({
            type: 'warning',
            icon: 'fas fa-clock',
            text: studyHours + 'h/week study time is quite low. Students who study 20+ hours perform significantly better.'
        });
    } else if (studyHours >= 30) {
        suggestions.push({
            type: 'success',
            icon: 'fas fa-fire',
            text: 'Excellent! ' + studyHours + 'h/week shows strong dedication. Keep up the consistency!'
        });
    }
    
    if (previousMarks > 0 && previousMarks < 40) {
        suggestions.push({
            type: 'danger',
            icon: 'fas fa-chart-line',
            text: 'Previous score of ' + previousMarks + '% needs improvement. Consider tutoring or study groups.'
        });
    }
    
    if (suggestions.length === 0) {
        container.style.display = 'none';
        return;
    }
    
    container.style.display = 'block';
    container.innerHTML = suggestions.map(s =>
        '<div class="suggestion-msg suggestion-' + s.type + '">' +
            '<i class="' + s.icon + '"></i>' +
            '<span>' + s.text + '</span>' +
        '</div>'
    ).join('');
}

// ─── Form Submit with Loading ───────────────────────────────────
function initFormSubmit(form, submitBtn) {
    form.addEventListener('submit', function(e) {
        const attendance = parseFloat(form.querySelector('[name="attendance"]')?.value);
        const studyHours = parseFloat(form.querySelector('[name="study_hours"]')?.value);
        const previousMarks = parseFloat(form.querySelector('[name="previous_marks"]')?.value);

        let errors = [];

        if (isNaN(attendance) || attendance < 0 || attendance > 100) {
            errors.push('Attendance must be between 0 and 100');
        }
        if (isNaN(studyHours) || studyHours < 0 || studyHours > 168) {
            errors.push('Weekly study hours must be between 0 and 168');
        }
        if (isNaN(previousMarks) || previousMarks < 0 || previousMarks > 100) {
            errors.push('Previous marks must be between 0 and 100');
        }

        if (errors.length > 0) {
            e.preventDefault();
            alert('Please fix the following:\n\n' + errors.join('\n'));
            return;
        }

        submitBtn.disabled = true;
        submitBtn.classList.add('loading');
        submitBtn.innerHTML = '<i class="fas fa-spinner fa-spin"></i> <span>Analyzing...</span>';
    });
}

// ─── Input Focus Animations ─────────────────────────────────────
function initInputAnimations() {
    const inputs = document.querySelectorAll('.float-label-group .form-input');
    inputs.forEach(input => {
        input.addEventListener('focus', function() {
            this.closest('.form-group')?.classList.add('focused');
            const icon = this.closest('.input-icon-wrap')?.querySelector('i');
            if (icon) icon.style.color = 'var(--primary)';
        });
        input.addEventListener('blur', function() {
            this.closest('.form-group')?.classList.remove('focused');
            const icon = this.closest('.input-icon-wrap')?.querySelector('i');
            if (icon) icon.style.color = '';
        });
    });
}

// ─── Live Gauge Chart (Doughnut) ────────────────────────────────
let liveGaugeChart = null;

function initLiveGauge(value) {
    const canvas = document.getElementById('liveGaugeChart');
    if (!canvas) return;
    
    const ctx = canvas.getContext('2d');
    
    if (liveGaugeChart) {
        liveGaugeChart.destroy();
    }
    
    const displayValue = value !== null ? value : 0;
    const remaining = 100 - displayValue;
    
    let color;
    if (value === null) {
        color = 'rgba(148, 163, 184, 0.3)';
    } else if (displayValue >= 75) {
        color = '#10b981';
    } else if (displayValue >= 50) {
        color = '#f59e0b';
    } else {
        color = '#ef4444';
    }
    
    liveGaugeChart = new Chart(ctx, {
        type: 'doughnut',
        data: {
            datasets: [{
                data: [displayValue, remaining],
                backgroundColor: [color, 'rgba(148, 163, 184, 0.1)'],
                borderWidth: 0,
                borderRadius: displayValue > 0 ? 6 : 0,
            }]
        },
        options: {
            cutout: '78%',
            responsive: false,
            plugins: {
                legend: { display: false },
                tooltip: { enabled: false }
            },
            animation: {
                duration: value !== null ? 600 : 0,
                easing: 'easeOutCubic'
            }
        }
    });
}

// ─── Performance Trend Chart (Line) ─────────────────────────────
function initTrendChart() {
    const canvas = document.getElementById('trendChart');
    if (!canvas) return;
    
    const dataScript = document.getElementById('chartData');
    if (!dataScript) return;
    
    let chartData;
    try {
        chartData = JSON.parse(dataScript.textContent);
    } catch (e) {
        console.error('Failed to parse chart data:', e);
        return;
    }
    
    const predictions = chartData.predictions || [];
    if (predictions.length === 0) return;
    
    const labels = predictions.map(p => p.date);
    const scores = predictions.map(p => p.score);
    const attendances = predictions.map(p => p.attendance);
    
    const ctx = canvas.getContext('2d');
    
    const gradient = ctx.createLinearGradient(0, 0, 0, canvas.height);
    gradient.addColorStop(0, 'rgba(59, 130, 246, 0.15)');
    gradient.addColorStop(1, 'rgba(59, 130, 246, 0)');
    
    new Chart(ctx, {
        type: 'line',
        data: {
            labels: labels,
            datasets: [
                {
                    label: 'Predicted Score',
                    data: scores,
                    borderColor: '#3b82f6',
                    backgroundColor: gradient,
                    borderWidth: 2.5,
                    fill: true,
                    tension: 0.4,
                    pointBackgroundColor: '#3b82f6',
                    pointBorderColor: '#fff',
                    pointBorderWidth: 2,
                    pointRadius: 4,
                    pointHoverRadius: 6,
                },
                {
                    label: 'Attendance',
                    data: attendances,
                    borderColor: '#10b981',
                    borderWidth: 2,
                    fill: false,
                    tension: 0.4,
                    pointBackgroundColor: '#10b981',
                    pointBorderColor: '#fff',
                    pointBorderWidth: 2,
                    pointRadius: 3,
                    pointHoverRadius: 5,
                    borderDash: [5, 5],
                }
            ]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            interaction: {
                intersect: false,
                mode: 'index',
            },
            plugins: {
                legend: {
                    display: true,
                    position: 'bottom',
                    labels: {
                        usePointStyle: true,
                        pointStyle: 'circle',
                        padding: 16,
                        font: { family: "'Inter', sans-serif", size: 11, weight: '600' },
                        color: '#64748b',
                    }
                },
                tooltip: {
                    backgroundColor: '#1e293b',
                    titleFont: { family: "'Inter', sans-serif", weight: '700', size: 12 },
                    bodyFont: { family: "'Inter', sans-serif", size: 11 },
                    padding: 12,
                    cornerRadius: 8,
                    displayColors: true,
                    boxPadding: 4,
                }
            },
            scales: {
                x: {
                    grid: { display: false },
                    ticks: {
                        font: { family: "'Inter', sans-serif", size: 10 },
                        color: '#94a3b8',
                        maxRotation: 0,
                    },
                    border: { display: false }
                },
                y: {
                    min: 0,
                    max: 100,
                    grid: {
                        color: 'rgba(148, 163, 184, 0.1)',
                        drawBorder: false,
                    },
                    ticks: {
                        font: { family: "'Inter', sans-serif", size: 10 },
                        color: '#94a3b8',
                        stepSize: 25,
                        callback: (val) => val + '%',
                    },
                    border: { display: false }
                }
            }
        }
    });
}
