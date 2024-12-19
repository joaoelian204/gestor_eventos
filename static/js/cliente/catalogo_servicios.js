 // Variables globales para almacenar datos del cliente y del evento
    let clienteId, eventoId, clienteCorreo;

    // Obtener elementos del DOM
    const btnReservar = document.querySelectorAll('.btn-reservar');
    const clienteBox = document.getElementById('cliente-box');
    const confirmacionBox = document.getElementById('confirmacion-box');
    const overlay = document.getElementById('overlay');
    const btnSiguiente = document.getElementById('btn-siguiente');
    const btnConfirmar = document.getElementById('btn-confirmar');

    // Función para mostrar el formulario de información del cliente
    btnReservar.forEach(btn => {
        btn.addEventListener('click', (event) => {
            event.preventDefault();

            clienteId = btn.dataset.clienteId;
            eventoId = btn.dataset.eventoId;
            clienteCorreo = btn.dataset.clienteCorreo;

            console.log('Cliente ID:', clienteId);
            console.log('Evento ID:', eventoId);
            console.log('Cliente Correo:', clienteCorreo);

            if (!clienteId || !eventoId || !clienteCorreo) {
                alert('Error: Faltan datos del cliente o del evento.');
                return;
            }

            document.getElementById('cliente-nombres').textContent = btn.dataset.clienteNombres || 'N/A';
            document.getElementById('cliente-apellidos').textContent = btn.dataset.clienteApellidos || 'N/A';
            document.getElementById('cliente-identificacion').textContent = btn.dataset.clienteIdentificacion || 'N/A';
            document.getElementById('cliente-telefono').textContent = btn.dataset.clienteTelefono || 'N/A';
            document.getElementById('reserva-titulo').textContent = btn.dataset.titulo || 'N/A';
            document.getElementById('reserva-precio').textContent = btn.dataset.precio || '0';

            clienteBox.classList.remove('d-none');
            overlay.classList.remove('d-none');
        });
    });

    // Función para validar y mostrar el recuadro de confirmación
    btnSiguiente.addEventListener('click', (event) => {
        event.preventDefault();

        const direccion = document.getElementById('direccion').value.trim();
        const fechaReserva = document.getElementById('fecha-reserva').value.trim();
        const fechaFinReserva = document.getElementById('fecha-fin-reserva').value.trim();
        const cantidad = document.getElementById('cantidad-unidades').value.trim();
        let precio = document.getElementById('reserva-precio').textContent.trim();

        if (!direccion || !fechaReserva || !fechaFinReserva || !cantidad || cantidad <= 0) {
            alert('Por favor, complete todos los campos obligatorios.');
            return;
        }

        precio = parseFloat(precio.replace(',', '.'));

        if (isNaN(precio)) {
            alert('Error: Precio inválido.');
            return;
        }

        const total = cantidad * precio;
        document.getElementById('reserva-cantidad').textContent = cantidad;
        document.getElementById('reserva-total').textContent = total.toFixed(2);

        clienteBox.classList.add('d-none');
        confirmacionBox.classList.remove('d-none');
    });

    // Función para enviar los datos al servidor
    btnConfirmar.addEventListener('click', () => {
        const direccion = document.getElementById('direccion').value.trim();
        const fechaReserva = document.getElementById('fecha-reserva').value.trim();
        const fechaFinReserva = document.getElementById('fecha-fin-reserva').value.trim();
        const cantidad = document.getElementById('cantidad-unidades').value.trim();
        const precio = document.getElementById('reserva-precio').textContent.trim();

        // Desactivar el botón para evitar múltiples clics
        btnConfirmar.disabled = true;

        if (!direccion || !fechaReserva || !fechaFinReserva || !cantidad || cantidad <= 0) {
            alert('Por favor, complete todos los campos obligatorios.');
            btnConfirmar.disabled = false;
            return;
        }

        const formData = new FormData();
        formData.append('cliente_id', clienteId);
        formData.append('evento_id', eventoId);
        formData.append('direccion', direccion);
        formData.append('fecha_hora_reserva', fechaReserva);
        formData.append('fecha_fin_reserva', fechaFinReserva);
        formData.append('cantidad_unidades', cantidad);
        formData.append('precio_por_unidad', precio);

        const csrftoken = document.querySelector('[name=csrfmiddlewaretoken]').value;

        fetch('/reservas/crear_alquiler/', {
            method: 'POST',
            headers: {
                'X-CSRFToken': csrftoken
            },
            body: formData
        })
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                alert(data.message);
                cerrarFloatingBox();
                window.location.reload();
            } else {
                alert(`Error: ${data.message}`);
            }
        })
        .catch(error => {
            console.error('Error al enviar la reserva:', error);
            alert('Hubo un error al enviar la solicitud. Por favor, inténtalo de nuevo.');
        })
        .finally(() => {
            // Rehabilitar el botón después de completar la solicitud
            btnConfirmar.disabled = false;
        });
    });

    // Función para cerrar los formularios flotantes al hacer clic en el overlay
    overlay.addEventListener('click', () => {
        clienteBox.classList.add('d-none');
        confirmacionBox.classList.add('d-none');
        overlay.classList.add('d-none');
    });

