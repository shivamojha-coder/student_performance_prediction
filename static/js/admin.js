/**
 * Admin Dashboard — Dynamic chart updates and interactions
 */

// Store chart instances for update
let pieChartInstance = null;
let barChartInstance = null;
let lineChartInstance = null;

/**
 * Fetch data from /api/class-stats and re-render dashboard
 */
function fetchAndRenderDashboard(className) {
    fetch(`/api/class-stats?class=${encodeURIComponent(className)}`)
        .then(res => res.json())
        .then(data => {
            // Update pie chart
            if (pieChartInstance) {
                pieChartInstance.destroy();
            }
            pieChartInstance = renderPieChart('pieChart', data.distribution);

            // Update legend counts
            const legendGood = document.getElementById('legendGood');
            const legendAvg = document.getElementById('legendAvg');
            const legendPoor = document.getElementById('legendPoor');
            if (legendGood) legendGood.textContent = data.distribution.good;
            if (legendAvg) legendAvg.textContent = data.distribution.average;
            if (legendPoor) legendPoor.textContent = data.distribution.poor;

            // Update bar chart
            if (barChartInstance) barChartInstance.destroy();
            if (data.class_comparison && data.class_comparison.labels.length > 0) {
                barChartInstance = renderBarChart('barChart', {
                    labels: data.class_comparison.labels.map(l => l.length > 12 ? l.substring(0, 12) + '...' : l),
                    scores: data.class_comparison.scores,
                    belowAvg: data.class_comparison.scores.map(s => Math.max(0, 100 - s)),
                });
            } else {
                barChartInstance = renderBarChart('barChart', {});
            }

            // Update line chart
            if (lineChartInstance) lineChartInstance.destroy();
            if (data.monthly_trend && data.monthly_trend.labels.length > 0) {
                lineChartInstance = renderLineChart('lineChart', {
                    labels: data.monthly_trend.labels,
                    scores: data.monthly_trend.scores,
                });
            } else {
                lineChartInstance = renderLineChart('lineChart', {});
            }
        })
        .catch(err => {
            console.error('Failed to fetch class stats:', err);
            // Render with defaults
            if (!pieChartInstance) pieChartInstance = renderPieChart('pieChart', { good: 0, average: 0, poor: 0 });
            if (!barChartInstance) barChartInstance = renderBarChart('barChart', {});
            if (!lineChartInstance) lineChartInstance = renderLineChart('lineChart', {});
        });
}

/**
 * Handle class dropdown change
 */
function updateDashboard(className) {
    // Update URL without reload
    const url = new URL(window.location);
    url.searchParams.set('class', className);
    window.history.replaceState({}, '', url);

    fetchAndRenderDashboard(className);
}

/**
 * Student directory search (client-side filter)
 */
function filterStudents(searchTerm) {
    const rows = document.querySelectorAll('.data-table tbody tr');
    const term = searchTerm.toLowerCase();

    rows.forEach(row => {
        const text = row.textContent.toLowerCase();
        row.style.display = text.includes(term) ? '' : 'none';
    });
}
