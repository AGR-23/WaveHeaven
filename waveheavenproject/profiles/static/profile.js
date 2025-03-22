const volumeData = {
    labels: JSON.parse('{{ volume_labels|escapejs }}'),
    datasets: [{
        label: 'Recommended Volume (%)',
        data: JSON.parse('{{ volume_data|escapejs }}'),
        borderColor: 'rgba(59, 130, 246, 1)',
        backgroundColor: 'rgba(59, 130, 246, 0.2)',
        fill: true,
        tension: 0.4
    }]
};

const volumeConfig = {
    type: 'line',
    data: volumeData,
    options: {
        scales: {
            y: {
                beginAtZero: true,
                max: 100
            }
        }
    }
};

const volumeChart = new Chart(
    document.getElementById('volumeChart'),
    volumeConfig
);

const hearingData = JSON.parse('{{ hearing_data|escapejs }}');
const ctx = document.getElementById('hearingChart').getContext('2d');

if (hearingData.length > 0) {
    new Chart(ctx, {
        type: 'line',
        data: {
            labels: hearingData.frequency.map(freq => freq + " Hz"),
            datasets: [
                { label: 'Left Ear', data: hearingData.left, borderColor: 'blue' },
                { label: 'Right Ear', data: hearingData.right, borderColor: 'purple' }
            ]
        }
    });
}