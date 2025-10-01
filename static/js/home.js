document.addEventListener('DOMContentLoaded', () => {
    // --- Lógica para ocultar el botón 'Volver Atrás' en la vista Home ---
    const backButton = document.querySelector('.back-button-float');
    if (backButton) {
        // Oculta el botón de 'Volver atrás' cuando estamos en la vista home
        // Usamos un estilo in-line para sobrescribir cualquier propiedad 'important' del CSS
        backButton.setAttribute('style', 'display: none !important;');
    }
    // -----------------------------------------------------------

    // Seleccionamos solo las pestañas que tienen data-tab-target ('Instituciones y Empresas')
    const tabs = document.querySelectorAll('.tabs li[data-tab-target]');
    const tabContentBoxes = document.querySelectorAll('.tab-content');

    tabs.forEach(tab => {
        tab.addEventListener('click', () => {
            // 1. Desactivar TODAS las pestañas y ocultar todos los contenidos de tabs
            document.querySelectorAll('.tabs li').forEach(item => item.classList.remove('is-active'));
            tabContentBoxes.forEach(box => box.classList.remove('is-active'));

            // 2. Activar la pestaña clickeada
            tab.classList.add('is-active');

            // 3. Mostrar el contenido objetivo
            const target = document.querySelector(tab.dataset.tabTarget);
            if (target) {
                target.classList.add('is-active');
            }
        });
    });

});