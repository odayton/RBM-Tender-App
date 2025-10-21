// Handle submenu toggles in sidebar with smooth animations
document.addEventListener('DOMContentLoaded', function () {
    const submenuToggles = document.querySelectorAll('.submenu-toggle');
    
    submenuToggles.forEach(toggle => {
        toggle.addEventListener('click', function(e) {
            e.preventDefault();
            
            const submenuId = this.getAttribute('data-submenu');
            const submenu = document.getElementById('submenu-' + submenuId);
            const chevron = this.querySelector('.fa-chevron-down');
            
            if (submenu) {
                // Toggle submenu with smooth animation
                submenu.classList.toggle('hidden');
                
                // Rotate chevron with smooth animation
                if (chevron) {
                    if (submenu.classList.contains('hidden')) {
                        chevron.style.transform = 'rotate(0deg)';
                    } else {
                        chevron.style.transform = 'rotate(180deg)';
                    }
                }
            }
        });
    });
    
    // Auto-expand submenu if current page is in it - DISABLED
    // All submenus will be hidden by default
    /*
    const currentPath = window.location.pathname;
    document.querySelectorAll('.submenu').forEach(submenu => {
        const links = submenu.querySelectorAll('a');
        let shouldExpand = false;
        
        links.forEach(link => {
            const href = link.getAttribute('href');
            if (href && (href === currentPath || currentPath.startsWith(href))) {
                shouldExpand = true;
            }
        });
        
        if (shouldExpand) {
            // Show the submenu
            submenu.classList.remove('hidden');
            
            // Rotate the chevron
            const submenuId = submenu.id.replace('submenu-', '');
            const toggle = document.querySelector(`[data-submenu="${submenuId}"]`);
            if (toggle) {
                const chevron = toggle.querySelector('.fa-chevron-down');
                if (chevron) {
                    chevron.style.transform = 'rotate(180deg)';
                }
            }
        }
    });
    */
});

