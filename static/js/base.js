document.addEventListener('DOMContentLoaded', () => {
  
    // Referencias globales de elementos dentro del ámbito DOMContentLoaded
    const $navbarBurgers = Array.prototype.slice.call(document.querySelectorAll('.navbar-burger'), 0);
    const $navbarMenu = document.getElementById('navbarBasicExample');
    const navbarContainer = document.getElementById('app-navbar');
    const themeToggle = document.getElementById('theme-toggle'); // Definido aquí para el punto 3

    // 1. Funcionalidad de notificaciones
    (document.querySelectorAll('.notification .delete') || []).forEach(($delete) => {
        const $notification = $delete.parentNode;
        $delete.addEventListener('click', () => {
            $notification.parentNode.removeChild($notification);
        });
    });

    // 2. Funcionalidad del Menú Hamburguesa (Bulma) Y Colapso al Clic Exterior
    
    function toggleNavbar() {
        const burger = $navbarBurgers[0];
        burger.classList.toggle('is-active');
        $navbarMenu.classList.toggle('is-active');
    }

    if ($navbarBurgers.length > 0) {
        $navbarBurgers.forEach(el => {
            el.addEventListener('click', toggleNavbar);
        });
    }
    
    document.addEventListener('click', (event) => {
        // Solo ejecutar si el menú responsive está abierto
        if ($navbarMenu.classList.contains('is-active')) {
            
            // Si el clic NO fue dentro del contenedor del navbar (toda el área de la barra)
            if (!navbarContainer.contains(event.target)) {
                toggleNavbar();
            }
        }
    });

    
    // 3. Funcionalidad de Cambio de Tema (Toggle - 3 temas)
    const body = document.body;
    const THEME_KEY = 'appTheme';
    const themes = ['light', 'dark', 'sepia'];
    
    function applyTheme(theme) {
        body.classList.remove('is-theme-light', 'is-theme-dark', 'is-theme-sepia');
        body.classList.add('is-theme-' + theme);
        localStorage.setItem(THEME_KEY, theme);
        updateToggleText(theme);
    }

    function updateToggleText(currentTheme) {
        let iconClass = 'fas fa-palette';
        let text = '';
        
        if (currentTheme === 'dark') {
            iconClass = 'fas fa-sun';
            // text = 'Tema Claro';
        } else if (currentTheme === 'sepia') {
            iconClass = 'fas fa-moon';
            // text = 'Tema Oscuro';
        }
        
        themeToggle.innerHTML = `<span class="icon"><i class="${iconClass}"></i></span><span>${text}</span>`;
    }

    let currentTheme = localStorage.getItem(THEME_KEY) || 'light';
    applyTheme(currentTheme);
    
    // 🎯 CORRECCIÓN APLICADA AQUÍ: Detener la propagación del evento
    themeToggle.addEventListener('click', (event) => {
        // Previene que el evento de clic llegue al listener del documento,
        // eliminando cualquier posible conflicto de doble manejo o cierre accidental.
        event.stopPropagation(); 
        
        const currentIndex = themes.indexOf(currentTheme);
        const nextIndex = (currentIndex + 1) % themes.length;
        const nextTheme = themes[nextIndex];
        
        currentTheme = nextTheme;
        applyTheme(currentTheme);
    });
    
});