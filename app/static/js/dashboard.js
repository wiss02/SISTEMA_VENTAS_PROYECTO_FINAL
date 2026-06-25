document.addEventListener("DOMContentLoaded", function () {
    const canvasTipos = document.getElementById("chartTipos");
    const canvasEstados = document.getElementById("chartEstados");
    const canvasTransacciones = document.getElementById("chartTransacciones");

    if (!canvasTipos || !canvasEstados || !canvasTransacciones) return;

    fetch("/dashboard/api/metrics")
        .then(response => {
            if (!response.ok) {
                throw new Error("Error al obtener las métricas del servidor.");
            }
            return response.json();
        })
        .then(data => {
            // 1. Gráfico de Distribución de Tipos de Propiedad (Dona)
            const tiposLabels = Object.keys(data.tipos);
            const tiposValues = Object.values(data.tipos);
            
            new Chart(canvasTipos, {
                type: 'doughnut',
                data: {
                    labels: tiposLabels,
                    datasets: [{
                        data: tiposValues,
                        backgroundColor: [
                            '#1e3c72',
                            '#00b4d8',
                            '#f59e0b',
                            '#10b981',
                            '#8b5cf6'
                        ],
                        borderWidth: 2,
                        borderColor: '#ffffff'
                    }]
                },
                options: {
                    responsive: true,
                    maintainAspectRatio: false,
                    plugins: {
                        legend: {
                            position: 'bottom',
                            labels: {
                                font: {
                                    family: 'Inter',
                                    size: 11
                                }
                            }
                        }
                    }
                }
            });

            // 2. Gráfico de Propiedades por Estado (Barra Horizontal)
            const estadosLabels = Object.keys(data.estados);
            const estadosValues = Object.values(data.estados);
            
            new Chart(canvasEstados, {
                type: 'bar',
                data: {
                    labels: estadosLabels,
                    datasets: [{
                        label: 'Cantidad de Inmuebles',
                        data: estadosValues,
                        backgroundColor: function(context) {
                            const label = context.chart.data.labels[context.dataIndex];
                            if (label === 'Disponible') return '#10b981';
                            if (label === 'Vendida') return '#ef4444';
                            if (label === 'Alquilada') return '#f59e0b';
                            if (label === 'Reservada') return '#3b82f6';
                            return '#64748b';
                        },
                        borderRadius: 6
                    }]
                },
                options: {
                    responsive: true,
                    maintainAspectRatio: false,
                    indexAxis: 'y',
                    plugins: {
                        legend: {
                            display: false
                        }
                    },
                    scales: {
                        x: {
                            beginAtZero: true,
                            ticks: {
                                stepSize: 1
                            },
                            grid: {
                                display: false
                            }
                        },
                        y: {
                            grid: {
                                display: false
                            }
                        }
                    }
                }
            });

            // 3. Gráfico de Ingresos por Contrato (Barra Vertical)
            const transLabels = Object.keys(data.transacciones);
            const transValues = Object.values(data.transacciones);
            
            new Chart(canvasTransacciones, {
                type: 'bar',
                data: {
                    labels: transLabels,
                    datasets: [{
                        label: 'Total Acumulado (Bs.)',
                        data: transValues,
                        backgroundColor: '#3b82f6',
                        borderColor: '#2563eb',
                        borderWidth: 1,
                        borderRadius: 6
                    }]
                },
                options: {
                    responsive: true,
                    maintainAspectRatio: false,
                    plugins: {
                        legend: {
                            display: false
                        }
                    },
                    scales: {
                        x: {
                            grid: {
                                display: false
                            }
                        },
                        y: {
                            beginAtZero: true,
                            grid: {
                                color: '#f1f5f9'
                            }
                        }
                    }
                }
            });
        })
        .catch(error => {
            console.error("Error al cargar los gráficos del dashboard:", error);
        });
});
