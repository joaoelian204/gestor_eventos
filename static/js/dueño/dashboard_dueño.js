document.addEventListener('DOMContentLoaded', function () {
    const reporteTipo = document.getElementById('reporteTipo');
    const fechaInicio = document.getElementById('fechaInicio');
    const fechaFin = document.getElementById('fechaFin');
    const generarBtn = document.getElementById('generarReporte');
    const descargarBtn = document.getElementById('descargarReporte');
    const ctx = document.getElementById('reporteGrafico').getContext('2d');
    let reporteChart = null;

    // Función para realizar la solicitud AJAX y obtener el reporte
    function obtenerReporte() {
        const tipo = reporteTipo.value;
        const inicio = fechaInicio.value;
        const fin = fechaFin.value;

        if (!tipo) {
            alert('Por favor, selecciona un tipo de reporte.');
            return;
        }
        if (!inicio || !fin) {
            alert('Por favor, selecciona una fecha de inicio y una fecha de fin.');
            return;
        }

        // URL del endpoint de reportes con el prefijo 'reportes/'
        const url = `/reportes/reporte/${tipo}/?fechaInicio=${inicio}&fechaFin=${fin}`;

        fetch(url)
            .then(response => {
                if (!response.ok) {
                    throw new Error('Error al obtener el reporte.');
                }
                return response.json();
            })
            .then(data => {
                if (data.error) {
                    alert(data.error);
                    return;
                }
                mostrarGrafico(tipo, data.total);
            })
            .catch(error => {
                console.error('Error:', error);
                alert('Hubo un error al obtener el reporte.');
            });
    }

    // Función para mostrar el gráfico con los datos obtenidos
    function mostrarGrafico(tipo, total) {
        const etiquetas = {
            'cliente': 'Clientes',
            'dueño': 'Dueños',
            'administrador': 'Administradores',
            'ventas': 'Ventas',
            'nuevos_clientes': 'Nuevos Clientes'
        };

        // Destruir el gráfico anterior si existe
        if (reporteChart) {
            reporteChart.destroy();
        }

        reporteChart = new Chart(ctx, {
            type: 'bar',
            data: {
                labels: [etiquetas[tipo]],
                datasets: [{
                    label: `Total de ${etiquetas[tipo]}`,
                    data: [total],
                    backgroundColor: 'rgba(54, 162, 235, 0.6)',
                    borderColor: 'rgba(54, 162, 235, 1)',
                    borderWidth: 1
                }]
            },
            options: {
                scales: {
                    y: {
                        beginAtZero: true
                    }
                }
            }
        });
    }

    // Función para descargar el reporte
    function descargarReporte() {
        const tipo = reporteTipo.value;
        const inicio = fechaInicio.value;
        const fin = fechaFin.value;

        if (!tipo) {
            alert('Por favor, selecciona un tipo de reporte.');
            return;
        }
        if (!inicio || !fin) {
            alert('Por favor, selecciona una fecha de inicio y una fecha de fin.');
            return;
        }

        // URL para descargar el reporte con el prefijo 'reportes/'
        const url = `/reportes/reporte/${tipo}/descargar/?fechaInicio=${inicio}&fechaFin=${fin}`;
        window.location.href = url;
    }

    // Event listener para el botón de generar reporte
    generarBtn.addEventListener('click', obtenerReporte);

    // Event listener para el botón de descargar reporte
    descargarBtn.addEventListener('click', descargarReporte);
});
