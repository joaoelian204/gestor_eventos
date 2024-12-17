// Confirma antes de eliminar un elemento
document.addEventListener('DOMContentLoaded', () => {
    const deleteButtons = document.querySelectorAll('.btn-danger');

    deleteButtons.forEach(button => {
        button.addEventListener('click', function (event) {
            const confirmDelete = confirm("¿Estás seguro de que deseas eliminar este elemento?");
            if (!confirmDelete) {
                event.preventDefault();
            }
        });
    });
});

// Ejemplo de interacción adicional
console.log("Scripts cargados correctamente.");
