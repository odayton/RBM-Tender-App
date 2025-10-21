// Wait for the DOM to be fully loaded before running the script
document.addEventListener('DOMContentLoaded', function () {
    
    // Find the toggle button and sidebar
    const sidebarToggle = document.getElementById('sidebar-toggle');
    const sidebar = document.getElementById('sidebar');
    const body = document.body;

    // Check if we're on mobile
    const isMobile = () => window.innerWidth <= 768;

    // Load saved sidebar state
    function loadSidebarState() {
        const savedState = localStorage.getItem('sidebar-collapsed');
        const isMobileDevice = isMobile();
        
        if (savedState !== null && !isMobileDevice) {
            // Only apply saved state on desktop
            if (savedState === 'true') {
                body.classList.add('sidebar-collapsed');
            } else {
                body.classList.remove('sidebar-collapsed');
            }
        }
    }

    // Save sidebar state
    function saveSidebarState() {
        if (!isMobile()) {
            const isCollapsed = body.classList.contains('sidebar-collapsed');
            localStorage.setItem('sidebar-collapsed', isCollapsed.toString());
        }
    }

    // Load the saved state on page load
    loadSidebarState();

    // Make sure elements exist before adding an event listener
    if (sidebarToggle && sidebar) {
        sidebarToggle.addEventListener('click', function () {
            if (isMobile()) {
                // On mobile: toggle overlay (sidebar-open on body)
                body.classList.toggle('sidebar-open');
            } else {
                // On desktop: toggle collapsed state (sidebar-collapsed on body)
                body.classList.toggle('sidebar-collapsed');
                // Save the new state
                saveSidebarState();
            }
        });
    }

    // Close mobile sidebar when clicking outside
    if (isMobile()) {
        body.addEventListener('click', function(e) {
            if (body.classList.contains('sidebar-open') && 
                !sidebar.contains(e.target) && 
                !sidebarToggle.contains(e.target)) {
                body.classList.remove('sidebar-open');
            }
        });
    }

    // Handle window resize - clean up classes when switching between mobile/desktop
    let wasMobile = isMobile();
    window.addEventListener('resize', function() {
        const isNowMobile = isMobile();
        
        if (wasMobile !== isNowMobile) {
            // Clear both classes when switching between mobile and desktop
            body.classList.remove('sidebar-open', 'sidebar-collapsed');
            
            // Load the saved desktop state when switching to desktop
            if (!isNowMobile) {
                loadSidebarState();
            }
            
            wasMobile = isNowMobile;
        }
    });

});