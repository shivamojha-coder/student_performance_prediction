/**
 * Chart.js Helpers — Reusable chart rendering functions
 * Uses consistent color palette and animations
 */

const COLORS = {
    primary: '#1A73E8',
    primaryLight: '#93C5FD',
    success: '#0D9F6E',
    warning: '#F59E0B',
    danger: '#E53E3E',
    gray: '#CBD5E1',
    grayLight: '#E2E8F0',
    dark: '#1E293B',
    white: '#FFFFFF',
    primaryAlpha: 'rgba(26, 115, 232, 0.15)',
    successAlpha: 'rgba(13, 159, 110, 0.15)',
};

const CHART_DEFAULTS = {
    responsive: true,
    maintainAspectRatio: false,
    plugins: {
        legend: { display: false },
        tooltip: {
            backgroundColor: COLORS.dark,
            titleFont: { family: 'Inter', weight: '600', size: 13 },
            bodyFont: { family: 'Inter', size: 12 },
            padding: 12,
            cornerRadius: 8,
            displayColors: false,
        },
    },
    animation: {
        duration: 800,
        easing: 'easeOutQuart',
    },
};

/**
 * Render a doughnut/pie chart
 */
function renderPieChart(canvasId, data) {
    const ctx = document.getElementById(canvasId);
    if (!ctx) return null;

    const total = (data.good || 0) + (data.average || 0) + (data.poor || 0);
    const passRate = total > 0 ? Math.round(((data.good + data.average) / total) * 100) : 0;

    return new Chart(ctx, {
        type: 'doughnut',
        data: {
            labels: ['Good Performers', 'Average', 'Poor / At Risk'],
            datasets: [{
                data: [data.good || 0, data.average || 0, data.poor || 0],
                backgroundColor: [COLORS.primary, COLORS.primaryLight, COLORS.gray],
                borderWidth: 0,
                borderRadius: 4,
                spacing: 2,
            }]
        },
        options: {
            ...CHART_DEFAULTS,
            cutout: '72%',
            plugins: {
                ...CHART_DEFAULTS.plugins,
                tooltip: {
                    ...CHART_DEFAULTS.plugins.tooltip,
                    callbacks: {
                        label: (ctx) => `${ctx.label}: ${ctx.parsed} students`
                    }
                },
            },
        },
        plugins: [{
            id: 'centerText',
            afterDraw(chart) {
                const { ctx: c, chartArea } = chart;
                const centerX = (chartArea.left + chartArea.right) / 2;
                const centerY = (chartArea.top + chartArea.bottom) / 2;

                c.save();
                c.textAlign = 'center';
                c.textBaseline = 'middle';

                c.font = '800 28px Inter';
                c.fillStyle = COLORS.dark;
                c.fillText(`${passRate}%`, centerX, centerY - 8);

                c.font = '500 11px Inter';
                c.fillStyle = '#94A3B8';
                c.fillText('PASSING', centerX, centerY + 16);
                c.restore();
            }
        }]
    });
}

/**
 * Render a bar chart
 */
function renderBarChart(canvasId, data) {
    const ctx = document.getElementById(canvasId);
    if (!ctx) return null;

    return new Chart(ctx, {
        type: 'bar',
        data: {
            labels: data.labels || ['Week 1', 'Week 2', 'Week 3', 'Week 4', 'Week 5', 'Week 6', 'Week 7'],
            datasets: [
                {
                    label: 'Top Performers',
                    data: data.scores || [65, 72, 68, 78, 82, 75, 80],
                    backgroundColor: COLORS.primary,
                    borderRadius: 6,
                    borderSkipped: false,
                    barPercentage: 0.6,
                },
                {
                    label: 'Below Avg',
                    data: data.belowAvg || [35, 28, 32, 22, 18, 25, 20],
                    backgroundColor: COLORS.grayLight,
                    borderRadius: 6,
                    borderSkipped: false,
                    barPercentage: 0.6,
                }
            ]
        },
        options: {
            ...CHART_DEFAULTS,
            scales: {
                x: {
                    grid: { display: false },
                    ticks: {
                        font: { family: 'Inter', size: 11 },
                        color: '#94A3B8',
                    }
                },
                y: {
                    grid: { color: '#F1F5F9' },
                    ticks: {
                        font: { family: 'Inter', size: 11 },
                        color: '#94A3B8',
                    },
                    beginAtZero: true,
                }
            }
        }
    });
}

/**
 * Render a line chart
 */
function renderLineChart(canvasId, data) {
    const ctx = document.getElementById(canvasId);
    if (!ctx) return null;

    const labels = data.labels || ['SEP', 'OCT', 'NOV', 'DEC', 'JAN', 'FEB', 'MAR', 'APR', 'MAY', 'JUN'];
    const scores = data.scores || [58, 55, 60, 62, 65, 68, 72, 70, 75, 78];

    return new Chart(ctx, {
        type: 'line',
        data: {
            labels: labels,
            datasets: [{
                label: 'Average Score',
                data: scores,
                borderColor: COLORS.primary,
                backgroundColor: COLORS.primaryAlpha,
                borderWidth: 2.5,
                fill: true,
                tension: 0.4,
                pointRadius: 4,
                pointBackgroundColor: COLORS.white,
                pointBorderColor: COLORS.primary,
                pointBorderWidth: 2,
                pointHoverRadius: 6,
                pointHoverBackgroundColor: COLORS.primary,
            }]
        },
        options: {
            ...CHART_DEFAULTS,
            scales: {
                x: {
                    grid: { display: false },
                    ticks: {
                        font: { family: 'Inter', size: 11, weight: '500' },
                        color: '#94A3B8',
                    }
                },
                y: {
                    grid: { color: '#F1F5F9' },
                    ticks: {
                        font: { family: 'Inter', size: 11 },
                        color: '#94A3B8',
                    },
                    min: 40,
                    max: 100,
                }
            },
            interaction: {
                mode: 'index',
                intersect: false,
            }
        }
    });
}

/**
 * Render a radar chart
 */
function renderRadarChart(canvasId, data) {
    const ctx = document.getElementById(canvasId);
    if (!ctx) return null;

    return new Chart(ctx, {
        type: 'radar',
        data: {
            labels: data.labels || ['Attendance', 'Study Hours', 'Previous Marks', 'Assignments', 'Internal'],
            datasets: [
                {
                    label: 'You',
                    data: data.you || [85, 70, 80, 90, 75],
                    backgroundColor: 'rgba(26, 115, 232, 0.2)',
                    borderColor: COLORS.primary,
                    borderWidth: 2,
                    pointRadius: 4,
                    pointBackgroundColor: COLORS.primary,
                },
                {
                    label: 'Class Avg',
                    data: data.classAvg || [75, 60, 65, 70, 65],
                    backgroundColor: 'rgba(203, 213, 225, 0.2)',
                    borderColor: COLORS.gray,
                    borderWidth: 2,
                    pointRadius: 3,
                    pointBackgroundColor: COLORS.gray,
                    borderDash: [5, 5],
                }
            ]
        },
        options: {
            ...CHART_DEFAULTS,
            plugins: {
                ...CHART_DEFAULTS.plugins,
                legend: { display: false },
            },
            scales: {
                r: {
                    beginAtZero: true,
                    max: 100,
                    ticks: {
                        stepSize: 20,
                        font: { size: 10 },
                        backdropColor: 'transparent',
                        color: '#94A3B8',
                    },
                    grid: { color: '#E2E8F0' },
                    pointLabels: {
                        font: { family: 'Inter', size: 11, weight: '600' },
                        color: '#475569',
                    },
                    angleLines: { color: '#E2E8F0' },
                }
            }
        }
    });
}

/**
 * Render a semicircular gauge chart
 */
function renderGauge(canvasId, score) {
    const ctx = document.getElementById(canvasId);
    if (!ctx) return null;

    let color = COLORS.success;
    if (score < 50) color = COLORS.danger;
    else if (score < 75) color = COLORS.warning;

    return new Chart(ctx, {
        type: 'doughnut',
        data: {
            datasets: [{
                data: [score, 100 - score],
                backgroundColor: [color, '#F1F5F9'],
                borderWidth: 0,
                circumference: 270,
                rotation: 225,
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: true,
            cutout: '80%',
            plugins: {
                legend: { display: false },
                tooltip: { enabled: false },
            },
            animation: {
                duration: 1200,
                easing: 'easeOutElastic',
            }
        }
    });
}
