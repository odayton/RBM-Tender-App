// Function to show the selected sidebar based on category
function showSidebar(category) {
    // Hide all sidebars
    document.querySelectorAll('.sidebar-content').forEach(function(el) {
        el.style.display = 'none';
    });

    // Show the selected sidebar
    document.getElementById(category + '-sidebar').style.display = 'block';
}

// Show the appropriate sidebar by default
document.addEventListener('DOMContentLoaded', function() {
    var path = window.location.pathname;
    if (path.includes('pumps')) {
        showSidebar('pumps');
    } else if (path.includes('hydronics')) {
        showSidebar('hydronics');
    } else if (path.includes('hydraulic')) {
        showSidebar('hydraulic');
    } else if (path.includes('quotes')) {
        showSidebar('quotes');
    }
});

// Function to toggle the sidebar
document.getElementById('sidebar-toggle').addEventListener('click', function() {
    var sidebar = document.getElementById('sidebar');
    var sidebarToggle = document.getElementById('sidebar-toggle');
    sidebar.classList.toggle('active');
    
    var mainContent = document.querySelector('.main-content');
    if (sidebar.classList.contains('active')) {
        mainContent.classList.add('with-sidebar');
        mainContent.classList.remove('no-sidebar');
        sidebarToggle.style.left = '260px';
    } else {
        mainContent.classList.add('no-sidebar');
        mainContent.classList.remove('with-sidebar');
        sidebarToggle.style.left = '10px';
    }
});

// Prevent sidebar from closing when a link is clicked
document.querySelectorAll('.sidebar .nav-link').forEach(function(link) {
    link.addEventListener('click', function(event) {
        event.stopPropagation();
    });
});
