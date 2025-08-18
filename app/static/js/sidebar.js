// Wait for the DOM to be fully loaded before running the script
document.addEventListener('DOMContentLoaded', function () {
    
    // Find the toggle button and the main page wrapper element
    const sidebarToggle = document.getElementById('sidebar-toggle');
    const pageWrapper = document.querySelector('.page-wrapper');

    // Make sure both elements exist before adding an event listener
    if (sidebarToggle && pageWrapper) {
        sidebarToggle.addEventListener('click', function () {
            // Toggle the 'sidebar-collapsed' class on the page wrapper
            pageWrapper.classList.toggle('sidebar-collapsed');
        });
    }

});