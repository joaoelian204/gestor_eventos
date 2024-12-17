/* ============================
    Script para Cerrar Menús Desplegables
   ============================ */

    document.addEventListener('DOMContentLoaded', function () {
    var dropdownItems = document.querySelectorAll('.dropdown-item');
    dropdownItems.forEach(function (item) {
        item.addEventListener('click', function () {
            var dropdownToggle = document.querySelector('.dropdown-toggle.show');
            if (dropdownToggle) {
                dropdownToggle.click();
            }
        });
    });
});
