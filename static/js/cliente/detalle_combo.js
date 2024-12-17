document.addEventListener("DOMContentLoaded", function () {
    const btnReservar = document.querySelectorAll(".btn-reservar");
    const comboBox = document.getElementById("combo-box");
    const confirmacionBox = document.getElementById("confirmacion-combo-box");

    btnReservar.forEach(btn => {
        btn.addEventListener("click", () => {
            // Llenar los datos del cliente y combo en el recuadro flotante
            document.getElementById("combo-cliente-nombres").textContent = btn.getAttribute("data-cliente-nombres");
            document.getElementById("combo-cliente-apellidos").textContent = btn.getAttribute("data-cliente-apellidos");
            document.getElementById("combo-cliente-identificacion").textContent = btn.getAttribute("data-cliente-identificacion");
            document.getElementById("combo-cliente-telefono").textContent = btn.getAttribute("data-cliente-telefono");

            // Mostrar el recuadro flotante de información
            comboBox.classList.remove("d-none");
        });
    });

    // Evento para el botón "Siguiente" que muestra el recuadro de confirmación
    document.getElementById("combo-btn-siguiente").addEventListener("click", () => {
        const titulo = document.querySelector(".btn-reservar").getAttribute("data-titulo");
        const precio = document.querySelector(".btn-reservar").getAttribute("data-precio");
        const cantidad = document.getElementById("combo-cantidad-unidades").value;
        const total = (parseFloat(precio) * parseInt(cantidad)).toFixed(2);

        document.getElementById("confirmacion-combo-titulo").textContent = titulo;
        document.getElementById("confirmacion-combo-precio").textContent = precio;
        document.getElementById("confirmacion-combo-cantidad").textContent = cantidad;
        document.getElementById("confirmacion-combo-total").textContent = total;

        comboBox.classList.add("d-none");
        confirmacionBox.classList.remove("d-none");
    });

    // Función para confirmar la reserva
    function confirmarReservaCombo() {
        alert("Reserva del combo confirmada.");
        confirmacionBox.classList.add("d-none");
    }

    // Cerrar el recuadro flotante al hacer clic fuera de él
    window.addEventListener("click", (e) => {
        if (e.target === comboBox) {
            comboBox.classList.add("d-none");
        }
        if (e.target === confirmacionBox) {
            confirmacionBox.classList.add("d-none");
        }
    });
});
