/* ============================
    Generación Dinámica de la Imagen de Perfil
   ============================ */

document.addEventListener("DOMContentLoaded", function () {
    // Obtener el contenedor de la imagen de perfil
    const profileImageContainer = document.getElementById("profileImageContainer");

    // Obtener nombres y apellidos desde los atributos data
    const nombres = profileImageContainer.dataset.nombres.trim();
    const apellidos = profileImageContainer.dataset.apellidos.trim();

    // Función para extraer las iniciales del primer nombre y primer apellido
    function getInitials(nombres, apellidos) {
        let primerNombre = nombres.split(/\s+/)[0] || '';
        let primerApellido = apellidos.split(/\s+/)[0] || '';
        return `${primerNombre.charAt(0).toUpperCase()}${primerApellido.charAt(0).toUpperCase()}`;
    }

    // Función para generar un color único basado en el nombre completo
    function stringToColor(str) {
        let hash = 0;
        for (let i = 0; i < str.length; i++) {
            hash = str.charCodeAt(i) + ((hash << 5) - hash);
        }
        let color = '#';
        for (let i = 0; i < 3; i++) {
            const value = (hash >> (i * 8)) & 0xff;
            color += ('00' + value.toString(16)).slice(-2);
        }
        return color;
    }

    // Función para asignar las iniciales y el color al contenedor
    function setProfileImage() {
        const initials = getInitials(nombres, apellidos);
        const color = stringToColor(`${nombres} ${apellidos}`);

        // Asignar las iniciales y el color al contenedor
        profileImageContainer.textContent = initials;
        profileImageContainer.style.backgroundColor = color;
        profileImageContainer.style.color = "#fff";
        profileImageContainer.style.display = "flex";
        profileImageContainer.style.alignItems = "center";
        profileImageContainer.style.justifyContent = "center";
        profileImageContainer.style.fontSize = "3rem";
        profileImageContainer.style.fontWeight = "bold";
        profileImageContainer.style.borderRadius = "50%";
        profileImageContainer.style.width = "150px";
        profileImageContainer.style.height = "150px";
    }

    // Llamar a la función para establecer la imagen de perfil
    setProfileImage();
});

