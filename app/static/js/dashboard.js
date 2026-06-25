document.addEventListener("DOMContentLoaded", function () {
    const canvasTipos = document.getElementById("chartTipos");
    const canvasEstados = document.getElementById("chartEstados");
    const canvasTransacciones = document.getElementById("chartTransacciones");
    const canvasAgentes = document.getElementById("chartAgentes");
    const canvasVisitas = document.getElementById("chartVisitas");

    // Solo ejecutar si estamos en la página del dashboard
    if (!canvasTipos && !canvasEstados && !canvasTransacciones) return;

    // Configuración global de Chart.js
    Chart.defaults.font.family = "'Inter', sans-serif";
    Chart.defaults.font.size = 11;
    Chart.defaults.color = "#7f8c8d";

    var palette = {
        brand: '#1a3a5c',
        accent: '#d4953a',
        success: '#2d8659',
        danger: '#c0392b',
        warning: '#d4a017',
        info: '#2980b9',
        muted: '#95a5a6'
    };

    fetch("/dashboard/api/metrics")
        .then(function (response) {
            if (!response.ok) throw new Error("Error al obtener métricas.");
            return response.json();
        })
        .then(function (data) {
            // 1. Distribución por Tipo (Dona)
            if (canvasTipos) {
                var tiposLabels = Object.keys(data.tipos);
                var tiposValues = Object.values(data.tipos);

                new Chart(canvasTipos, {
                    type: 'doughnut',
                    data: {
                        labels: tiposLabels,
                        datasets: [{
                            data: tiposValues,
                            backgroundColor: [palette.brand, palette.accent, palette.info, palette.success, palette.muted],
                            borderWidth: 2,
                            borderColor: '#ffffff'
                        }]
                    },
                    options: {
                        responsive: true,
                        maintainAspectRatio: false,
                        cutout: '60%',
                        plugins: {
                            legend: {
                                position: 'bottom',
                                labels: { padding: 12, usePointStyle: true, pointStyleWidth: 8 }
                            }
                        }
                    }
                });
            }

            // 2. Inmuebles por Estado (Barra Horizontal)
            if (canvasEstados) {
                var estadosLabels = Object.keys(data.estados);
                var estadosValues = Object.values(data.estados);
                var estadoColores = estadosLabels.map(function (label) {
                    if (label === 'Disponible') return palette.success;
                    if (label === 'Vendida') return palette.danger;
                    if (label === 'Alquilada') return palette.warning;
                    if (label === 'Reservada') return palette.info;
                    return palette.muted;
                });

                new Chart(canvasEstados, {
                    type: 'bar',
                    data: {
                        labels: estadosLabels,
                        datasets: [{
                            data: estadosValues,
                            backgroundColor: estadoColores,
                            borderRadius: 4
                        }]
                    },
                    options: {
                        responsive: true,
                        maintainAspectRatio: false,
                        indexAxis: 'y',
                        plugins: { legend: { display: false } },
                        scales: {
                            x: { beginAtZero: true, ticks: { stepSize: 1 }, grid: { display: false } },
                            y: { grid: { display: false } }
                        }
                    }
                });
            }

            // 3. Ingresos por Contrato (Barra Vertical)
            if (canvasTransacciones) {
                var transLabels = Object.keys(data.transacciones);
                var transValues = Object.values(data.transacciones);

                new Chart(canvasTransacciones, {
                    type: 'bar',
                    data: {
                        labels: transLabels,
                        datasets: [{
                            label: 'Total (Bs.)',
                            data: transValues,
                            backgroundColor: [palette.success, palette.accent],
                            borderRadius: 4
                        }]
                    },
                    options: {
                        responsive: true,
                        maintainAspectRatio: false,
                        plugins: { legend: { display: false } },
                        scales: {
                            x: { grid: { display: false } },
                            y: { beginAtZero: true, grid: { color: '#f1f3f5' } }
                        }
                    }
                });
            }

            // 4. Propiedades por Agente (Barra Horizontal)
            if (canvasAgentes && data.agentes) {
                var agLabels = Object.keys(data.agentes);
                var agValues = Object.values(data.agentes);

                new Chart(canvasAgentes, {
                    type: 'bar',
                    data: {
                        labels: agLabels,
                        datasets: [{
                            label: 'Propiedades asignadas',
                            data: agValues,
                            backgroundColor: palette.brand,
                            borderRadius: 4
                        }]
                    },
                    options: {
                        responsive: true,
                        maintainAspectRatio: false,
                        indexAxis: 'y',
                        plugins: { legend: { display: false } },
                        scales: {
                            x: { beginAtZero: true, ticks: { stepSize: 1 }, grid: { display: false } },
                            y: { grid: { display: false } }
                        }
                    }
                });
            }

            // 5. Visitas por Estado (Dona)
            if (canvasVisitas && data.visitas_estado) {
                var vLabels = Object.keys(data.visitas_estado);
                var vValues = Object.values(data.visitas_estado);
                var vColores = vLabels.map(function (label) {
                    if (label === 'Programada') return palette.info;
                    if (label === 'Realizada') return palette.success;
                    if (label === 'Cancelada') return palette.danger;
                    return palette.muted;
                });

                new Chart(canvasVisitas, {
                    type: 'doughnut',
                    data: {
                        labels: vLabels,
                        datasets: [{
                            data: vValues,
                            backgroundColor: vColores,
                            borderWidth: 2,
                            borderColor: '#ffffff'
                        }]
                    },
                    options: {
                        responsive: true,
                        maintainAspectRatio: false,
                        cutout: '60%',
                        plugins: {
                            legend: {
                                position: 'bottom',
                                labels: { padding: 12, usePointStyle: true, pointStyleWidth: 8 }
                            }
                        }
                    }
                });
            }
        })
        .catch(function (error) {
            console.error("Error al cargar gráficos:", error);
        });
});
