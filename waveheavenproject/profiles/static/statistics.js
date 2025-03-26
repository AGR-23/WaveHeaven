// Obtener los datos desde el script generado por Django
const volumeData = {
    labels: JSON.parse(document.getElementById('volumeLabels').textContent),  // Eje X: Tiempo
    datasets: [{
        label: 'Volume (%)',  // Etiqueta del conjunto de datos
        data: JSON.parse(document.getElementById('volumeData').textContent),  // Eje Y: Volumen
        borderColor: 'rgba(59, 130, 246, 1)',  // Color de la línea
        backgroundColor: 'rgba(59, 130, 246, 0.2)',  // Color de relleno
        fill: true,  // Rellenar el área bajo la línea
        tension: 0.4  // Suavizar la línea
    }]
};

// Configuración del gráfico
const volumeConfig = {
    type: 'line',
    data: volumeData,
    options: {
        scales: {
            x: {
                title: {
                    display: true,
                    text: 'Time',  // Etiqueta del eje X
                    font: {
                        size: 14,
                        weight: 'bold'
                    }
                },
                ticks: {
                    font: {
                        size: 12
                    }
                }
            },
            y: {
                title: {
                    display: true,
                    text: 'Volume (%)',  // Etiqueta del eje Y
                    font: {
                        size: 14,
                        weight: 'bold'
                    }
                },
                beginAtZero: true,
                max: 100,
                ticks: {
                    font: {
                        size: 12
                    }
                }
            }
        },
        plugins: {
            tooltip: {
                enabled: true,  // Habilitar tooltips
                mode: 'index',
                intersect: false
            },
            legend: {
                display: true,  // Mostrar la leyenda
                position: 'top'
            }
        },
        responsive: true,
        maintainAspectRatio: true
    }
};

// Renderizar el gráfico
const volumeChart = new Chart(
    document.getElementById('volumeChart'),
    volumeConfig
);