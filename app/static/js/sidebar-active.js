// Highlight active navigation item based on current URL
document.addEventListener('DOMContentLoaded', function () {
    const currentPath = window.location.pathname;
    const navLinks = document.querySelectorAll('.nav-link, .submenu-link');
    
    navLinks.forEach(link => {
        const href = link.getAttribute('href');
        
        // Skip javascript:void(0) links (submenu toggles)
        if (!href || href.startsWith('javascript:')) {
            return;
        }
        
        // Exact match or starts with match for nested pages
        if (href === currentPath || (href !== '/' && currentPath.startsWith(href))) {
            link.classList.add('active');
        }
    });
});

